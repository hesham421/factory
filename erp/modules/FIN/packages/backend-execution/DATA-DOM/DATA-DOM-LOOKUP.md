<!-- source: PHASE:DATA-DOM / SUB:DATA-DOM-LOOKUP -->
<!-- context: DATA-DOM-HEADER.md — phase-level preamble -->
<!-- traces: REQ-FIN-004, REQ-FIN-007, REQ-FIN-022, REQ-FIN-025 -->
<!-- SUB:DATA-DOM-LOOKUP:START traces=REQ-FIN-004,REQ-FIN-007,REQ-FIN-022,REQ-FIN-025 -->
### SUB — DATA-DOM-LOOKUP (FIN's own config/lookup-kind structural data)

#### ENT-FIN-002 — Dimension      kind: config
BINDINGS: table `FIN_DIMENSION` · PK `dimensionPk` (DBF-FIN-014) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-014..022. DTO: create `{code, nameAr, nameEn}`; no update endpoint (name
edits go through a future v2 if needed — not named in the plan, so not built). DOMAIN
RULES: none scoped alone. REPOSITORY OPS → QR-FIN-007, QR-FIN-008, QR-FIN-046 (EXISTS, code unique).

#### ENT-FIN-003 — DimensionValue      kind: lookup
BINDINGS: table `FIN_DIMENSION_VALUE` · PK `dimensionValuePk` (DBF-FIN-023) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-023..033 — matches `profile.conventions.entity_defaults.lookup` exactly
(code, nameAr, nameEn, sortOrder, isActiveFl) plus PK/FK/audit. DOMAIN RULES:
**RULE-FIN-002** (duplicate code within dimension) — QR-FIN-010 — service + DB
(`UQ_FIN_DIMENSION_VALUE_DIM_CODE`). REPOSITORY OPS → QR-FIN-009, QR-FIN-010, QR-FIN-011.

#### ENT-FIN-009 — EventTypeRule      kind: config
BINDINGS: table `FIN_EVENT_TYPE_RULE` · PK `eventTypeRulePk` (DBF-FIN-089) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-089..097; `eventTypeCode` lookup-backed (XM-FIN-001). DOMAIN RULES: one
active rule per event type — DB (`UQ_FIN_EVENT_TYPE_RULE_CODE`) + QR-FIN-014. REPOSITORY
OPS → QR-FIN-012, QR-FIN-013, QR-FIN-014, QR-FIN-027 (reused at post time).

#### ENT-FIN-010 — RuleLine      kind: config
BINDINGS: table `FIN_RULE_LINE` · PK `ruleLinePk` (DBF-FIN-098) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-098..108; `accountDerivationTypeCode`/`amountSourceTypeCode`/
`directionCode`/`distributionTypeCode` all lookup-backed (XM-FIN-001). DOMAIN RULES:
**RULE-FIN-003** (exactly one remainder line whenever the line set is a compound or
percentage distribution — any sibling PERCENTAGE-distributed, or any line already marked
remainder — plus marker agreement: `isRemainderFl` (DBF-FIN-103) is the SINGLE remainder
marker, the one both this guard and the API-FIN-020 builder read, and must agree with the
line's own REMAINDER type code, `FIN-422-REMAINDER-MARKER`) — QR-FIN-016 —
`EventTypeRuleDomain`. REPOSITORY OPS → QR-FIN-015, QR-FIN-016; read as part of QR-FIN-025/028 at
event-entry build time.

#### ENT-FIN-011 — RecurringTemplate      kind: config
BINDINGS: table `FIN_RECURRING_TEMPLATE` · PK `recurringTemplatePk` (DBF-FIN-109) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-109..121; `scheduleTypeCode`/`frequencyCode` lookup-backed (XM-FIN-001).
DOMAIN RULES: none scoped alone (its run posts through the same shared pipeline as any
entry — RULE-FIN-006 through RULE-FIN-010, cited on API-FIN-014). REPOSITORY OPS →
QR-FIN-017, QR-FIN-018, QR-FIN-019.

#### ENT-FIN-012 — RecurringTemplateLine      kind: config
BINDINGS: table `FIN_RECURRING_TEMPLATE_LINE` · PK `recurringTemplateLinePk` (DBF-FIN-122) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-122..129; `directionCode` lookup-backed (XM-FIN-001); `amount` DB-CHECK'd
positive. DOMAIN RULES: none scoped alone. REPOSITORY OPS → written with QR-FIN-018; read
by QR-FIN-019 at run time.

#### ENT-FIN-013 — AllocationRule      kind: config
BINDINGS: table `FIN_ALLOCATION_RULE` · PK `allocationRulePk` (DBF-FIN-130) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-130..138. DOMAIN RULES: none scoped alone. REPOSITORY OPS → QR-FIN-020,
QR-FIN-021, QR-FIN-022.

#### ENT-FIN-014 — AllocationTarget      kind: config
BINDINGS: table `FIN_ALLOCATION_TARGET` · PK `allocationTargetPk` (DBF-FIN-139) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-139..146; `distributionTypeCode` lookup-backed (XM-FIN-001). DOMAIN RULES:
**RULE-FIN-003** (reused — exactly one remainder target whenever the target set is a
compound or percentage distribution, plus marker agreement between `isRemainderFl`
(DBF-FIN-141, the SINGLE marker the API-FIN-017 builder reads) and `distributionTypeCode`,
`FIN-422-REMAINDER-MARKER`) — QR-FIN-016 (reused) — `AllocationRuleDomain`. REPOSITORY OPS → written with QR-FIN-021; read by
QR-FIN-022 at run time.
<!-- SUB:DATA-DOM-LOOKUP:END -->
