<!-- source: PHASE:DATA-DOM / SUB:DATA-DOM-TRANSACTIONAL -->
<!-- context: DATA-DOM-HEADER.md — phase-level preamble -->
<!-- traces: REQ-FIN-010, REQ-FIN-014, REQ-FIN-017, REQ-FIN-028 -->
<!-- SUB:DATA-DOM-TRANSACTIONAL:START traces=REQ-FIN-010,REQ-FIN-014,REQ-FIN-017,REQ-FIN-028 -->
### SUB — DATA-DOM-TRANSACTIONAL

#### ENT-FIN-004 — JournalEntry      kind: transactional
BINDINGS: table `FIN_JOURNAL_ENTRY` · PK `journalEntryPk` (DBF-FIN-034) · PK generation `GENERATED ALWAYS AS IDENTITY`
BUSINESS CODE: **docNo** · column `doc_no` (DBF-FIN-035) · format:
`JV-{fiscalYearCode}-{NNNNNN}` (e.g. `JV-2026-000123`), counter scoped per `fiscalYearId`
and restarting at `000001` each fiscal year, single counter across all journal types
(`UQ_FIN_JOURNAL_ENTRY_YEAR_DOCNO`) · generation source: a FIN-local generator in
`com.erp.fin` (not `com.erp.common` — see CORE Numbering), invoked at create, before the
first save — excluded from every create/update request body, always present in responses.
FIELDS: DBF-FIN-034..050 — see DB Alignment Manifest; `journalTypeCode`/`statusCode`
lookup-backed (XM-FIN-001).
DTO MEMBERSHIP: manual-create request `{docDate, fiscalYearId, periodId, descriptionAr,
descriptionEn, lines: [...]}`; event-build request = the canonical event payload (opaque
to this DTO description — shape owned by the out-of-scope Event consumer, POL-FIN-020);
no update endpoint exists once POSTED (RULE-FIN-016); response includes all fields
including nested lines.
LOOKUP FIELDS: `journalTypeCode`→`JOURNAL_TYPE`, `statusCode`→`JOURNAL_STATUS`, both via
XM-FIN-001.
DOMAIN RULES:
**RULE-FIN-004** — duplicate eventReference rejected — QR-FIN-026 — service.
**RULE-FIN-005** — no active rule for event type — QR-FIN-027 — service.
**RULE-FIN-006** — debit=credit invariant — QR-FIN-029 — service (POL-FIN-001).
**RULE-FIN-008** — period open at post, except the year-end closing/opening entries the rule
itself exempts (REQ-FIN-036 / API-FIN-027) — QR-FIN-031 — service (POL-FIN-004).
**RULE-FIN-011** — reversal exact and linked — QR-FIN-034 — service (POL-FIN-007).
**RULE-FIN-012** — reversal posts to current period if original's closed — QR-FIN-036 — service.
**RULE-FIN-013** — reject reverse of non-POSTED, and reject reversing an entry that already
carries a reversal link (double-reversal) — QR-FIN-035 — service.
**RULE-FIN-016** — lock after posting — enforced by omission (no UPDATE/DELETE mapping on
a POSTED row in the repository layer at all) — service/repository.
**RULE-FIN-017** — the submitted fiscalYearId, periodId and docDate must describe one
accounting context (the period belongs to that year, DBF-FIN-076; the date falls inside the
period, DBF-FIN-080/081) — API-FIN-019 only, since every system-generated entry derives the
three from one another — `JournalEntryDomain.assertHeaderCoherent(...)` (ALIGN-BE;
`FIN-400-PERIOD-NOT-IN-YEAR`, `FIN-400-DOCDATE-OUTSIDE-PERIOD`).
**RULE-FIN-013's second half under concurrency** — the "already reversed" read-then-write is
made atomic by a PESSIMISTIC_WRITE load of the original's header before the guard runs
(ALIGN-BE); no FIN entity carries `@Version`, so without it two concurrent reversals both
post a mirror.
(Full text of every RULE above: srs-fin.md §A5 — not restated here per the single-source rule.)
STATE MACHINE: `statusCode` (JOURNAL_STATUS) per SRS A7 — DRAFT→POSTED (RULE-FIN-016 locks
immediately); POSTED is terminal. Classic reversal (RULE-FIN-011): reversing an entry leaves the
original POSTED and posts an equal, opposite mirror entry, the two linked through
`originalEntryId`/`reversalEntryId` (DBF-FIN-042/043) — net ledger effect zero. No path sets VOID.
CROSS-MODULE: `journalTypeCode`/`statusCode` touch XM-FIN-001.
REPOSITORY OPS → QR-FIN-023 through QR-FIN-037 (the full posting pipeline + reversal + read).

#### ENT-FIN-005 — JournalLine      kind: transactional
BINDINGS: table `FIN_JOURNAL_LINE` · PK `journalLinePk` (DBF-FIN-051) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-051..060 — see DB Alignment Manifest; `directionCode` lookup-backed
(XM-FIN-001); `amount` DB-CHECK'd positive (`CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE`, POL-FIN-005).
DTO MEMBERSHIP: written only as a nested array inside the entry create/build request; no
standalone line endpoint; never independently updated (locked with its header).
DOMAIN RULES: **RULE-FIN-007** (leaf/active account) — QR-FIN-030 — service;
**RULE-FIN-010** (remainder-line rounding) — QR-FIN-028 — service.
CROSS-MODULE: `directionCode` touches XM-FIN-001.
REPOSITORY OPS → written as part of QR-FIN-024/025/034 (SAVE, header+lines in one
transaction); read via QR-FIN-037, QR-FIN-042 (ledger), QR-FIN-043 (statements).

#### ENT-FIN-006 — JournalLineDimension      kind: transactional
BINDINGS: table `FIN_JOURNAL_LINE_DIM` · PK `journalLineDimensionPk` (DBF-FIN-061) · PK generation `GENERATED ALWAYS AS IDENTITY`
FIELDS: DBF-FIN-061..064 — see DB Alignment Manifest.
DTO MEMBERSHIP: nested under each line in the entry create/build request (0..N per line).
DOMAIN RULES: **RULE-FIN-009** (dimension value validity) — QR-FIN-032 — service.
CROSS-MODULE: none.
REPOSITORY OPS → written as part of QR-FIN-024/025/034; read via QR-FIN-044 (dimension report).
<!-- SUB:DATA-DOM-TRANSACTIONAL:END -->
