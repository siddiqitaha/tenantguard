# Multi-Tenant AI Isolation Audit , the framework

The repeatable assessment. For each layer: what can leak, what to check, and the pass bar. Isolation
in AI must hold at **every** layer of the request pipeline, which is what makes it harder than
classic database multi-tenancy. A single weak layer breaks the whole guarantee.

Severity: **C**ritical (cross-tenant data exposure possible) / **H**igh / **M**edium.

| # | Layer | What can leak | Check | Pass bar | Sev |
|---|---|---|---|---|---|
| 1 | Auth & tenant identity | wrong tenant assumed | Is tenant identity derived from a verified credential (not a client-supplied header/body field)? | Tenant id comes from the auth token server-side, never trusted from the request body | C |
| 2 | Tenant resolution / routing | request runs as another tenant | Trace one request: where is tenant context set, and can it be spoofed or omitted? | Every request carries a server-set tenant context; missing context fails closed | C |
| 3 | Data & RAG isolation | retrieval pulls another tenant's docs | Are vector stores / collections / namespaces per-tenant, and is every query tenant-filtered? | Retrieval is physically or logically partitioned per tenant; no global index without a tenant filter | C |
| 4 | Prompt / context build | another tenant's data in the prompt | Inspect the assembled prompt: any shared examples, history, or cache that crosses tenants? | Context is built only from this tenant's data | H |
| 5 | Inference & cache | prompt/KV cache shared across tenants (timing leak, NDSS 2025) | Run `prefix_cache_check.py` against the endpoint with two tenant keys | No cross-tenant cache speedup; per-tenant `cache_salt` in use | C |
| 6 | Memory / state | conversation or long-term memory bleeds across tenants | Are session + long-term memory keyed by tenant, with no shared store? | Memory reads/writes are tenant-scoped | C |
| 7 | Tool / action scope | a tool acts on another tenant's resources | Do tools receive tenant-scoped credentials (not a shared admin key)? | Tools use per-tenant scoped credentials; no ambient authority | C |
| 8 | Cost & usage attribution | wrong tenant billed; abuse hidden | Is every request tagged tenant_id / feature / model at the gateway before it leaves? | Per-tenant usage is attributable end to end | M |
| 9 | Logging / observability | logs/traces expose tenant content to others | Are logs, traces, and dashboards tenant-scoped, with content redaction? | No tenant can see another tenant's logs or prompt content | H |
| 10 | Egress / DLP | tenant data leaves to a 3rd-party model/tool | Is outbound data to external models/tools governed and tenant-scoped? | Egress is policy-checked (DLP) per tenant | H |

## How to run an audit (half a day)
1. **Scope.** Confirm the tenancy model and pull one real request trace end to end.
2. **Walk the 10 layers** above with the customer's engineer, recording evidence per row.
3. **Run the cache check** (`prefix_cache_check.py`) live , this is the demo that lands.
4. **Score** each layer Pass / Review / Fail with severity.
5. **Deliver the report** (see `report_template.md`): findings, the proof artifact, and a fix plan.

## The fixes you will most often prescribe
- Per-tenant `cache_salt` so prefix/KV cache keys never collide across tenants (layer 5).
- Server-derived tenant context, fail-closed on absence (layers 1-2).
- Tenant-filtered retrieval / per-tenant namespaces (layer 3).
- Per-tenant scoped tool credentials, no shared admin key (layer 7).
- Gateway-level tenant tagging + DLP on egress (layers 8, 10).
