# ADR-NOTE-006 — RULE-NOTE-004 تُنفَّذ بشكل الطلب لا بفرع تحقّق / RULE-NOTE-004 is enforced by DTO shape, with no catalog row

| Item | Value |
|---|---|
| Status | ACCEPTED (non-breaking) |
| Stage | P3.1 — backend execution plan |
| Module | NOTE v1 |
| Date | 2026-09-17 |
| Traces | REQ-NOTE-002, REQ-NOTE-005 |

## Context

RULE-NOTE-004 states that a note's owner may never change after creation, and carries a
user-facing message («لا يمكن تغيير مالك الملاحظة.» / "A note's owner cannot be changed.").
The engine's completeness rule is that every RULE listed in an endpoint's `Validations` has a
row in the error catalog. But AC-NOTE-003 settles the behaviour in the other direction: a
client-supplied owner is **ignored**, not rejected — the create endpoint stores the
authenticated principal regardless of what the request carried. The update request DTO carries
no owner field at all, and no mapper writes the column after creation.

A catalog row for this rule would therefore be raisable by no code path in the module: to
raise it, the service would first have to accept an owner value from the request in order to
detect that it differs — which is precisely what REQ-NOTE-002 forbids. An unreachable catalog
row reads downstream (test-gen, api-verify) as a behaviour that exists and can be asserted on.

## Decision

RULE-NOTE-004 is enforced structurally: `ownerUserRef` is absent from both request DTOs, it is
never mapped from a request, and the update statement does not touch the column. The rule is
listed in the entity block and in API-NOTE-004's `Validations` with its full text, marked as
enforced by DTO shape, and it carries **no error-catalog row and no validation branch**.

## Consequences

- No test can assert an "owner changed" error, because the module cannot produce one; the
  assertion available to test-gen is the positive one AC-NOTE-003 already states — the stored
  owner is the authenticated principal whatever the request carried.
- The SRS message text of RULE-NOTE-004 is preserved in the plan (it remains the rule's
  statement) but is not published as a runtime code.
- If a later version ever accepts an owner field on a request — an administrative reassignment,
  say — that version adds the branch and the catalog row, and supersedes this ADR.
