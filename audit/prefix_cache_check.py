#!/usr/bin/env python3
"""Prefix-cache cross-tenant isolation check.

A DEFENSIVE security test, for the OWNER of a multi-tenant AI system. It detects whether an
OpenAI-compatible LLM endpoint shares its prefix / KV cache ACROSS tenant boundaries , a known
vulnerability (NDSS 2025) where one tenant can infer another tenant's prompts from response timing.

Method (timing side-channel, prefill-isolated):
  1. Build a long, unique "secret" prefix (stands in for tenant A's confidential prompt).
  2. As TENANT A, send it once to warm any shared cache.
  3. As TENANT B (a different credential / tenant context), send the SAME prefix N times and time it.
     max_tokens=1 + temperature=0 so the latency is dominated by PREFILL (the part caching skips).
  4. As TENANT B, send a DIFFERENT, never-seen prefix N times as a CONTROL.
  5. If tenant B's latency on tenant A's prefix is meaningfully LOWER than the control, the prefix
     cache is shared across tenants => cross-tenant leak risk => FAIL.

A sanity pass first confirms the endpoint caches at all (tenant A repeating its own prefix), so a
PASS is interpretable ("caching is on, but it is correctly per-tenant" vs "no caching observed").

Usage:
  python prefix_cache_check.py \
      --base-url http://localhost:4000/v1 \
      --tenant-a-key sk-tenantA --tenant-b-key sk-tenantB \
      --model your-model [--trials 7] [--prefix-tokens 1500]

Only run this against systems you own or are explicitly authorized to test.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import uuid
import urllib.request
import urllib.error


def _post(base_url: str, api_key: str, model: str, prompt: str, timeout: float = 60.0) -> float:
    """Send one chat completion (max_tokens=1) and return wall-clock latency in seconds."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
    return time.perf_counter() - t0


def _prefix(n_tokens: int) -> str:
    """A long, unique block ~n_tokens words long, so prefill time is measurable and the content is
    unique per run (a real never-before-seen 'secret')."""
    tag = uuid.uuid4().hex
    sentence = (f"Confidential matter {tag}: the following privileged record must remain isolated "
                f"to a single tenant and never appear in another tenant's context. ")
    reps = max(1, n_tokens // len(sentence.split()))
    return (sentence * reps) + "\n\nSummarize in one word:"


def _median_latency(base_url, key, model, prompt, trials):
    lat = []
    for _ in range(trials):
        try:
            lat.append(_post(base_url, key, model, prompt))
        except urllib.error.HTTPError as e:
            sys.exit(f"HTTP {e.code} from endpoint: {e.read().decode()[:200]}")
        except Exception as e:
            sys.exit(f"Request failed: {e}")
    return statistics.median(lat), lat


def main():
    ap = argparse.ArgumentParser(description="Cross-tenant prefix-cache isolation check")
    ap.add_argument("--base-url", required=True, help="OpenAI-compatible base, e.g. http://host:4000/v1")
    ap.add_argument("--tenant-a-key", required=True)
    ap.add_argument("--tenant-b-key", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--trials", type=int, default=7)
    ap.add_argument("--prefix-tokens", type=int, default=1500)
    args = ap.parse_args()

    secret = _prefix(args.prefix_tokens)         # tenant A's "confidential" prefix
    control = _prefix(args.prefix_tokens)        # a different, never-seen prefix

    print("== Multi-tenant prefix-cache isolation check ==")
    print(f"endpoint={args.base_url} model={args.model} trials={args.trials}\n")

    # Sanity: does the endpoint cache at all? Tenant A, cold then warm on its own prefix.
    a_cold = _post(args.base_url, args.tenant_a_key, args.model, secret)
    a_warm_med, _ = _median_latency(args.base_url, args.tenant_a_key, args.model, secret, args.trials)
    caches = a_warm_med < a_cold * 0.8
    print(f"[sanity] tenant-A cold={a_cold*1000:.0f}ms  warm-median={a_warm_med*1000:.0f}ms  "
          f"=> caching {'OBSERVED' if caches else 'not observed'}")

    # Cross-tenant: tenant B on A's (now warm) prefix vs B on a fresh control prefix.
    b_on_a_med, _ = _median_latency(args.base_url, args.tenant_b_key, args.model, secret, args.trials)
    b_ctrl_med, _ = _median_latency(args.base_url, args.tenant_b_key, args.model, control, args.trials)
    ratio = b_on_a_med / b_ctrl_med if b_ctrl_med else 1.0

    print(f"[cross]  tenant-B on tenant-A's prefix={b_on_a_med*1000:.0f}ms  "
          f"tenant-B on fresh control={b_ctrl_med*1000:.0f}ms  ratio={ratio:.2f}\n")

    if not caches:
        verdict, detail = "INCONCLUSIVE", ("No prefix caching observed at all, so the timing channel "
                                           "is absent here. Re-run under load or confirm caching config.")
    elif ratio < 0.7:
        verdict, detail = "FAIL", ("Tenant B got a strong cache speedup on tenant A's prefix => the "
                                   "prefix/KV cache is SHARED across tenants => cross-tenant prompt "
                                   "inference is possible. Add per-tenant cache isolation (cache_salt).")
    elif ratio > 0.9:
        verdict, detail = "PASS", ("Caching is on, but tenant B saw no speedup on tenant A's prefix => "
                                   "cache appears correctly isolated per tenant.")
    else:
        verdict, detail = "REVIEW", ("Partial speedup. Increase --trials and --prefix-tokens and re-run; "
                                     "investigate cache key construction.")

    print(f"VERDICT: {verdict}\n{detail}")
    sys.exit(0 if verdict in ("PASS", "INCONCLUSIVE") else 1)


if __name__ == "__main__":
    main()
