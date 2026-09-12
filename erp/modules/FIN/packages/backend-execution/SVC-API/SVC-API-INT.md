<!-- source: PHASE:SVC-API / SUB:SVC-API-INT -->
<!-- context: SVC-API-HEADER.md — phase-level preamble -->
<!-- traces: DBF-FIN-034, DBF-FIN-041, DBF-FIN-042, DBF-FIN-043, DBF-FIN-066, DBF-FIN-067, DBF-FIN-068, DBF-FIN-069, DBF-FIN-077, DBF-FIN-082, DBF-FIN-083, DBF-FIN-084, DBF-FIN-090, DBF-FIN-106, DBF-FIN-107, DBF-FIN-112, DBF-FIN-115, DBF-FIN-133, DBF-FIN-145, DBF-FIN-146, REQ-FIN-010, REQ-FIN-011, REQ-FIN-012, REQ-FIN-013, REQ-FIN-017, REQ-FIN-018, REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-023, REQ-FIN-024, REQ-FIN-026, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038 -->
<!-- SUB:SVC-API-INT:START traces=REQ-FIN-010,REQ-FIN-023,REQ-FIN-024,REQ-FIN-026,REQ-FIN-028,REQ-FIN-031,REQ-FIN-034,REQ-FIN-036,REQ-FIN-037 -->
### SUB — SVC-API-INT (posting-pipeline orchestration and period-control actions)

<!-- API:API-FIN-020:START traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,DBF-FIN-041,DBF-FIN-090,DBF-FIN-106,DBF-FIN-107 -->
### API-FIN-020 — build event entry (system)
Endpoint: POST /api/v1/fin/journal-entries/from-event · Layers: `JournalEntryController.buildFromEvent`→`EventEntryService.build`
Request: the canonical accounting event payload (opaque shape, out-of-scope Event consumer, POL-FIN-020)
Response: 201 · `JournalEntryResponse` (statusCode=POSTED) — or a rejection recorded for operator follow-up (REQ-FIN-013)
Validations: RULE-FIN-004 (duplicate eventReference, QR-FIN-026), RULE-FIN-005 (active
rule exists, QR-FIN-027), RULE-FIN-003 (the single-remainder guarantee RULE-FIN-010 depends
on, re-checked over the stored line set, QR-FIN-016), RULE-FIN-010 (PER-SIDE remainder
difference, QR-FIN-028), then the same RULE-FIN-006/007/008/009 checks as API-FIN-019
(QR-FIN-029..032)
Errors: `FIN-409-DUPLICATE-EVENT`, `FIN-404-NO-ACTIVE-RULE`, `FIN-409-REMAINDER-COUNT`,
`FIN-422-REMAINDER-MARKER`, `FIN-422-REMAINDER-NOT-POSITIVE`, `FIN-409-UNBALANCED`,
`FIN-409-NOT-POSTABLE-ACCOUNT`, `FIN-409-PERIOD-NOT-OPEN`, `FIN-409-INVALID-DIMENSION`,
`FIN-422-MAPPING-UNSUPPORTED` (a rule line whose accountDerivationTypeCode is MAPPING — the
derivation fails loudly, since db-script-fin.md declares no mapping store; CONSTANT and
DIRECT are unaffected)
Orchestration: check RULE-FIN-004 (QR-FIN-026) → resolve active rule (QR-FIN-027) →
generate docNo (under the fiscal-year allocation lock, as API-FIN-019) → build lines from
the rule against the event's fields, computing the remainder line last as the difference
between the total already carried by the OPPOSING posting side and the total already carried
by the remainder line's own side (QR-FIN-028, QR-FIN-025) — a side-blind total would subtract
debit and credit lines alike from the base amount and produce a negative amount that dies on
CHK_FIN_JOURNAL_LINE_AMOUNT_POSITIVE; a remainder that computes to zero or less is
`FIN-422-REMAINDER-NOT-POSITIVE`. Which line is the remainder is read from `isRemainderFl`
alone (DBF-FIN-103), the same marker RULE-FIN-003's guard counts → validate (QR-FIN-029..032)
→ post (QR-FIN-033) → return
Repository: QR-FIN-025, QR-FIN-026, QR-FIN-027, QR-FIN-028, QR-FIN-029..033 · join NONE ·
READ_WRITE (one transaction, build-through-post)
Security: system-to-system call (the Event consumer's own service principal), gated by
the same interceptor as any authenticated caller · `PERM_FIN_JOURNAL_ENTRIES_CREATE`
Localization: n/a (no free-text description supplied by an event)
<!-- API:API-FIN-020:END -->

<!-- API:API-FIN-014:START traces=REQ-FIN-023,REQ-FIN-024,DBF-FIN-115,DBF-FIN-112 -->
### API-FIN-014 — run template
Endpoint: POST /api/v1/fin/recurring-templates/{id}/run · Layers: `RecurringTemplateController.run`→`RecurringTemplateService.run`
Request: path `id` (or invoked by an internal scheduler with no path — the endpoint is the
same either way) · Response: 201 · `JournalEntryResponse`
Validations: the template must still be ACTIVE — `RecurringTemplateDomain.assertCanRun()`
(the NEW Domain companion for ENT-FIN-011) runs FIRST, immediately after the row is loaded and
before the period is resolved, and refuses a deactivated template with `FIN-409-NOT-ACTIVE`;
**no RULE-FIN-* states this gate — it rests on a recorded human decision of 2026-09-12, not on
stated requirement.** Then the same RULE-FIN-006/007/008/009 checks as API-FIN-019 (the
template's own lines were already balance-checked at API-FIN-013 create time, but re-validated
here since accounts/periods may have changed since)
Errors: same as API-FIN-019, plus `FIN-404-TEMPLATE` (unknown recurring template id) and
`FIN-409-NOT-ACTIVE` (the template exists but is deactivated)
Orchestration: load template (QR-FIN-019) → assert it is active → build entry from its lines (journalTypeCode=
RECURRING) → validate + post (QR-FIN-029..033) → advance nextRunDate per frequencyCode →
if scheduleTypeCode=REVERSING: also build and post the linked reversal in the next period
(REQ-FIN-024, reusing RULE-FIN-011/012 via QR-FIN-034/036) → return
Repository: QR-FIN-019, QR-FIN-024(-style build), QR-FIN-029..033, QR-FIN-034, QR-FIN-036
· join NONE · READ_WRITE
Security: screen FIN_RECURRING_TEMPLATES · `PERM_FIN_RECURRING_TEMPLATES_UPDATE` (running
a template is modeled as an update-class custom action) · Localization: n/a
<!-- API:API-FIN-014:END -->

<!-- API:API-FIN-017:START traces=REQ-FIN-026,DBF-FIN-133,DBF-FIN-145,DBF-FIN-146 -->
### API-FIN-017 — run allocation rule
Endpoint: POST /api/v1/fin/allocation-rules/{id}/run · Layers: `AllocationRuleController.run`→`AllocationRuleService.run`
Request: path `id` · Response: 201 · `JournalEntryResponse`
Validations: the rule must still be ACTIVE — `AllocationRuleDomain.assertCanRun()` runs FIRST,
immediately after the row is loaded and before the target set is even fetched, and refuses a
deactivated rule with `FIN-409-NOT-ACTIVE`; **no RULE-FIN-* states this gate — it rests on a
recorded human decision of 2026-09-12, not on stated requirement.** Then RULE-FIN-003 (single
remainder marker over the stored targets, QR-FIN-016) and RULE-FIN-010 (per-side remainder
guarantee, QR-FIN-028, reused) then RULE-FIN-006/007/008/009
Errors: same family as API-FIN-019, plus `FIN-404-ALLOCATION-RULE`, `FIN-409-NOT-ACTIVE`,
`FIN-409-REMAINDER-COUNT`, `FIN-422-REMAINDER-MARKER`, `FIN-422-REMAINDER-NOT-POSITIVE`
Orchestration: load rule → assert it is active → load targets + current source-account balance (QR-FIN-022) →
distribute per target's distributionTypeCode, the target marked `isRemainderFl`
(DBF-FIN-141, the single marker — not `distributionTypeCode`) absorbing the rounding
difference between the source line's side and the targets' own side (QR-FIN-028) → build
entry (journalTypeCode=ALLOCATION) → validate + post (QR-FIN-029..033) → return
Repository: QR-FIN-022, QR-FIN-028, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_ALLOCATION_RULES · `PERM_FIN_ALLOCATION_RULES_UPDATE` · Localization: n/a
<!-- API:API-FIN-017:END -->

<!-- API:API-FIN-021:START traces=REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,DBF-FIN-042,DBF-FIN-043 -->
### API-FIN-021 — reverse entry
Endpoint: POST /api/v1/fin/journal-entries/{id}/reverse · Layers: `JournalEntryController.reverse`→`JournalEntryService.reverse`
Request: path `id` · Response: 201 · `JournalEntryResponse` (the new reversal entry)
Validations: RULE-FIN-013 (must be POSTED and not already reversed, QR-FIN-035); RULE-FIN-012
(period substitution if original's is closed, QR-FIN-036)
Errors: `FIN-409-NOT-POSTED`, `FIN-409-ALREADY-REVERSED`, `FIN-404-ENTRY`
Orchestration: load original UNDER A ROW LOCK (`SELECT ... FOR UPDATE` on the
FIN_JOURNAL_ENTRY header — no FIN entity carries `@Version`, so without it two concurrent
reversals both read reversalEntryId as null, both post a mirror, and the second save
overwrites the first link, leaving one orphaned mirror and a net effect of −(original)) →
check RULE-FIN-013 (QR-FIN-035) → resolve posting period
(original's if Open, else the current open period per RULE-FIN-012, QR-FIN-036) → build
mirrored lines with opposite directions, same amounts (RULE-FIN-011, QR-FIN-034) →
validate + post (QR-FIN-029..033, journalTypeCode=REVERSAL) → set originalEntryId/
reversalEntryId on both rows (bidirectional link) → return. Classic reversal: the original
STAYS POSTED — the only write back to it is the reversalEntryId link (DBF-FIN-043); its
statusCode is never modified, so both entries are seen by the POSTED-only report queries and
the pair nets to zero (SRS A7). Because the original stays POSTED, the double-reversal half of
RULE-FIN-013 is an explicit guard on the reversal link: a second reverse on the same entry is
rejected with `FIN-409-ALREADY-REVERSED` (AC-FIN-030), which would otherwise post a second
mirror and leave a net effect of −(original).
Repository: QR-FIN-034, QR-FIN-035, QR-FIN-036, QR-FIN-029..033 · join NONE · READ_WRITE
Security: screen FIN_JOURNAL_ENTRIES · `PERM_FIN_JOURNAL_ENTRIES_REVERSE` (custom action) · Localization: n/a
<!-- API:API-FIN-021:END -->

<!-- API:API-FIN-023:START traces=REQ-FIN-031,DBF-FIN-066,DBF-FIN-067,DBF-FIN-068,DBF-FIN-077 -->
### API-FIN-023 — create fiscal year
Endpoint: POST /api/v1/fin/fiscal-years · Layers: `FiscalYearController.create`→`FiscalYearService.create`
Request: `{code, startDate, endDate, periodCount}` · Response: 201 · `FiscalYearResponse` with its generated periods
Validations: uniqueness of code
Errors: `FIN-409-YEAR-DUP`
Orchestration: validate → persist year (statusCode=OPEN) + generate periodCount periods,
each statusCode=OPEN (QR-FIN-038) → return
Period spans and names (governed, not implicit): when `periodCount` = 12 and
[startDate, endDate] spans one whole calendar year, each generated period IS a calendar
month — period N runs from the 1st to the last day of the Nth month of the span — and its
NAME_AR / NAME_EN (DBF-FIN-078/079, both NOT NULL) are that month's own name in Arabic and
English, taken from the platform's locale data (`java.time.Month` + CLDR), never a
hardcoded string table. For any other `periodCount`, or a span that is not a whole year,
the fallback is the even split: the days of [startDate, endDate] divided into periodCount
contiguous blocks, the first (totalDays mod periodCount) blocks one day longer, so the last
period always ends on the year's endDate and no day belongs to two periods; those periods
are named "الفترة N" / "Period N".
Repository: QR-FIN-038 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CREATE` · Localization: n/a
<!-- API:API-FIN-023:END -->

<!-- API:API-FIN-024:START traces=REQ-FIN-032,DBF-FIN-082 -->
### API-FIN-024 — open period
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/open · Layers: `FiscalPeriodController.open`→`FiscalPeriodService.open`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: current state must be SOFT_CLOSE (§10.2 "re-openable" — Hard Closed is not, RULE-FIN-014)
Errors: `FIN-409-NOT-REOPENABLE`, `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040) → transition (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_UPDATE` · Localization: n/a
<!-- API:API-FIN-024:END -->

<!-- API:API-FIN-025:START traces=REQ-FIN-033,DBF-FIN-082 -->
### API-FIN-025 — soft-close period
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/soft-close · Layers: `FiscalPeriodController.softClose`→`FiscalPeriodService.softClose`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: current state must be OPEN · Errors: `FIN-409-INVALID-TRANSITION`, `FIN-404-PERIOD`
Orchestration: load → transition (QR-FIN-039) → return · Repository: QR-FIN-039 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_UPDATE` · Localization: n/a
<!-- API:API-FIN-025:END -->

<!-- API:API-FIN-026:START traces=REQ-FIN-034,REQ-FIN-035,REQ-FIN-037,REQ-FIN-038,DBF-FIN-082,DBF-FIN-083,DBF-FIN-084 -->
### API-FIN-026 — hard-close period (approval)
Endpoint: PATCH /api/v1/fin/fiscal-periods/{id}/hard-close · Layers: `FiscalPeriodController.hardClose`→`FiscalPeriodService.hardClose`
Request: path `id` · Response: 200 · `FiscalPeriodResponse`
Validations: RULE-FIN-014 (not already Hard Closed, QR-FIN-040); RULE-FIN-015 (full text:
DATA-DOM §ENT-FIN-008) — caller must hold `PERM_FIN_PERIODS_CLOSE_APPROVE`, a permission
distinct from `PERM_FIN_JOURNAL_ENTRIES_CREATE`. **That gate is the WHOLE of the rule**: the
`@PreAuthorize` on `FiscalPeriodService.hardClose`, enforced by SEC's own mechanism, exactly as
RULE-FIN-015 states it and AC-FIN-038 describes it. There is NO service-layer SoD read — the
one that existed was deleted on 2026-09-12 as an over-implementation (it refused the close for
every caller whenever any single user held both codes); see the Error Catalog's struck
`FIN-403-SOD-VIOLATION` row and retired XM-FIN-002
Errors: `FIN-409-NOT-REOPENABLE`(reused message context), `FIN-404-PERIOD`
Orchestration: load → check RULE-FIN-014 (QR-FIN-040)
→ transition, set closedBy/closedAt to the approving principal (QR-FIN-039) → return
Repository: QR-FIN-039, QR-FIN-040 · join NONE · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` (custom — the distinct permission RULE-FIN-015 requires; since V30 it is also granted to SYS_ADMIN) · Localization: n/a
<!-- API:API-FIN-026:END -->

<!-- API:API-FIN-027:START traces=REQ-FIN-036,DBF-FIN-069,DBF-FIN-034 -->
### API-FIN-027 — run year-end close
Endpoint: POST /api/v1/fin/fiscal-years/{id}/year-end-close · Layers: `FiscalYearController.yearEndClose`→`FiscalYearService.yearEndClose`
Request: path `id` · Response: 201 · `{closingEntry: JournalEntryResponse, openingEntry: JournalEntryResponse}`
Validations, IN THIS ORDER (the order is part of the contract — a test asserting 409 on this
endpoint must not be defeated by a missing successor year or Retained Earnings
account): (1) the fiscal year's own statusCode must
still be OPEN — a re-run against an already-CLOSED year is rejected with
`FIN-409-INVALID-TRANSITION`, a stated rule on ENT-FIN-007's state machine rather than the
incidental `FIN-409-PERIODS-NOT-CLOSED` the first run's own YEAR_END_CLOSE transitions would
otherwise raise; (2) every period of the year must be HARD_CLOSE (§10.4 precondition), 409.
Only then are the successor year and the Retained Earnings account resolved.
RULE-FIN-015 is no longer a numbered step here: it is enforced entirely by this endpoint's
`@PreAuthorize(PERM_FIN_PERIODS_CLOSE_APPROVE)` gate, which rejects before the method body
runs. The step that used to come first — a service-layer SoD read answering 403 — was deleted
on 2026-09-12 as an over-implementation; see the Error Catalog's struck `FIN-403-SOD-VIOLATION`
row. **A test written against the old contract and asserting 403 from inside this method will
now fail, and should be retargeted at the `@PreAuthorize` gate.**
Errors: `FIN-409-INVALID-TRANSITION` (year already closed), `FIN-409-PERIODS-NOT-CLOSED`, `FIN-404-YEAR` (unknown year id, or no adjacent successor year), `FIN-404-ACCOUNT` (no account marked as Retained Earnings)
Orchestration: verify the year is still OPEN → verify all periods Hard
Closed → resolve the successor year and the Retained Earnings account → compute closing
balances (QR-FIN-041) →
build + post a closing entry into the year's LAST period (result accounts → Retained
Earnings, journalTypeCode=CLOSING). The Retained Earnings account is DERIVED BY THE SYSTEM
from FIN_ACCOUNT.is_retained_earnings_fl (DBF-FIN-147, at most one row TRUE — partial unique
index UQ_FIN_ACCOUNT_RETAINED_EARNINGS) and is never supplied by the caller; no marked
account is `FIN-404-ACCOUNT`
→ build + post the next year's opening entry from the resulting balance-sheet balances
(journalTypeCode=OPENING, QR-FIN-041, POL-FIN-010) — CLOSING/OPENING are two values added
to the JOURNAL_TYPE lookup this stage (see Decisions Applied — a data-only, non-breaking
extension, not a new REQ/RULE) → mark FiscalYear statusCode=CLOSED, periods
statusCode=YEAR_END_CLOSE → return
Repository: QR-FIN-041, QR-FIN-029, QR-FIN-030, QR-FIN-032, QR-FIN-033 (both generated
entries go through the same validated posting pipeline) · QR-FIN-031 is deliberately NOT
applied to either of them: RULE-FIN-008 itself exempts the year-end closing and opening
entries, since this API's own all-periods-Hard-Closed precondition leaves no Open period for
the closing entry to post into. RULE-FIN-006/007/009 apply to both in full · the successor
fiscal year receiving the opening entry is resolved by DATE ADJACENCY (the year whose
startDate is the day after this year's endDate) — a DERIVED decision, recorded as such in
execution-state.json because ENT-FIN-007 declares no successor column; no such year is
`FIN-404-YEAR` · join intra-module · READ_WRITE
Security: screen FIN_PERIODS · `PERM_FIN_PERIODS_CLOSE_APPROVE` · Localization: n/a
DORMANT YEAR — a reviewed decision, not an accident. For a fiscal year in which no result account
carries a non-zero balance, `FiscalYearService.closingLines` contributes no line at all (each
result account with `net().signum() == 0` is skipped, and the Retained Earnings absorbing line is
added only when the running `resultTotal` is itself non-zero), and symmetrically
`openingLines` contributes none when no balance-sheet account carries a non-zero balance. The run
therefore posts a CLOSING (and OPENING) journal entry with an EMPTY line set, and that entry still
consumes a `docNo`: `JournalPostingService.buildValidateAndPost` allocates the number from the
locked fiscal-year series before it validates, and writes the entry unconditionally.
This was reviewed and deliberately KEPT. `JournalEntryDomain.checkBalanced` sums debits and
credits and returns empty when they compare equal, so 0 = 0 passes — a lineless entry literally
satisfies AC-FIN-036's "both entries individually balanced". Omitting the entry would make
AC-FIN-036's "posts a closing entry" false, and refusing the close outright would invent a rule no
artifact states.
Reachable only from here. `JournalEntryCreateRequest.lines` carries `@NotEmpty`, so API-FIN-019
rejects a lineless entry at the DTO boundary. This shape exists solely on the internal year-end
path, which builds its lines itself and never passes through that DTO.
<!-- API:API-FIN-027:END -->
<!-- SUB:SVC-API-INT:END -->
