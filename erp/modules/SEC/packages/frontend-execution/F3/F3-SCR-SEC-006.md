<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-006 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-016, AC-SEC-017, AC-SEC-018, AC-SEC-019, API-SEC-018, API-SEC-019, API-SEC-020, API-SEC-021, REQ-SEC-016, REQ-SEC-017, REQ-SEC-018, REQ-SEC-019, SCR-SEC-006 -->
<!-- SUB:F3-SCR-SEC-006:START traces=REQ-SEC-016,REQ-SEC-017,REQ-SEC-018,REQ-SEC-019,AC-SEC-016,AC-SEC-017,AC-SEC-018,AC-SEC-019,API-SEC-018,API-SEC-019,API-SEC-020,API-SEC-021,SCR-SEC-006 -->
### F3 · SCR-SEC-006 — سجل الوحدة/الشاشة/الإجراء / Module / screen / action registry

This screen has **no form**: every field is read-only, registration happens through the
registering module's own onboarding call, and the one edit the SRS names — deactivating a stale
row — has no published endpoint (ADR-SEC-008, ADR-SEC-009). There is therefore no validation
timing to declare and no field block to write.
### F3-VALIDATION — RULE-SEC-004      traces=REQ-SEC-018,AC-SEC-018
Statement : The system shall reject a screen registration whose module code has no
            ModuleRegistry row.
Message   : from the catalog code `SEC-409-MODULE-NOT-REGISTERED` —
            ar: "الوحدة غير مسجّلة" · en: "Module is not registered"
Scope     : CREATE (a screen registration, API-SEC-019)
Field     : `moduleCode` of `ScreenRegistryCreateRequest` · kind BUSINESS_RULE · when submit
Validation shape : **not enforced on any form in this frontend.** The rule binds
            `API-SEC-019`, which this frontend does not call (ADR-SEC-009); it is recorded here
            so the block that will enforce it — in the registering module's own screen — has a
            reconciled contract to inherit, message and catalog code included. No client-side
            pre-check is written, because a registry lookup before the call would be a second
            source of truth for a rule the server already owns.
Only the search filters accept input, and they are filters rather than a form: `module code`
(LIKE) and `pageCode` (EXACT), both plain strings with no published constraint to assert.
Locale       : session → browser → `ar`.
Permission-driven behaviour: the screen is read-only for every caller, so no permission
changes a field's behaviour here.

<!-- SUB:F3-SCR-SEC-006:END -->
