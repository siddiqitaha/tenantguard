# TenantGuard

**Multi-tenant AI isolation audit.** A kit to find out whether a multi-tenant AI product can leak
data or prompts **across tenants**, and to produce a proof report the customer can hand to their own
customers' security reviewers.

The wedge: multi-tenant agentic AI isolation is a verified-open *operational* problem (teams bolt it
on piecemeal after incidents). Cross-tenant leaks are existential, and most teams cannot *prove*
isolation when asked. This kit makes that provable, fast. First vertical: **legal AI** (where
attorney-client privilege makes the fear , and the willingness to pay , highest).

## What is inside
- **`audit/FRAMEWORK.md`** , the repeatable ten-layer isolation assessment (the core method).
- **`audit/prefix_cache_check.py`** , a runnable, defensive cross-tenant cache-leak test (the demo
  that lands the sale). Detects whether an OpenAI-compatible endpoint shares its prefix/KV cache
  across tenants (NDSS-2025 timing side-channel).
- **`audit/report_template.md`** , the client deliverable, including an isolation attestation section
  written to be forwarded to a security reviewer.
- **`marketing/lead_magnet.md`** , the "Can your AI leak one law firm's data to another?" explainer
  that drives audits.

## Quickstart (the cache check)
Run against a system you own or are authorized to test, with two tenant credentials:
```
python audit/prefix_cache_check.py \
    --base-url http://localhost:4000/v1 \
    --tenant-a-key sk-tenantA --tenant-b-key sk-tenantB \
    --model your-model
```
Stdlib only, no dependencies. Exit code 0 on PASS/INCONCLUSIVE, 1 on FAIL/REVIEW.

## The offering this supports
A productized service: a fixed-fee **Isolation Audit** -> a managed-operation retainer -> a packaged
per-tenant governance + observability product.

## Scope & ethics
The cache check is a **defensive** tool for the system owner. Only run it against infrastructure you
own or are explicitly authorized to test.

Status: v1 , the method, the runnable check, the report, and the lead magnet. Next: a per-tenant
governance proxy (the productized remediation) and per-tenant cost/quality observability.
