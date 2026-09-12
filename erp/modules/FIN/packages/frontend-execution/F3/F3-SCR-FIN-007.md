<!-- source: PHASE:F3 / SUB:F3-SCR-FIN-007 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-031, AC-FIN-032, AC-FIN-033, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-037, AC-FIN-038, API-FIN-023, API-FIN-024, API-FIN-025, API-FIN-026, API-FIN-027, API-FIN-033, REQ-FIN-031, REQ-FIN-032, REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038, SCR-FIN-007, UXD-FIN-003, UXD-FIN-004 -->
<!-- SUB:F3-SCR-FIN-007:START traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,API-FIN-023,API-FIN-024,API-FIN-025,API-FIN-026,API-FIN-027,API-FIN-033,UXD-FIN-003,UXD-FIN-004,SCR-FIN-007 -->
### F3 · SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years

Validation timing for this form: **on blur for the year code, on submit for the rest**.
The period transitions carry no form at all — each is a path-id call with no body.
### F3-FIELD — SCR-FIN-007 (fiscal year, create)
code        · REQUIRED · LENGTH (maxLength 10) · UNIQUE_CHECK · when blur
startDate   · REQUIRED · when submit
endDate     · REQUIRED · DATE_RANGE (after `startDate`) · when submit
periodCount · REQUIRED · when submit
UNIQUE_CHECK : the year code has no published search to check against — no fiscal-year search
               exists (ADR-FIN-006) — so the check is **not** written as an async pre-check.
               `FIN-409-YEAR-DUP` from the server is the only authority, routed inline to
               `code`. A pre-check over the period rows would test a proxy, not the code.
### F3-VALIDATION — RULE-FIN-014      traces=REQ-FIN-035,AC-FIN-035
Statement : The system shall reject any attempt to reopen a Hard Closed period.
Message   : from the catalog code `FIN-409-NOT-REOPENABLE` —
            ar: "الفترة مغلقة إغلاقًا صارمًا ولا يمكن إعادة فتحها" ·
            en: "The period is hard-closed and cannot be reopened"
Scope     : the open action (API-FIN-024)
Field     : none — a row action · kind BUSINESS_RULE · when submit
Validation shape : the row offers only the transitions SRS §A7 allows from its current state,
            so a hard-closed row shows no Open affordance at all; the catalog message is still
            routed to a user message, because a row may be stale when the action is taken.
### F3-VALIDATION — RULE-FIN-015      traces=REQ-FIN-038,AC-FIN-038
Statement : The system shall gate the period-close-approval action behind a permission
            distinct from the journal-entry-creation permission, enforced by the Security
            module.
Message   : the rule's own text — ar: "صلاحية اعتماد الإغلاق منفصلة عن صلاحية إنشاء القيود" ·
            en: "The close-approval permission is separate from the entry-creation permission"
            — and, on refusal, the catalog's `FIN-403-FORBIDDEN`
Scope     : the hard-close and year-end-close actions
Field     : none — a row and a header action · kind BUSINESS_RULE · when submit
Validation shape : **server-side only, and by design.** The rule's own `Data source` line
            reads DEFERRED — there is no FIN-side fact to read — and no published endpoint
            tells this screen whether the caller holds `PERM_FIN_PERIODS_CLOSE_APPROVE`. The
            affordance therefore renders for anyone holding the screen and the server's 403 is
            the answer (ADR-FIN-005). Hiding the button would be a weaker copy of a check that
            already exists where the rule puts it.
The year-end close additionally answers `FIN-409-PERIODS-NOT-CLOSED` when a period of the year
is not hard-closed; the header shows that count as context beside the affordance, not as a gate.
Business-code fields: the year `code` is client-defined, not platform-numbered, and is
read-only after create because no update endpoint exists.
Locale       : session → browser → `ar`.
Permission-driven behaviour: as above — the forbidden message is the localized catalog text,
never a silent no-op.

<!-- SUB:F3-SCR-FIN-007:END -->
