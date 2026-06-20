# Multi-Tenant AI Isolation Audit , Report

**Client:** {{company}}  **Product:** {{ai_feature}}  **Date:** {{date}}  **Auditor:** {{auditor}}

---

## 1. Executive summary
{{company}}'s {{ai_feature}} serves multiple customers (tenants) through shared AI infrastructure.
This audit assessed whether one tenant's data or prompts can reach another tenant, across the ten
layers of the AI request pipeline. 

**Overall result:** {{PASS / ISSUES FOUND}}.  **Critical findings:** {{n}}.  **High:** {{n}}.

This report is structured so it can be shared directly with a customer's security reviewer as
evidence of per-tenant isolation.

## 2. Scope & method
- Tenancy model reviewed: {{shared-infra / per-tenant store / hybrid}}.
- One production request traced end to end on {{date}}.
- The ten-layer isolation framework applied (auth, routing, RAG, prompt, cache, memory, tools, cost,
  logging, egress).
- A live cross-tenant **prefix-cache timing test** executed against {{endpoint}} with two tenant
  credentials (method: NDSS-2025 prefill timing side-channel; tool: `prefix_cache_check.py`).

## 3. Findings
| # | Layer | Result | Severity | Evidence | Remediation |
|---|---|---|---|---|---|
| 1 | Auth & tenant identity | {{Pass/Fail}} | {{}} | {{}} | {{}} |
| 2 | Tenant resolution | {{}} | {{}} | {{}} | {{}} |
| 3 | Data & RAG isolation | {{}} | {{}} | {{}} | {{}} |
| 4 | Prompt / context build | {{}} | {{}} | {{}} | {{}} |
| 5 | **Inference & cache** | {{}} | {{}} | cache check ratio {{x.xx}} | per-tenant cache_salt |
| 6 | Memory / state | {{}} | {{}} | {{}} | {{}} |
| 7 | Tool / action scope | {{}} | {{}} | {{}} | {{}} |
| 8 | Cost attribution | {{}} | {{}} | {{}} | {{}} |
| 9 | Logging / observability | {{}} | {{}} | {{}} | {{}} |
| 10 | Egress / DLP | {{}} | {{}} | {{}} | {{}} |

### 3a. Cross-tenant cache test (the headline)
- Tenant B latency on tenant A's prefix: {{}} ms. On a fresh control prefix: {{}} ms. Ratio: {{}}.
- **Interpretation:** {{shared cache detected => cross-tenant prompt inference possible / no cross-tenant
  speedup => cache correctly isolated}}.

## 4. Remediation plan
| Priority | Fix | Layer | Effort | Owner |
|---|---|---|---|---|
| P0 | {{}} | {{}} | {{}} | {{}} |
| P1 | {{}} | {{}} | {{}} | {{}} |

## 5. Isolation attestation (for your customers' security reviews)
As of {{date}}, {{company}}'s {{ai_feature}} was assessed against the ten-layer multi-tenant AI
isolation framework. {{After remediation,}} no cross-tenant data path was identified at the
{{Critical}} severity level. Method and evidence are documented above and are reproducible via the
included test tooling.

*Re-test recommended after any change to the AI pipeline, caching, retrieval, or tenancy model.*
