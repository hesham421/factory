<!-- source: PHASE:SEC-BE -->
<!-- traces: REQ-FIN-038, REQ-FIN-044 -->
<!-- PHASE:SEC-BE:START traces=REQ-FIN-038,REQ-FIN-044 -->
## PHASE 7 — SEC-BE (security, backend half)

| Screen (page code) | VIEW | CREATE | UPDATE | DELETE | Custom |
|---|---|---|---|---|---|
| FIN_ACCOUNTS | ✓ (API-FIN-001) | ✓ (API-FIN-002) | ✓ (API-FIN-003, and API-FIN-004 deactivate) | — | — |
| FIN_DIMENSIONS | ✓ (API-FIN-005,008) | ✓ (API-FIN-006,007) | ✓ (API-FIN-035, deactivate a dimension VALUE — `PERM_FIN_DIMENSIONS_UPDATE`, added by V28) | — | — |
| FIN_RULES | ✓ (API-FIN-009) | ✓ (API-FIN-010) | ✓ (API-FIN-011, add line; and API-FIN-034, deactivate rule) | — | — |
| FIN_RECURRING_TEMPLATES | ✓ (API-FIN-012) | ✓ (API-FIN-013) | ✓ (API-FIN-014, run; and API-FIN-036, deactivate template) | — | — |
| FIN_ALLOCATION_RULES | ✓ (API-FIN-015) | ✓ (API-FIN-016) | ✓ (API-FIN-017, run; and API-FIN-037, deactivate rule) | — | — |
| FIN_JOURNAL_ENTRIES | ✓ (API-FIN-018,022) | ✓ (API-FIN-019,020) | — | — | Reverse (`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, API-FIN-021) |
| FIN_PERIODS | ✓ (API-FIN-033, search periods — and still the gateway, see below) | ✓ (API-FIN-023, year) | ✓ (API-FIN-024,025) | — | Close-approve (`PERM_FIN_PERIODS_CLOSE_APPROVE`, API-FIN-026,027 — the distinct permission RULE-FIN-015 requires) |
| FIN_ACCOUNT_LEDGER | ✓ (API-FIN-028) | — | — | — | — |
| FIN_TRIAL_BALANCE | ✓ (API-FIN-029) | — | — | — | — |
| FIN_BALANCE_SHEET | ✓ (API-FIN-030) | — | — | — | — |
| FIN_INCOME_STATEMENT | ✓ (API-FIN-031) | — | — | — | — |
| FIN_DIMENSION_REPORTS | ✓ (API-FIN-032) | — | — | — | — |

**DELETE column — deliberately empty everywhere.** FIN exposes no `DELETE` endpoint at all.
Deactivation is `PUT /{id}/deactivate` gated by the screen's UPDATE permission (see
`AccountService.deactivate`, `@PreAuthorize` on `PERM_FIN_ACCOUNTS_UPDATE`), exactly as
MDL_LOOKUPS models it, and neither V24 nor V28 seeds a `PERM_FIN_*_DELETE` row for any FIN screen.
The FIN_ACCOUNTS row above read "✓ deactivate (API-FIN-004)" under DELETE until ALIGN-BE moved it
to UPDATE; inventing DELETE rows here would create permanently-unreferenced registry data. The two
later deactivates follow the same modelling: API-FIN-034 (event-type rule) under FIN_RULES/UPDATE,
API-FIN-035 (dimension value) under FIN_DIMENSIONS/UPDATE, API-FIN-036 (recurring template) under
FIN_RECURRING_TEMPLATES/UPDATE and API-FIN-037 (allocation rule) under FIN_ALLOCATION_RULES/UPDATE.
There are five deactivate endpoints in FIN and no `activate` anywhere — API-FIN-034, 035, 036 and
037 each deliberately omit a counterpart, following the delivered `AccountService.deactivate`
precedent.

**FIN_DIMENSIONS / UPDATE — the one cell V24 did not seed.** `PERM_FIN_DIMENSIONS_UPDATE` is
declared in `PermissionConstants` and registered by `V28__fin_dimensions_update_action.sql`, which
also grants it explicitly to `SYS_ADMIN`. The explicit grant is not optional: V25 grants SYS_ADMIN
its FIN actions with a `SELECT` over `SEC_ACTION_REG` and has already run everywhere, so Flyway
will never re-evaluate it against a row inserted later — registering without granting is exactly
the MDL failure V19/V21 had to repair. Tiers 1 and 2 need nothing new (V25 already grants SYS_ADMIN
the FIN module row and every FIN screen, FIN_DIMENSIONS included), and the RULE-SEC-007 gateway
holds because V24/V25 already registered and granted `PERM_FIN_DIMENSIONS_VIEW` on the same screen.
`FIN_CLOSE_APPROVER` (V27) deliberately gets nothing from V28 — its grants are scoped to
FIN_PERIODS and two permission codes.

**FIN_RULES / UPDATE — one permission, two endpoints.** API-FIN-034 reuses the pre-existing
`PERM_FIN_RULES_UPDATE` that V24 already seeds and V25 already granted, so it needed no new
constant, no new error code and no migration.

**FIN_RECURRING_TEMPLATES / UPDATE and FIN_ALLOCATION_RULES / UPDATE — the same shape, two
endpoints each.** API-FIN-036 reuses `PERM_FIN_RECURRING_TEMPLATES_UPDATE` and API-FIN-037 reuses
`PERM_FIN_ALLOCATION_RULES_UPDATE`; both action rows are seeded by V24 (`FIN_RECURRING_TEMPLATES /
UPDATE` and `FIN_ALLOCATION_RULES / UPDATE`) and both are already granted to SYS_ADMIN by V25's
Tier-3 statement, which grants every FIN action row except `PERM_FIN_PERIODS_CLOSE_APPROVE`. So
neither endpoint needed a new constant, a new error code or a migration — unlike API-FIN-035, whose
`FIN_DIMENSIONS / UPDATE` row did not exist and had to be both registered and explicitly granted by
V28. Each screen's UPDATE cell therefore now covers a run AND a deactivate.

**Deactivating now DOES stop the run — defect closed 2026-09-12, by decision rather than by rule.**
The permission gate above is still the whole of what API-FIN-036/037 themselves enforce, but the
two run endpoints are no longer indifferent to the flag. `RecurringTemplateService.run`
(API-FIN-014) and `AllocationRuleService.run` (API-FIN-017) each call `assertCanRun()` on the
loaded row's Domain companion — `RecurringTemplateDomain`, created for this, and
`AllocationRuleDomain` — and refuse a deactivated definition with `FIN-409-NOT-ACTIVE` (409).
**No RULE-FIN-* states this gate**; it rests on a recorded human decision, because closing the gap
required a new "exists but is inactive" error code that no requirement asks for. Do not cite it as
pre-existing spec. What remains open on those two screens is only that neither a template nor an
allocation rule can be UPDATED after creation. Recorded in full at srs-fin.md SCR-REQ-FIN-004 §B4,
SCR-REQ-FIN-005 §B4 and §"Access summary", and in SVC-API-CRUD's API-FIN-036/037 blocks.

**FIN_PERIODS / VIEW — a gateway that now also has an endpoint.** `PERM_FIN_PERIODS_VIEW` is a
real V24 action row and is load-bearing: `MenuService.effectiveAuthorityCodes()` keeps a granted
permission only if the same screen also carries a granted gateway (VIEW) action, so V27's
FIN_CLOSE_APPROVER role must hold it for `PERM_FIN_PERIODS_CLOSE_APPROVE` to survive into the
caller's authorities. That much is unchanged.

What HAS changed: the row is no longer constant-less and no longer endpoint-less. API-FIN-033
(`POST /api/v1/fin/fiscal-periods/search`, `FiscalPeriodService.search`) is gated on
`PERM_FIN_PERIODS_VIEW`, and the matching `PermissionConstants` constant was added with it. No
migration was needed — the action row was already registered by V24 and already granted by V25 and
V27. This section previously recorded the opposite state ("no `PermissionConstants` constant,
because FIN publishes no fiscal-period read endpoint … §B5 and the API registry define no search
API"); that was accurate before API-FIN-033 and is superseded now. srs-fin.md SCR-REQ-FIN-007 §B5
carries the endpoint row.

**Seed data** (REQ-FIN-044): 12 SEC_PAGES rows registered via SEC's screen-registration
endpoint at FIN onboarding; one action row per action above via SEC's action-registration
endpoint, following `PERM_<PAGE_CODE>_<ACTION>` — including the two custom actions
(`PERM_FIN_JOURNAL_ENTRIES_REVERSE`, `PERM_FIN_PERIODS_CLOSE_APPROVE`). Delivered as migrations
V24 (registry) and V25 (SYS_ADMIN grants); V27 adds the dedicated `FIN_CLOSE_APPROVER` role; V28
adds the one later action row, `FIN_DIMENSIONS / UPDATE`, together with its own explicit SYS_ADMIN
grant; V30 grants `PERM_FIN_PERIODS_CLOSE_APPROVE` to `SYS_ADMIN`, the one row V25 had
deliberately withheld — see the SoD section below.

**SoD enforcement (RULE-FIN-015, POL-FIN-016) — SPECIFICATION REWRITTEN 2026-09-12.** What the
SRS actually requires, read at source: RULE-FIN-015 (srs-fin.md:1026-1033) requires the
period-close-approval action to be "gated by a permission distinct from the journal-entry-creation
permission, enforced through the Security module", and its `Data source` line reads "DEFERRED —
the permission matrix is the Security module's declaration surface; FIN declares no permission
entity in this version, so the separation is enforced there and has no FIN-side field to read".
REQ-FIN-038 (:781-788) states the same requirement, and AC-FIN-038 (:789-792) describes an
ordinary interceptor denial: "Given a role holding only the entry-creation permission / When that
role's user attempts the period-close-approval action / Then the system denies it (the CORE
interceptor, per SEC's own mechanism)."

That is the whole requirement, and it is satisfied in full by the delivered
`@PreAuthorize(PermissionConstants.PERM_FIN_PERIODS_CLOSE_APPROVE)` on
`FiscalPeriodService.hardClose` (API-FIN-026) and `FiscalYearService.yearEndClose`
(API-FIN-027). `PERM_FIN_PERIODS_CLOSE_APPROVE` is a different permission code from
`PERM_FIN_JOURNAL_ENTRIES_CREATE`, and SEC's own mechanism enforces it — `JwtAuthenticationFilter`
builds the caller's authorities from `MenuService`, which reads `SEC_ROLE_ACTION_GRANT`. Keeping
the two codes off the same role remains a sound administrative guideline, and `FIN_CLOSE_APPROVER`
(V27) is how a deployment expresses it; it is a guideline, not a constraint FIN code enforces.

**WHAT THIS SECTION USED TO SPECIFY, AND MUST NOT SPECIFY AGAIN.** Every earlier revision of this
paragraph said FIN's service layer "additionally checks at hard-close/year-end-close time that no
single *user* holds both, per role union". **That sentence is the origin of the defect** — it is a
GLOBAL user-set-disjointness rule, strictly stronger than anything the SRS states, and it was
implemented exactly as written: `FinSeparationOfDutiesService` read SEC's user directory and
`FiscalPeriodDomain.assertCanHardClose` threw `FIN-403-SOD-VIOLATION` whenever ANY single user in
the system held both codes, refusing the close for EVERY caller — including an approver who was
himself perfectly clean. Both classes were DELETED on 2026-09-12 by recorded human decision. This
section is rewritten rather than annotated precisely so that a future generation pass reading it
cannot regenerate the removed behaviour. **No FIN service reads SEC's user directory, and none may
be specified to here.** FIN has no cross-module dependency on SEC at all any more: XM-FIN-002 is
retired (INT-C), and `FIN-403-SOD-VIOLATION` is struck as unreachable in the Error Catalog.

**Who can actually close, as seeded.** V25 deliberately withheld `PERM_FIN_PERIODS_CLOSE_APPROVE`
from `SYS_ADMIN`, because granting it would have put the bootstrap `admin` user into both
permission sets and tripped the removed check on every close. With the check gone that exclusion
had no purpose, and `V30__fin_sys_admin_close_approve_grant.sql` reverses it by granting the single
withheld action row to `SYS_ADMIN`. So on a fresh database **the bootstrap `admin` user can now
hard-close a period and run a year-end close** — endpoints V25 had left answering 403 to every
principal. V27's `FIN_CLOSE_APPROVER` role (module FIN, screen FIN_PERIODS, exactly the
`PERM_FIN_PERIODS_VIEW` gateway plus `PERM_FIN_PERIODS_CLOSE_APPROVE`, and by construction no entry
creation) **remains valid** and is still the least-privilege way to give close approval to someone
who is not a system administrator. It is simply no longer REQUIRED for the close to work at all.

**V27's own "OPERATIONAL PRECONDITIONS" text is now factually wrong in BOTH numbered points, and
V27 is applied and immutable — this prose is the correction, because the source cannot be fixed.**
V27's header states (1) that a user assignment is still required, because
`FinSeparationOfDutiesService.resolveFacts()` reports `closeApprovePermissionHeld =
!approvers.isEmpty()` and `FiscalPeriodDomain.assertCanHardClose` throws when nobody holds
close-approval; and (2) that the assignee must not be a journal-entry creator and must NOT be the
bootstrap `admin`, or `FIN-403-SOD-VIOLATION` trips on every close. **Neither holds.** There is no
`resolveFacts()`, no `assertCanHardClose`, and no thrower of `FIN-403-SOD-VIOLATION` anywhere in
the codebase: "nobody holds close-approval" is no longer a failure mode, and assigning
`FIN_CLOSE_APPROVER` to a journal-entry creator — or to `admin`, who now holds the permission
directly via V30 — breaks nothing. Read V27's header as the history of a removed mechanism, never
as live operating instructions. (The same applies to V25's header, which explains its exclusion in
the same removed terms; V30's own header records the reversal in full.)

**Gateway**: every non-VIEW permission requires VIEW on the same screen first (platform
convention, SEC's own interceptor — not restated as a FIN-owned RULE).

**Forbidden responses**: both FIN 403 codes map through the `LocalizedException` envelope, each
carrying a registered FIN code and both ar/en messages — but only `FIN-403-FORBIDDEN` is still
reachable; see the next paragraph.

`FIN-403-SOD-VIOLATION` is STRUCK and no longer reachable, so it is not among them. It was never a
Spring Security `AccessDeniedException` — it was a business refusal thrown by hand as a
`LocalizedException`, so no advisor or handler for access denial was ever involved in it, and that
much is unchanged. What changed on 2026-09-12 is that BOTH of its throw sites were deleted with the
SoD over-implementation, so nothing raises it at all. The constant
`FinErrorCodes.FIN_403_SOD_VIOLATION` and both bundle entries were deliberately left in place by
the code session; they are dead text, not a live response.

`FIN-403-FORBIDDEN` now does too, and **this reverses what this section previously said**. It is a
real `FinErrorCodes.FIN_403_FORBIDDEN` constant and has entries in BOTH
`src/main/resources/i18n/messages.properties` and `messages_ar.properties`. A `@PreAuthorize`
denial on any `com.erp.fin.service.*` method is intercepted by
`com.erp.fin.security.FinForbiddenAdvisor`, which catches the `AccessDeniedException` and re-raises
it as `LocalizedException(Status.FORBIDDEN, FinErrorCodes.FIN_403_FORBIDDEN)`; `GlobalExceptionHandler`
then renders it like every other FIN error. The advisor is a `DefaultPointcutAdvisor` at
`Ordered.HIGHEST_PRECEDENCE`, declared once for the whole module — never per endpoint, and never as
a feature-module `@ControllerAdvice`, which `gov-enforce-backend-contract` CU.7 forbids. It mirrors
`com.erp.sec.security.SecForbiddenAdvisor`. So **FIN-403-FORBIDDEN does reach the wire**, and the
earlier claim that it is "the catalog's *name* for a platform response, not a FIN code" is
superseded.

Two boundaries bound that statement, and both were read in source rather than assumed:

1. **Filter-chain denials are still `SEC-403-FORBIDDEN`.** A denial raised before any FIN service is
   entered never reaches an AOP proxy or `GlobalExceptionHandler`; it is written directly by the
   chain's `accessDeniedHandler`. Today this is unreachable for FIN: `SecurityConfig` (`com.erp.main.config`)
   authorizes with `.anyRequest().authenticated()` and declares no FIN authority rule, so every FIN
   permission denial is in fact a `@PreAuthorize` denial on a FIN service and does pass through the
   advisor. Adding a URL-level authority rule for a FIN path would change that.
2. **`FIN-403-SOD-VIOLATION` is moot.** It never was an `AccessDeniedException`, so the advisor
   never saw it; and since 2026-09-12 it has no throw site at all. See the SoD section above.

What DID change, platform-wide: the 403 body is now localized. `handleAccessDenied` resolves its
message through the same `resolveMessage(...)` helper and `MessageSource` every other handler uses,
keyed on a new `CommonErrorCodes.ACCESS_DENIED` constant, and `ACCESS_DENIED` was added to BOTH
`messages.properties` and `messages_ar.properties`. The wire `code` is unchanged and the English
text is byte-identical to the string that was hardcoded before, so only Arabic callers observe any
difference. The earlier description of this response as carrying "a hardcoded English message,
bypassing `MessageSource`" is therefore no longer accurate; the separate point — that this is a
platform response and not a FIN code — still stands, as does the fact that routing it through
`LocalizedException` would change every module's 403 envelope and remains a platform decision.
<!-- PHASE:SEC-BE:END -->
