<!-- source: PHASE:INT-C -->
<!-- traces: REQ-FIN-001, REQ-FIN-007, REQ-FIN-008, REQ-FIN-010, REQ-FIN-014, REQ-FIN-018, REQ-FIN-022, REQ-FIN-025, REQ-FIN-031, REQ-FIN-037, REQ-FIN-038 -->
<!-- PHASE:INT-C:START traces=REQ-FIN-001 -->
## PHASE 5 — INT-C (cross-module consume)

One `XM-*` row (XM-FIN-001), below the split threshold (1 < 5) — no SUB opened.
A second row, XM-FIN-002 (READ → SEC), was assigned at ALIGN-BE — SEC-BE landed after this
phase was written and added what then looked like a second, genuinely distinct cross-module
consumption — and was RETIRED on 2026-09-12. Its block below is kept as a historical record,
struck; it must not be read as a live dependency.

<!-- XM:XM-FIN-001:START traces=REQ-FIN-001,REQ-FIN-007,REQ-FIN-008,REQ-FIN-010,REQ-FIN-014,REQ-FIN-018,REQ-FIN-022,REQ-FIN-025,REQ-FIN-031 -->
### XM-FIN-001 — validate/read lookup-backed codes against MDL
Target        : MDL · ENT-MDL-001/002 (LookupType/LookupValue) · classification SOFT-READ
Interface     : in-process Spring injection — FIN's service layer injects
`com.erp.mdl.crossmodule.MdlLookupApi` and calls `readActiveValuesByKey(typeKey)` for every
one of FIN's 13 owned keys, at the point each lookup-backed field is written or offered as a select-list
Contract      : data required = the submitted code exists as an active value under the
named type, checked by membership in the returned `List<LookupOptionView>` (code, labelAr,
labelEn, sortOrder); fallback if absent = reject with `FIN-400-INVALID-LOOKUP`; an unknown/
inactive `typeKey` raises MDL's `LocalizedException(NOT_FOUND, MDL_404_TYPE_KEY)`, which FIN
catches and translates to `FIN-400-INVALID-LOOKUP` (MDL's code never leaks out of FIN's API);
retry = none (same-process call, no network hop); idempotency
= read-only, naturally idempotent
Blocks        : none DEFERRED — MDL v1 is already gated (pass-1 APPROVE); ACTIVE from the
moment FIN v1 is created
<!-- XM:XM-FIN-001:END -->

<!-- XM:XM-FIN-002:START traces=REQ-FIN-037,REQ-FIN-038 -->
### ~~XM-FIN-002~~ — RETIRED 2026-09-12 (historical record, NOT a live dependency)
Status        : RETIRED. Kept so a reader reconstructing the decision can see what was
registered and why it went away. It binds nothing today and no code consumes it. The id is
burned, not reused.
What it was   : a READ of SEC's user→permission directory, classification READ, target SEC ·
ENT-SEC-001 (User) + SEC's role/permission grant tables. `FinSeparationOfDutiesService`
injected `com.erp.sec.crossmodule.SecUserDirectoryApi` and called
`findUserIdsHoldingPermission(permissionCode)` twice, for `PERM_FIN_PERIODS_CLOSE_APPROVE` and
`PERM_FIN_JOURNAL_ENTRIES_CREATE`, on every API-FIN-026 hard-close and API-FIN-027 year-end
close (never HTTP); it derived `closeApprovePermissionHeld` and `entryCreatePermissionShared`
and handed them to `FiscalPeriodDomain.assertCanHardClose`, which threw
`FIN-403-SOD-VIOLATION`.
Why it is gone: that check enforced GLOBAL user-set disjointness — if ANY single user in the
system held both permissions, the close was refused for EVERY caller, including a perfectly
clean approver — and no REQ, AC or RULE requires it. RULE-FIN-015 (srs-fin.md:1026-1033)
requires only that the close-approval action be gated by a permission DISTINCT from the
journal-entry-creation permission, "enforced through the Security module", and its `Data
source` line reads "DEFERRED — ... has no FIN-side field to read"; REQ-FIN-038
(srs-fin.md:781-788) and AC-FIN-038 (:789-792) say the same, the latter describing an ordinary
interceptor denial. By recorded human decision on 2026-09-12 the over-implementation was
removed: `FinSeparationOfDutiesService` and `FiscalPeriodDomain.assertCanHardClose(...)` were
deleted. RULE-FIN-015 still stands, enforced by the delivered
`@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate on `FiscalPeriodService.hardClose` and
`FiscalYearService.yearEndClose`.
Consequence   : that service was FIN's ONLY consumer of `com.erp.sec.crossmodule`, so **FIN's
cross-module dependency on SEC is gone entirely**. The only remaining `com.erp.sec` mentions
under `src/main/java/com/erp/fin/` are `@PreAuthorize` SpEL string literals naming
`PermissionConstants`, plus two javadoc references — neither is a structural dependency.
`FIN-403-SOD-VIOLATION` is correspondingly struck as unreachable in the Error Catalog.
<!-- XM:XM-FIN-002:END -->

FIN's dependency on SEC for identity/authorization (the principal on every request, the
`@PreAuthorize` gate, and FIN's own self-registration of its module/screens/actions into SEC)
remains NOT a formal `XM` row — ADR-FIN-001 (carried from P2), unchanged — and since 2026-09-12
it is the ONLY relationship FIN has with SEC. XM-FIN-002 had been registered separately on the
grounds that it was a different thing: not the platform's ambient authorization of the caller
but FIN's own business logic reading SEC's data *about other users* — a named FIN service
calling a named SEC `crossmodule` interface method, whose returned rows were an input to a FIN
business rule (RULE-FIN-015) and whose absence had a defined, FIN-owned failure code. That
reasoning was sound for exactly as long as the consumption existed. It stopped applying when
the service making the call was deleted. Nothing about ADR-FIN-001 changed; what changed is
that there is no longer a second, non-ambient consumption for it to fail to cover.
<!-- PHASE:INT-C:END -->
