<!-- P0 stage output — governed by factory.yaml stages[P0]; see shared/GOVERNANCE-CORE.md -->
## BUSINESS POLICIES — Finance / المحاسبة والمالية (FIN)
══════════════════════════════════════════════════════════════════
Module   : FIN     Source of truth : FIN vision document (`general-accounting-system-plan-en.md`) + dialogue resolutions
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)

POL-FIN-001 — Dimensions defined as data
  Statement : The system shall support one or more account dimensions that are defined and maintained as configuration data, requiring no code change to add, remove, or change a dimension.
  Pattern   : ubiquitous
  Trigger   : Define/modify a dimension
  Rationale : Pluggability into any host system — a dimension (e.g. "Investor") is an example, never a hardcoded concept (plan §0, §1.2).
  Source    : plan §0, §1.2
  Status    : CONFIRMED

POL-FIN-002 — Event-type rules defined as data
  Statement : The system shall derive a journal entry from an accounting event solely through rules defined as data per event_type, without event-type-specific code.
  Pattern   : ubiquitous
  Trigger   : Receive a canonical accounting event
  Rationale : The engine carries no embedded accounting knowledge; adapting to a new event type or a new host system is a data change (plan §3.1, §3.4).
  Source    : plan §3.1, §3.4
  Status    : CONFIRMED

POL-FIN-003 — Dedicated, isolated reference data
  Statement : The system shall maintain all accounting reference data (lookups) in tables owned exclusively by FIN, with no link to or dependency on any other module's reference tables.
  Pattern   : ubiquitous
  Trigger   : Manage reference data (Lookups screen)
  Rationale : Generic pluggability into any host system, independent of that host's own reference data (plan §2.1).
  Source    : plan §2.1
  Status    : CONFIRMED

POL-FIN-004 — Direct posting after automatic validation
  Statement : When a journal entry (from any source) passes automatic validation, the system shall post it directly, with no per-entry human approval.
  Pattern   : event
  Trigger   : Submit / build an entry (event-generated, manual, recurring, or allocation)
  Rationale : Events are trusted and manual entries pass the same automatic validation; per-entry approval would not scale (plan §5.1, §5.2).
  Source    : plan §5.1, §5.2
  Status    : CONFIRMED

POL-FIN-005 — Period close is the sole human control point
  Statement : The system shall require a human approval before a fiscal period (soft or hard close) can be closed.
  Pattern   : ubiquitous
  Trigger   : Close period
  Rationale : Moves the single point of human control from the individual entry to the period, where it can review accumulated content (plan §5.2, §7.3).
  Source    : plan §5.2, §7.3
  Status    : CONFIRMED

POL-FIN-006 — Segregation of duties at period close
  Statement : The system shall prevent the user who created a journal entry from also being the approver who closes the period containing it.
  Pattern   : unwanted
  Trigger   : Close period
  Rationale : SoD moves from the entry level (no approval there) to the period level, enforced via RBAC (plan §5.2, §8.2).
  Source    : plan §5.2, §8.2
  Status    : CONFIRMED

POL-FIN-007 — Posted entries are locked; correction only by reversal
  Statement : If a posted journal entry requires correction, then the system shall require a new reversing entry rather than editing or deleting the original.
  Pattern   : unwanted
  Trigger   : Attempt to correct a posted entry
  Rationale : Preserves the full audit trail and prevents any suspicion of tampering (plan §5.3, §6.1).
  Source    : plan §5.3, §6.1
  Status    : CONFIRMED

POL-FIN-008 — Independent, accounting-only RBAC
  Statement : The system shall enforce access control through a role-based security model fully independent of any other module, with its own dedicated user accounts.
  Pattern   : ubiquitous
  Trigger   : Authenticate / authorize any FIN action
  Rationale : Consistent with FIN's total isolation from the host system (plan §8.1).
  Source    : plan §8.1
  Status    : CONFIRMED

POL-FIN-009 — Balances derived from posted entries only
  Statement : The system shall derive every account balance from POSTED journal entries only, maintaining no manually accumulated balance column.
  Pattern   : ubiquitous
  Trigger   : Compute/display a balance or report
  Rationale : Single source of truth; prevents the balance and the ledger from ever disagreeing (plan §9.1).
  Source    : plan §9.1
  Status    : CONFIRMED

POL-FIN-010 — Automatic year-end carryforward
  Statement : When a fiscal year is closed, the system shall automatically generate the new year's opening journal entry from the prior year's closing balances.
  Pattern   : event
  Trigger   : Year-end close
  Rationale : Balance-sheet accounts carry forward; result accounts close to Retained Earnings — no manual re-entry (plan §7.4).
  Source    : plan §7.4
  Status    : CONFIRMED

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
| Lookup key | Added values | Source |
|---|---|---|
| account-types | asset, liability, equity, revenue, expense | plan §1.2 |
| period-states | Open, Soft Close, Hard Close, Year-End Close | plan §7.2 |
None beyond the above — the vision document names lookup *categories* (payment
methods, accounting event types, journal types) without specific values; those are
configured post-delivery via the Lookups screen (plan §2.2, §2.3).

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| Multi-currency | Not supported in v1 | Reconsider as a FIN v2+ scope item | plan §12 |
| Multi-ledger / multi-entity / intercompany entries | Not supported in v1 | FIN v2+ | plan §12 |
| Statistical accounts | Not supported in v1 | FIN v2+ | plan §12 |
| Multi-pattern fiscal calendar | Single calendar pattern only | FIN v2+ | plan §12 |
| Attachments on entries | Not supported in v1 | FIN v2+ | plan §12 |
| Workflow / BPM engine | Never used anywhere in FIN | N/A — permanent, platform-wide | `profiles/erp.yaml → conventions.workflow_engine` |
| Business Module, Event consumer, AQ/RabbitMQ transport layer | Out of FIN's scope — each has its own separate document | N/A | plan §0, §12 |
| Account numbers in the event payload | Explicitly disallowed — would re-leak the separated responsibility | N/A — architecture constraint | plan §12 |
| Shared platform lookups (`MDL`) / shared platform RBAC (`SEC`) | FIN does not consume `MDL` lookups or `SEC` roles — owns dedicated tables instead | Confirm or reject at `prd-approval` gate | plan §2.1, §8.1 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Should FIN consume the platform's shared `MDL` lookups and `SEC` RBAC, or own dedicated, isolated equivalents? | Own dedicated, isolated equivalents — matches the vision document's explicit, repeated design intent | Recommended and adopted for this draft — confirm or reject at `prd-approval` gate | plan §2.1, §8.1 |
══════════════════════════════════════════════════════════════════
