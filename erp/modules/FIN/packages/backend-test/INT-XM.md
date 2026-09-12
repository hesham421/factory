<!-- source: PHASE:INT-XM -->
<!-- traces: AC-FIN-038, API-FIN-002, API-FIN-026, REQ-FIN-001, REQ-FIN-037, REQ-FIN-038, XM-FIN-001 -->
<!-- PHASE:INT-XM:START traces=REQ-FIN-001,REQ-FIN-037,REQ-FIN-038,XM-FIN-001 -->
FIN declares exactly ONE XM: XM-FIN-001 (SOFT-READ → MDL's lookup values), consumed by
FinLookupValidationService through the injected MdlLookupApi. MDL is in the current selection, so it
is a real linking atom.
XM-FIN-002 (READ → SEC's user→permission directory, registered at ALIGN-BE for the RULE-FIN-015
fact) NO LONGER EXISTS — REVISED 2026-09-12. Its only consumer, FinSeparationOfDutiesService, was
deleted by a recorded human decision, and nothing under com.erp.fin imports com.erp.sec.crossmodule
any more. XM coverage for this module is therefore 1/1, down from 2/2. TC-FIN-091, which existed
solely to exercise that call, is RETIRED below rather than deleted, so no id renumbers.

<!-- TC:TC-FIN-047:START traces=XM-FIN-001,REQ-FIN-001,API-FIN-002 -->
### TC-FIN-047 — MDL lookup-type not-found is translated into a FIN error code
Derived from : XM-FIN-001 (REQ-FIN-001) · Exercises: API-FIN-002 POST /api/v1/fin/accounts (representative of every lookup-validating API)
Rule / code  : XM-FIN-001 (SOFT-READ) → FIN-400-INVALID-LOOKUP (a defined error, never a 500/unhandled state, never MDL's raw code)
Scenario     : INTEGRATION · data class EDGE · language ALL
Preconditions: MDL's `ACCOUNT_TYPE` LookupType is absent or deactivated, so the injected `MdlLookupApi.readActiveValuesByKey("ACCOUNT_TYPE")` throws `LocalizedException(NOT_FOUND, MDL_404_TYPE_KEY)`. (XM-FIN-001 is in-process Spring injection inside the single deployable — there is no network hop, so the former "MDL unreachable / times out" precondition is not reachable and has been replaced by the real in-process failure mode.)
Steps        : 1. POST a new account (accountTypeCode requires MDL validation) while that lookup type is unavailable
Expected     : the request fails with FIN-400-INVALID-LOOKUP, message ar "القيمة المُدخلة غير صالحة" / en "The submitted value is not valid" — never a raw crash, and MDL's `MDL_404_TYPE_KEY` never surfaces to the caller
Test data    : any account payload; MDL's ACCOUNT_TYPE lookup type deactivated (or the MdlLookupApi test double configured to throw MDL_404_TYPE_KEY)
<!-- TC:TC-FIN-047:END -->

<!-- TC:TC-FIN-091:START traces=AC-FIN-038,REQ-FIN-037,REQ-FIN-038,API-FIN-026 -->
### TC-FIN-091 — RETIRED 2026-09-12 — asserts nothing; the SEC directory read it exercised no longer exists
Derived from : AC-FIN-038 (REQ-FIN-038), through the now-deleted XM-FIN-002 ·
  Exercised: API-FIN-026 PATCH /api/v1/fin/fiscal-periods/{id}/hard-close
Rule / code  : none — this TC is RETIRED and contributes NO coverage
Scenario     : RETIRED — do not implement, do not count as a gap
Status       : RETIRED 2026-09-12. The id is deliberately kept, never deleted and never renumbered,
  because it is referenced from the TC TRACEABILITY INDEX, test-execution-manifest-fin.md and
  packages/backend-test/state.json. Any runner that enumerates TCs must SKIP it and must NOT report
  it as a coverage gap.
Why retired  : it existed only to drive XM-FIN-002 — a test double for
  `SecUserDirectoryApi.findUserIdsHoldingPermission` throwing on the first call — and to assert that
  an unverified separation-of-duties fact answers 403 FIN-403-SOD-VIOLATION rather than approving the
  close. FIN makes no such call any more. FinSeparationOfDutiesService, FIN's only consumer of
  SecUserDirectoryApi, and FiscalPeriodDomain.assertCanHardClose(boolean, boolean) with it, were
  deleted by a recorded human decision; nothing under com.erp.fin imports com.erp.sec.crossmodule,
  and FIN-403-SOD-VIOLATION has no throw site anywhere in the module. There is no mock to install,
  no call to fail and no code to answer — so there is nothing real left to assert, which is why this
  was RETIRED rather than rewritten (unlike TC-FIN-059/060/061, each of which still had a true
  assertion available).
Coverage moved: REQ-FIN-037 is covered by TC-FIN-037 (closedBy/closedAt recorded as a distinct act)
  and now also by TC-FIN-059's Expected. REQ-FIN-038 is covered by TC-FIN-038 and TC-FIN-060 (the
  denial, on API-FIN-026 and API-FIN-027), TC-FIN-061 (the satisfied direction) and TC-FIN-062 (the
  gateway resolution). Neither REQ loses coverage. XM coverage DOES drop, 2/2 → 1/1
Traces note  : the `traces=` of this block names AC-FIN-038, the acceptance criterion whose
  denial direction this case asserted before XM-FIN-002 was deleted. The trace records where the
  case CAME FROM; it does not restore coverage — AC-FIN-038 is covered by TC-FIN-038, TC-FIN-060
  and TC-FIN-062, and this block still contributes none. It was added because `traces=` had been
  left with REQ and API ids only when XM-FIN-002 went, which left a defined TC with no
  AC/XM/UXD source at all (analyze C10.1, CRITICAL) — a retired case must still say what it was
  derived from. The id is still never enumerated by a runner.
Test data    : none
<!-- TC:TC-FIN-091:END -->
<!-- PHASE:INT-XM:END -->
