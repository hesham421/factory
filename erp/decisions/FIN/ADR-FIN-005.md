# ADR-FIN-005 — screen gating reads the security module's effective menu; FIN publishes no permission-read endpoint

Module  : FIN     Version : v1     Stage raised : P3.2 (Frontend — UX Design + Execution Plan)
Status  : ACCEPTED (non-breaking)

## Context
§RF4 requires every route element to be guarded by its permission, and §RF5 requires a
navigation guard per screen. The names are fixed and not in dispute: the SRS Access summary
and `backend-execution-plan-fin.md` declare `PERM_FIN_ACCOUNTS_VIEW`, `PERM_FIN_RULES_UPDATE`,
`PERM_FIN_PERIODS_CLOSE_APPROVE` and the rest, all following
`PERM_<PAGE_CODE>_<ACTION>`.

What no FIN endpoint publishes is the *caller's own* set. `_inputs/api-docs-fin.md` has no
endpoint returning the current principal's permissions or screens — every FIN endpoint is a
business operation gated by `@PreAuthorize`, and REQ-FIN-044 states the design deliberately:
FIN registers its module, screens and actions **into the Security module** and owns no
security of its own [POL-FIN-015]. The caller's effective grants are therefore SEC's to
serve, through the effective-menu read its own frontend plan already binds
(`registry-exec-be-sec.md` → API-SEC-027).

## Decision
A FIN screen's navigation guard is "this screen's page code is present in the effective menu
the security module serves for this caller" — the same gate SEC's own screens use. FIN
neither publishes nor duplicates a permission read, and composes no permission name at
runtime.

Action-level affordances (create, update, run, reverse, close-approve) render for a caller
who holds the screen, and the server's `FIN-403-FORBIDDEN` is the authority on the write
itself, shown as its localized catalog message. A second client-side test would be a weaker
copy of the server's.

As with ADR-FIN-004, the foreign endpoint is named in `ui-ux-spec-fin.md`; the execution plan
states the gate in terms of the page code and never cites a foreign `API-*` id.

## Consequences
- Every route of a FIN screen carries that screen's VIEW gate, including `new`, `:id` and
  `:id/edit` — the gateway convention (`conventions.security_model.gateway_action`) means no
  other permission applies without VIEW anyway.
- `PERM_FIN_PERIODS_CLOSE_APPROVE` (RULE-FIN-015) is not readable client-side either, so the
  hard-close and year-end-close affordances render for any caller holding `FIN_PERIODS`, and
  a caller without the approval permission receives the server's 403. The separation of duty
  is enforced where the rule says it is — in the Security module — not by hiding a button.
- A failure to load the menu renders no FIN entry and grants no FIN route: access narrows,
  never widens.
- No `REQ-*` changes; RULE-FIN-015 is unaffected.
