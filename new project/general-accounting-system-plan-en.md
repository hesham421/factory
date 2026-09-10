# Full Plan — General Accounting (GL) Module, Pluggable

```
Status        : Ready as input for the Factory stage (domain-profile / idea-to-brief)
Scope         : A complete, standalone General Ledger (GL) module — starts at receiving the
                canonical event, ends at the financial statements
Nature        : A generic module pluggable into ANY host system, not bound to one system
Out of scope  : The Business Module, the Event consumer, the transport layer (AQ/RabbitMQ),
                the Security Module, and the Lookup Module — each has its own separate document
Governing rule: Everything that can change = defined data, not code
                (no hardcode, no contradiction, no duplication, no exceptions)
```

---

## 1. Technology stack

- **Backend:** Spring.
- **Frontend:** React.
- **Database:** **PostgreSQL** (target for the new build). The legacy Oracle/ADF system remains only an upstream source of canonical events (via AQ); all new modules, this one included, are built on PostgreSQL — not on the legacy Oracle schema.
- The stack is fixed for this build; it does not affect the data-driven design (§4 onward) — a different host could rebuild the same design on a different stack without changing the accounting logic itself.

---

## 2. Security — consumed from the shared Security Module (FIN owns none)

### 2.1 Principle
Accounting owns **no** authentication and **no** RBAC of its own. All identity and permissions come from the platform's separate, **generic Security Module** (its own plan: `security-module-plan-en.md`) — a shared capability with hierarchical RBAC (Module → Screen → Action). FIN is registered there as a **module**; if a role isn't granted the FIN module, none of its screens appear at all (module gate).

### 2.2 What FIN does
- **Registers its own screens and actions** (VIEW/CREATE/UPDATE/DELETE + custom actions such as *reverse entry* and *approve period close*) into the Security Module **as data**, so they can be granted to roles there.
- **Gates every screen/action** on the permissions issued by the Security Module.
- **Requires Segregation of Duties** by declaring the entry-creator permission and the period-close-approver permission be held by **distinct roles/users** (§8.2 / §10.3) — enforced through the shared RBAC, not a FIN-local mechanism.
- Uses the shared **Login / Sign-up / Forgot-password** and the **dynamic per-user menu** from the Security Module — FIN builds none of these.

### 2.3 Available ready platform services (optional)
**Notifications** and **File Service** are already implemented and available at build time. FIN **may** integrate with them **only when genuinely needed** (e.g., notify a Financial Controller a period awaits close approval; export a statement as a file) — optional integration points, never a hard dependency; FIN's posting and reporting keep working if skipped.

### 2.4 Deliverables
- No security screens of its own. Only: data registration of FIN's screens/actions/permissions into the Security Module, and permission checks on every FIN screen/action.

---

## 3. Entry point, boundary, and pluggability

The accounting system knows nothing about the business world as entities (contracts, customers, investors...). Its single entry point: a **canonical accounting event** arriving ready from the Event consumer (out of scope).

**Pluggability into any system (generic) — a governing design constraint:**
- **Dimensions are defined as data, not code.** "Investor" here is merely an *example* of a dimension. Any other host defines its own dimensions (project, department, property, cost center...) without touching code.
- **The Event Contract is standard and generic.** Any source system emits events in the same shape.
- **Event types are data per host system.** The set of `event_type` values is not fixed in the engine; each host defines its own types and rules as data.

The governing separation test: can you change any table in the host system — or replace the host entirely — without touching one line in accounting? The answer must always remain "yes".

---

## 4. Chart of Accounts

### 4.1 Purpose
The reference structure that determines where values are recorded. Configuration, not part of the event flow.

### 4.2 Requirements
- **Hierarchical** structure: parent → branches → leaf; only a leaf accepts direct posting; rollup accounts are display/reporting only.
- Each account carries: account type (asset / liability / equity / revenue / expense), nature (debit/credit), active flag, whether it accepts direct posting.
- **Dimensions (segments):** account combination = base account + dimensions defined as data. A dimension is added/removed as data; avoids duplicating the account per dimension value.

### 4.3 Deliverables
- Chart-of-accounts management screen (hierarchical CRUD).
- Dimension definition & values screen.

---

## 5. Reference data (Lookups) — consumed from the shared Lookup Module

### 5.1 Decision
FIN owns **no** lookup tables and **no** lookup screen of its own. All accounting reference lists live in the platform's separate, **generic Lookup Module** (its own plan: `lookup-module-plan-en.md`), the single governed hub for coded value lists. This replaces the earlier "FIN-isolated lookups" decision — central reference data is the recommended practice and removes cross-module value drift.

### 5.2 What FIN does
- **Registers its lookup types** (payment methods, accounting event types, account types, period states, journal types) in the Lookup Module **as data, with FIN as the owning module** — central storage and screen, FIN-owned meaning.
- **Reads values** from the Lookup Module wherever it needs a coded value; stores none locally.

### 5.3 Deliverables
- No lookup screen of its own — only the registration of FIN's lookup types into the shared Lookup Module.

---

## 6. Rules Engine — the core

### 6.1 Principle
Each `event_type` has a **rule defined as data, not code**. The engine knows no accounting; it applies rules to the event's shape.

### 6.2 Rule structure
Each rule maps an `event_type` to **lines**; each line carries two fully separate references:
- **a) Account derivation:** constant / direct from the event (a ready dimension → its segment) / mapping set (event attributes → segment value via lookup).
- **b) Amount source:** a specific event field, or an operation (percentage/remainder) on a real field — never a written number.
- **c) Direction (debit/credit)** per line.

Separating (a) from (b) is deliberate: changing the account source never touches amount logic, and vice versa.

### 6.3 Distribution in a compound entry
- Each line's distribution type: percentage / fixed / **remainder**.
- Order: fixed first → percentages from the remainder (each rounded to smallest currency unit) → **the single remainder line** takes the true difference = original − sum of the rest, guaranteeing exact balance and absorbing rounding.
- Alternative as data: route the difference to a separate "rounding difference" account.

### 6.4 Event-type rules
Each `event_type` = one rule. New type (or adapting to another host) = new data rule, not code.

### 6.5 Deliverables
- Rules management screen.
- Execution engine building the entry from rule + event + chart of accounts.

---

## 7. Journal sources

Four sources, all ending in the same lifecycle (§8):
- **7.1 Event-generated:** canonical event → engine → entry.
- **7.2 Direct manual:** adjustments, opening entry, lines with no source event; same validation and posting.
- **7.3 Recurring / reversing scheduled:** templates that recur on a schedule or auto-reverse next period (accruals); template defined once as data.
- **7.4 Allocations:** distribute an accumulated account balance across several accounts/dimensions by data-defined rules (broader than §6.3's within-entry distribution).

### 7.5 Deliverables
- Manual entry screen; recurring/reversing templates screen; allocation rules screen.

---

## 8. Journal entry lifecycle

### 8.1 The unified rule
**All entries — from any source (§7) — post directly after automatic validation, with no per-entry approval.**

```
Build entry (DRAFT)
   → Automatic validation (debits = credits + accounts leaf/active + dimension valid + period open)
   → POSTED directly (affects balances, locked against edit)
```

### 8.2 Human control point = period-close gate (not the individual entry)
- No per-entry approval.
- **The only human approval is at period close** (§10).
- **SoD** moves to the period level: **entry creator ≠ period-close approver** — enforced through the shared Security Module (§2).

### 8.3 Lock after posting
A posted entry is fully locked — no edit, no delete. Correction only by reversal (§9).

### 8.4 Deliverables
- Journal entries screen (view/create/status detail).

---

## 9. Corrections

- A posted entry is **never edited or deleted**. Correction = a **reversing entry** zeroing the wrong entry + a new correct entry if needed; preserves the full audit trail.
- The reversal is a new `VOID`/`CORRECTION` entry, **posted directly after automatic validation**, linked by reference to the original. If the original's period is closed, the reversal posts in the current open period.
- **Deliverable:** a "reverse entry" action on the posted-entry screen.

---

## 10. Accounting period lifecycle (fully internal control)

### 10.1 Principle
Opening/closing periods is controlled **from inside accounting only** — no external system has authority over it.

### 10.2 States
- **Open** → accepts posting.
- **Soft Close** → blocks normal posting, allows authorized adjustments; re-openable.
- **Hard Close** → no posting after it; not re-openable.
- **Year-End Close.**

### 10.3 Approval gate at close
Closing a period is the single human control point: only an authorized approver (distinct from the entry creator — §8.2, via §2) may close it.

### 10.4 Year-end close and carryforward
- Balance-sheet accounts (assets/liabilities/equity) → balances carry forward as **opening balances**.
- Result accounts (revenue/expense) → net closed to **Retained Earnings**; new year starts at zero.
- **New year's opening entry generated automatically** from closing balances.
- Years and periods are data; adding a year = new data.

### 10.5 Deliverables
- Fiscal periods & years management screen (open/close/year-end + close approval).
- Year-end close procedure generating closing and opening entries.

---

## 11. Balances & reporting

- All balances **derived from POSTED entries only** — no manually accumulated balance column.
- Core reports: Account Ledger, Trial Balance, Balance Sheet, Income Statement, and per-dimension reports (without duplicated accounts).
- **Drill-down:** financial-statement line → trial balance → account ledger → original entry → its event reference.
- **Deliverables:** ledger, trial balance, balance sheet, income statement, dimension reports, with drill-down.

---

## 12. Accounting details the analysis agent MUST honor

Precise points the writing agent must not miss or simplify away when producing the analysis:

1. **Debit=Credit is an absolute invariant.** No entry reaches POSTED unless total debits equal total credits to the smallest currency unit — including after any rounding in §6.3.
2. **Normal balance sign per account type.** Assets/expenses are debit-natured; liabilities/equity/revenue are credit-natured. Reports and the trial balance must present each side correctly; a balance's sign follows the account's nature, not the raw arithmetic only.
3. **Posting only to leaf, active, direct-postable accounts.** Rollup/parent accounts never receive postings; an inactive account never receives a new posting.
4. **Period gating is checked at post time, not build time.** An entry may only post into an Open period; if the period changed state between build and post, revalidate.
5. **Amounts are always positive; direction carries the sign.** No negative amounts on a line — a reduction is the opposite direction, not a negative number (mirrors the canonical event carrying a positive amount + a type).
6. **The remainder line is the balancing guarantor.** In any compound/percentage distribution exactly one remainder line absorbs the rounding difference; it is never itself computed as a percentage.
7. **Reversal is exact and linked.** A reversing entry mirrors the original line-for-line with opposite directions and equal amounts, and stores a bidirectional link (original ↔ reversal). It never partially reverses unless a partial correction is explicitly modeled as its own entry.
8. **Trial balance must always balance.** Sum of all debit balances = sum of all credit balances at any point in time; a report that doesn't balance signals a posting-integrity defect, not a display bug.
9. **Balances are recomputed, never stored-and-trusted.** Every balance/report reads POSTED lines; there is no cached balance column to fall out of sync (the exact defect of the legacy design being replaced).
10. **Opening balances continuity.** The new fiscal year's opening balances must equal the prior year's closing balances for balance-sheet accounts, and result accounts must open at zero after closing to Retained Earnings; the generated opening entry must itself be balanced.
11. **Dimensions are part of the posting identity, not decoration.** A balance is meaningful per account **and** per dimension combination; ledger and dimension reports must aggregate by the full combination, never by base account only when a dimension is in play.
12. **Idempotency at the boundary is assumed, not re-implemented.** The engine treats each canonical event as already de-duplicated by the (out-of-scope) consumer; it must not silently create a second entry for the same event reference — a repeated event reference is a defect to reject, not to post twice.
13. **Audit trail is immutable and complete.** Every posted entry retains created-by/at; nothing is hard-deleted; every reported figure is traceable down to its entry and source-event reference (§11 drill-down).
14. **No business meaning inside accounting.** The agent must not introduce any host-specific logic (e.g., "if contract… then…"); all behavior derives from account/dimension/rule/event data only.

---

## 13. Cross-cutting design principles

1. **No hardcode:** tree, rules, event types, dimensions, period types, years — all data (security roles/permissions live in the Security Module, also data).
2. **No contradiction:** single source of truth (balance from entries, no duplicated column).
3. **No duplication:** one rule per event type; lookups in the shared Lookup Module; security in the shared Security Module; nothing FIN-local for either.
4. **Total separation:** accounting knows nothing of the host system; neither reads from nor writes to it.
5. **Pluggability:** generic — fits any host by changing data, not code.

---

## 14. Screen inventory (for initial sizing)

Security screens (login, sign-up, forgot-password, users, roles, menu) belong to the shared Security Module; the generic Lookups screen belongs to the shared Lookup Module. Neither is listed here.

| # | Screen | Group |
|---|---|---|
| 1 | Chart of accounts | Setup |
| 2 | Dimension definition & values | Setup |
| 3 | Engine rules | Setup |
| 4 | Recurring/reversing templates | Setup |
| 5 | Allocation rules | Setup |
| 6 | Journal entries (view + manual entry) | Operations |
| 7 | Reverse/correct entry (action within the entry screen) | Operations |
| 8 | Fiscal periods & years + close approval + year-end close | Control |
| 9 | Account ledger | Reports |
| 10 | Trial balance | Reports |
| 11 | Balance sheet | Reports |
| 12 | Income statement | Reports |
| 13 | Dimension reports | Reports |

---

## 15. Explicit boundaries (out of scope)

- The Business Module and any business logic.
- The Event consumer, idempotency logic, the AQ/RabbitMQ layer.
- **The Security Module** (authentication + hierarchical RBAC) — separate plan; FIN only consumes it.
- **The Lookup Module** (shared reference data) — separate plan; FIN only consumes it.
- Notifications and File Service — ready platform modules, used only on real need.
- Any read/write from or to the host system's tables.
- Passing account numbers within the event payload.
- Multi-currency, multi-ledger/entity and intercompany entries, statistical accounts, multi-pattern calendar, attachments — excluded by explicit decision.
