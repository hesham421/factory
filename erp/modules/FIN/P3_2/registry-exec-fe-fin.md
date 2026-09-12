## REGISTRY — P3.2 — FIN v1
══════════════════════════════════════════════════════════════════

ID RANGES
UXD-FIN-001 .. UXD-FIN-012 · SCR-FIN-001 .. SCR-FIN-012

SCR ids: SCR-FIN-001, SCR-FIN-002, SCR-FIN-003, SCR-FIN-004, SCR-FIN-005, SCR-FIN-006,
SCR-FIN-007, SCR-FIN-008, SCR-FIN-009, SCR-FIN-010, SCR-FIN-011, SCR-FIN-012

UXD ids: UXD-FIN-001, UXD-FIN-002, UXD-FIN-003, UXD-FIN-004, UXD-FIN-005, UXD-FIN-006,
UXD-FIN-007, UXD-FIN-008, UXD-FIN-009, UXD-FIN-010, UXD-FIN-011, UXD-FIN-012

Last sequence per atom: SCR: 012 · UXD: 012

SCREENS
| SCR | Name (ar / en) | Container pattern | Owning ENT | Permissions |
|---|---|---|---|---|
| SCR-FIN-001 | شجرة الحسابات / Chart of accounts | TREE_MASTER_DETAIL | ENT-FIN-001 | PERM_FIN_ACCOUNTS_VIEW, PERM_FIN_ACCOUNTS_CREATE, PERM_FIN_ACCOUNTS_UPDATE |
| SCR-FIN-002 | تعريف الأبعاد وقيمها / Dimension definition & values | TREE_MASTER_DETAIL | ENT-FIN-002 (+ ENT-FIN-003) | PERM_FIN_DIMENSIONS_VIEW, PERM_FIN_DIMENSIONS_CREATE, PERM_FIN_DIMENSIONS_UPDATE |
| SCR-FIN-003 | قواعد المحرك / Engine rules | FULL_PAGE | ENT-FIN-009 (+ ENT-FIN-010) | PERM_FIN_RULES_VIEW, PERM_FIN_RULES_CREATE, PERM_FIN_RULES_UPDATE |
| SCR-FIN-004 | قوالب متكررة/عكسية / Recurring / reversing templates | FULL_PAGE | ENT-FIN-011 (+ ENT-FIN-012) | PERM_FIN_RECURRING_TEMPLATES_VIEW, PERM_FIN_RECURRING_TEMPLATES_CREATE, PERM_FIN_RECURRING_TEMPLATES_UPDATE |
| SCR-FIN-005 | قواعد التوزيع / Allocation rules | FULL_PAGE | ENT-FIN-013 (+ ENT-FIN-014) | PERM_FIN_ALLOCATION_RULES_VIEW, PERM_FIN_ALLOCATION_RULES_CREATE, PERM_FIN_ALLOCATION_RULES_UPDATE |
| SCR-FIN-006 | قيود اليومية / Journal entries | FULL_PAGE | ENT-FIN-004 (+ ENT-FIN-005, ENT-FIN-006) | PERM_FIN_JOURNAL_ENTRIES_VIEW, PERM_FIN_JOURNAL_ENTRIES_CREATE, PERM_FIN_JOURNAL_ENTRIES_REVERSE |
| SCR-FIN-007 | الفترات والسنوات المالية / Fiscal periods & years | TREE_MASTER_DETAIL | ENT-FIN-007 (+ ENT-FIN-008) | PERM_FIN_PERIODS_VIEW, PERM_FIN_PERIODS_CREATE, PERM_FIN_PERIODS_UPDATE, PERM_FIN_PERIODS_CLOSE_APPROVE |
| SCR-FIN-008 | دفتر الحساب / Account ledger | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_ACCOUNT_LEDGER_VIEW |
| SCR-FIN-009 | ميزان المراجعة / Trial balance | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_TRIAL_BALANCE_VIEW |
| SCR-FIN-010 | الميزانية العمومية / Balance sheet | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_BALANCE_SHEET_VIEW |
| SCR-FIN-011 | قائمة الدخل / Income statement | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005 (live-derived) | PERM_FIN_INCOME_STATEMENT_VIEW |
| SCR-FIN-012 | تقارير الأبعاد / Dimension reports | FULL_PAGE (no entry sub-view — ADR-FIN-003) | ENT-FIN-005, ENT-FIN-006 (live-derived) | PERM_FIN_DIMENSION_REPORTS_VIEW |

UXD INDEX
| UXD | Screen(s) | Field | Owner module · API used |
|---|---|---|---|
| UXD-FIN-001 | SCR-FIN-001, SCR-FIN-009, SCR-FIN-010, SCR-FIN-011 | accountTypeCode (`ACCOUNT_TYPE`) | MDL · the lookup module's consumer read (named in ui-ux-spec-fin.md) |
| UXD-FIN-002 | SCR-FIN-001, SCR-FIN-003, SCR-FIN-004, SCR-FIN-006, SCR-FIN-008, SCR-FIN-009, SCR-FIN-010, SCR-FIN-011, SCR-FIN-012 | natureCode / directionCode (`DEBIT_CREDIT`) | MDL · same |
| UXD-FIN-003 | SCR-FIN-007 | period statusCode (`PERIOD_STATE`) | MDL · same |
| UXD-FIN-004 | SCR-FIN-007 | year statusCode (`FISCAL_YEAR_STATUS`) | MDL · same |
| UXD-FIN-005 | SCR-FIN-006, SCR-FIN-008 | journalTypeCode (`JOURNAL_TYPE`) | MDL · same |
| UXD-FIN-006 | SCR-FIN-006 | entry statusCode (`JOURNAL_STATUS`) | MDL · same |
| UXD-FIN-007 | SCR-FIN-003 | eventTypeCode (`ACCOUNTING_EVENT_TYPE`) | MDL · same |
| UXD-FIN-008 | SCR-FIN-003 | accountDerivationTypeCode (`ACCOUNT_DERIVATION_TYPE`) | MDL · same |
| UXD-FIN-009 | SCR-FIN-003 | amountSourceTypeCode (`AMOUNT_SOURCE_TYPE`) | MDL · same |
| UXD-FIN-010 | SCR-FIN-003, SCR-FIN-005 | distributionTypeCode (`DISTRIBUTION_TYPE`) | MDL · same |
| UXD-FIN-011 | SCR-FIN-004 | scheduleTypeCode (`RECURRING_SCHEDULE_TYPE`) | MDL · same |
| UXD-FIN-012 | SCR-FIN-004 | frequencyCode (`RECURRING_FREQUENCY`) | MDL · same |

One `UXD-*` per displayed lookup key, not per screen occurrence — the key is the unit the one
shared hook is built on (ADR-FIN-004). `PAYMENT_METHOD` is FIN-owned and registered by
REQ-FIN-045 but displayed by no FIN field in this version, so it mints none. The screen gate
(the security module's effective menu) is an authorization dependency, not a displayed field,
and is recorded in ADR-FIN-005 rather than minted as a `UXD-*`.

API COVERAGE
| Status | Count | API ids |
|---|---|---|
| used by this frontend | 36 | API-FIN-001..019, API-FIN-021..037 |
| documented, deliberately uncalled | 1 | API-FIN-020 — the event-sourced build a host system calls over the platform's in-process module interface; bound and blocked out in F2 — ADR-FIN-007 |
| used but undocumented | 0 | — no endpoint is called that the api-docs lack |
| documented but unbound | 0 | all 37 published endpoints are bound by the API ID BINDING annex — ADR-FIN-002 |

No verb or path differs between the plan, the SRS Part B tables and the published surface: the
annex matched all 37 on verb + path with no shape diff.

**Backend registry gap, carried forward.** `registry-exec-be-fin.md` lists
`API-FIN-001 .. API-FIN-032`. API-FIN-033 (fiscal-period search), API-FIN-034, API-FIN-035,
API-FIN-036 and API-FIN-037 (the four deactivates) are defined in
`backend-execution-plan-fin.md`, published in the api-docs and used by this frontend, but were
never carried into that registry's ID RANGES line — `gov.py analyze` already reports it against
P3.1. Closing it is one line in a backend artifact, which §8 puts outside this stage's
boundary. Recorded here and in ADR-FIN-002.

OPERATIONS WITHOUT AN ENDPOINT
template update · allocation-rule update · fiscal-year search · by-id read of an account, a
template, an allocation rule, a fiscal year or a fiscal period · rule-line, template-line and
allocation-target delete · parent-dimension deactivate — named by SRS Part B, required by no
`REQ-*`, and omitted from the frontend rather than faked (ADR-FIN-006).

LOOKUPS
| Key | Owner | Hook | Endpoint |
|---|---|---|---|
| ACCOUNT_TYPE | FIN (registered into MDL, REQ-FIN-045) | one shared hook | the lookup module's consumer read — UXD-FIN-001 |
| DEBIT_CREDIT | FIN → MDL | one shared hook | UXD-FIN-002 |
| PERIOD_STATE | FIN → MDL | one shared hook | UXD-FIN-003 |
| FISCAL_YEAR_STATUS | FIN → MDL | one shared hook | UXD-FIN-004 |
| JOURNAL_TYPE | FIN → MDL | one shared hook | UXD-FIN-005 |
| JOURNAL_STATUS | FIN → MDL | one shared hook | UXD-FIN-006 |
| ACCOUNTING_EVENT_TYPE | FIN → MDL | one shared hook | UXD-FIN-007 |
| ACCOUNT_DERIVATION_TYPE | FIN → MDL | one shared hook | UXD-FIN-008 |
| AMOUNT_SOURCE_TYPE | FIN → MDL | one shared hook | UXD-FIN-009 |
| DISTRIBUTION_TYPE | FIN → MDL | one shared hook | UXD-FIN-010 |
| RECURRING_SCHEDULE_TYPE | FIN → MDL | one shared hook | UXD-FIN-011 |
| RECURRING_FREQUENCY | FIN → MDL | one shared hook | UXD-FIN-012 |
| PAYMENT_METHOD | FIN → MDL | none | displayed by no FIN field this version |
Every lookup field stays a string holding the code and no enum is modelled anywhere in the
plan; no lookup validator binds a static list.

ALIGN-FE
The verdict row inside the plan's ALIGN-FE block is written by the orchestrator from the
analyze report; findings fixed by this stage: 0.

ADRs
erp/decisions/FIN/ADR-FIN-002.md (ACCEPTED, non-breaking — API id binding annex, and the stale backend API range) ·
erp/decisions/FIN/ADR-FIN-003.md (ACCEPTED, non-breaking — container pattern for screens with no entry sub-view) ·
erp/decisions/FIN/ADR-FIN-004.md (ACCEPTED, non-breaking — lookup values through the lookup module's consumer API, one UXD per key) ·
erp/decisions/FIN/ADR-FIN-005.md (ACCEPTED, non-breaking — screen gating reads the security module's effective menu) ·
erp/decisions/FIN/ADR-FIN-006.md (ACCEPTED, non-breaking — operations with no published endpoint) ·
erp/decisions/FIN/ADR-FIN-007.md (ACCEPTED, non-breaking — API-FIN-020 bound but drawn on no screen) ·
erp/decisions/FIN/ADR-FIN-008.md (ACCEPTED, non-breaking — the manual entry's journalTypeCode and fiscalYearId vs SRS B3)
Carried from earlier stages: ADR-FIN-001 (P2). No BLOCKED ADR.

TRACEABILITY
REQ covered by ≥1 SCR/F-block: 46/46 — REQ-FIN-001..043 each appear in the `traces=` of at
least one SUB block of every sub-bearing phase that owns their screen; REQ-FIN-044 is cited by
the SEC-FE phase (it is what registers FIN's screens in the security module, which is what the
menu gate reads) and REQ-FIN-045 by the F2 phase and by every lookup-bearing F2 SUB (it is what
registers the twelve lookup keys the hooks read); REQ-FIN-046 is cited by the four report
screens whose links form its drill-down chain.
Orphan REQ: none.
AC covered: 46/46 (each AC accompanies its REQ in the same traces).
SCR covered: 12/12 — every `SCR-*` carries a block in F1, F2, F3 and F4 (48 SUB blocks) and an
RF5 block in SEC-FE.
UXD cited by an F-block: 12 of 12 — none unreferenced, none dangling.

Event
"P3.2 completed: FIN v1 — 12 screens, 12 UXD, 37/37 API bound (36 called), 4 sub-bearing phases
× 12 SUB blocks, ALIGN-FE stamped by the orchestrator, 7 ADRs"
══════════════════════════════════════════════════════════════════
