<!-- source: PHASE:INT-XM -->
<!-- traces: API-FIN-002, REQ-FIN-001, XM-FIN-001 -->
<!-- PHASE:INT-XM:START traces=REQ-FIN-001,XM-FIN-001 -->
FIN declares one XM (XM-FIN-001, SOFT-READ → MDL's lookup values); MDL is in the current
selection, so this is a real linking atom.

<!-- TC:TC-FIN-047:START traces=XM-FIN-001,REQ-FIN-001,API-FIN-002 -->
### TC-FIN-047 — graceful degradation when MDL is unreachable during lookup validation
Derived from : XM-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-002 POST /api/v1/fin/accounts (representative of every lookup-validating API)
Rule / code  : XM-FIN-001 (SOFT-READ) → FIN-503 (a defined error, never a 500/unhandled state)
Scenario     : INTEGRATION · data class EDGE · language ALL
Preconditions: MDL's `GET /api/v1/mdl/lookups` (API-MDL-011) is made unreachable/times out
Steps        : 1. POST a new account (accountTypeCode requires MDL validation) while MDL is down
Expected     : the request fails with FIN-503, message ar "تعذّر التحقق من القيمة المرجعية مؤقتًا" / en "Could not verify the reference value right now" — never a raw crash
Test data    : any account payload; MDL endpoint simulated as down
<!-- TC:TC-FIN-047:END -->
<!-- PHASE:INT-XM:END -->
