# ADR-FIN-008 — `journalTypeCode` is a required input on the manual-entry form, although SRS B3 marks it system-set

Module  : FIN     Version : v1     Stage raised : P3.2 (Frontend — UX Design + Execution Plan)
Status  : ACCEPTED (non-breaking)

## Context
`srs-fin.md` SCR-REQ-FIN-006 §B3 reads: "Header fields: docDate, periodId, descriptionAr,
descriptionEn (ENT-FIN-004; docNo/statusCode/journalTypeCode system-set)".

The published `JournalEntryCreateRequest` (API-FIN-019) declares four required header fields:
`docDate`, `fiscalYearId`, `periodId` and **`journalTypeCode`** (maxLength 20), plus the
optional descriptions and the required `lines[]`. So the request carries two fields B3 does
not list as inputs: `fiscalYearId` and `journalTypeCode`. `docNo` and `statusCode` are indeed
absent from the request and are system-set exactly as B3 says.

`fiscalYearId` is not in dispute — RULE-FIN-017, added during SVC-API, requires the submitted
period to belong to the submitted fiscal year and the document date to fall inside that
period, which means all three must be submitted together for the rule to have anything to
check.

`journalTypeCode` is the real divergence. ENT-FIN-004 declares it required and lookup-backed
(`JOURNAL_TYPE`: EVENT_GENERATED, MANUAL, RECURRING, ALLOCATION, REVERSAL), and for a manual
entry there is exactly one value the SRS admits: `MANUAL` (REQ-FIN-014, POL-FIN-018 — a manual
entry follows the same path as any other source, classified by its source).

## Decision
The manual-entry form submits `journalTypeCode = MANUAL` as a **fixed, non-editable value**,
rendered read-only beside the header rather than offered as a select. The field is in the
form model because the request requires it; it is not an input because the screen has exactly
one legitimate value for it and the SRS says so.

`fiscalYearId` is a real input, selected together with the period: the period select is filtered
by the chosen year, and RULE-FIN-017 is the server-side check behind that pairing.

## Consequences
- No `JOURNAL_TYPE` select appears on the entry form; the key is still displayed (read-only,
  and on the search filter it is a real select) and still resolves through UXD-FIN-005.
- A user cannot mislabel a manual entry as `EVENT_GENERATED` or `REVERSAL` — those values are
  produced by API-FIN-020 and API-FIN-021 respectively, never by this form.
- The SRS B3 line stays accurate about `docNo` and `statusCode` and is narrowed, here and in
  `ui-ux-spec-fin.md` → SCR-FIN-006, for `journalTypeCode` and `fiscalYearId`.
- No `REQ-*` changes and no rule is weakened: RULE-FIN-017's three fields all reach the server.
