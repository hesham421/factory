# Full Plan — General Accounting (GL) Module, Pluggable

```
Status        : Ready as input for the Factory stage (domain-profile / idea-to-brief)
Scope         : A complete, standalone General Ledger (GL) module — starts at receiving the
                canonical event, ends at the financial statements
Nature        : A generic module pluggable into ANY host system, not bound to one system
Out of scope  : The Business Module, the Event consumer, the transport layer (AQ/RabbitMQ) —
                each has its own separate document
Build         : Spring (backend) + React (frontend) on the same existing Oracle schema
Governing rule: Everything that can change = defined data, not code
                (no hardcode, no contradiction, no duplication, no exceptions)
```

---

## 0. Entry point, boundary, and pluggability

The accounting system knows nothing about the business world as entities (contracts, customers, investors...). Its single entry point: a **canonical accounting event** arriving ready from the Event consumer (out of scope).

**Pluggability into any system (generic) — a governing design constraint:**
- **Dimensions are defined as data, not code.** "Investor" here is merely an *example* of a dimension, not a dimension baked into the design. Any other host system defines its own dimensions (project, department, property, cost center...) without touching code.
- **The Event Contract is standard and generic.** Any source system emits events in the same shape; the contract is not tailored to one system's events.
- **Event types are data per host system.** The set of `event_type` values is not fixed in the engine; each host defines its own types and their rules as data.

The governing separation test: can you change any table in the host system — or replace the host system entirely — without touching one line in accounting? The answer must always remain "yes".

---

## 1. Chart of Accounts

### 1.1 Purpose
The reference structure that determines where values are recorded. Configuration, not part of the event flow.

### 1.2 Requirements
- **Hierarchical** structure: parent → branches → lowest level (leaf) is the only one that accepts direct posting; rollup accounts are for display and reporting only.
- Each account carries: account type (asset / liability / equity / revenue / expense), its nature (debit/credit), active flag, whether it accepts direct posting.
- **Dimensions (segments):** the account combination = base account + dimensions defined as data (one or more). A dimension is added/removed as data, so the module fits any host with different dimensions, and it avoids duplicating the account per dimension value.

### 1.3 Deliverables
- Chart-of-accounts management screen (hierarchical CRUD).
- Dimension definition & values screen (defined as data per host system).

---

## 2. Reference data (Lookups)

### 2.1 Decision
All accounting reference data is managed through a **single generic screen** (master-detail pattern: list type in the master, values in the detail), built on **entirely new tables belonging to accounting only**, with no link to or dependency on any generic reference table from the business world or any other system.

### 2.2 Example managed lists
Payment methods, accounting event types, account types, period states, journal types — all rows in the same generic screen, not a screen per list.

### 2.3 Deliverables
- One generic Lookups screen (master: list types / detail: values).

---

## 3. Rules Engine — the core

### 3.1 Principle
Each `event_type` has a **rule defined as data, not code**. The engine knows no accounting; it applies rules to the event's shape. All intelligence is in configuration.

### 3.2 Rule structure
Each rule maps an `event_type` to a set of **lines**; each line carries two fully separate references:

**a) Account derivation** — one or a combination of:
- Constant value (part of the combination always the same).
- Direct source from the event (a dimension arriving ready → placed in the right segment).
- Mapping set: a combination of event attributes → a segment value via lookup.

**b) Amount source** — points to a specific field in the event, or the result of an operation (percentage/remainder) built on a real field, not a written number.

**c) Direction (debit/credit)** per line.

Separating (a) from (b) is deliberate: changing the account source never touches the amount logic, and vice versa.

### 3.3 Distribution mechanism in a compound entry
When distributing an amount across several lines:
- Each line has a distribution type: percentage / fixed amount / **remainder**.
- Order: fixed first → percentages from the remaining amount (each rounded to the smallest currency unit) → **the single remainder line** takes the true difference = original amount − sum of the rest, guaranteeing exact balance and absorbing the rounding difference.
- Allowed alternative as data: route the difference to a separate "rounding difference" account.

### 3.4 Event-type rules
Each `event_type` = one rule. Adding a new type (or adapting the module to another host) = a new data rule, not code.

### 3.5 Deliverables
- Rules management screen (event_type ← lines ← account/amount/direction/distribution derivation).
- Execution engine that builds the entry from the rule + event + chart of accounts.

---

## 4. Journal sources

The system accepts entries from four sources, all ending in the same lifecycle (§5):

### 4.1 Event-generated entries
The primary path: canonical event → rules engine → entry.

### 4.2 Direct manual entries
Direct human input (adjustments, opening entry, lines not arising from an event). Goes through the same automatic validation and posting.

### 4.3 Recurring / reversing scheduled entries
- Entry templates that recur on a schedule (e.g., monthly), or auto-reverse in the next period (accruals).
- The template is defined once as data, then generates its entries automatically per schedule.

### 4.4 Allocation entries
- Distributing an account balance across several accounts/dimensions by rules defined as data.
- Broader than the within-entry distribution (§3.3): here it distributes an accumulated balance across multiple targets.

### 4.5 Deliverables
- Manual entry screen.
- Recurring/reversing templates screen.
- Allocation rules screen.

---

## 5. Journal entry lifecycle

### 5.1 The unified rule
**All entries — from any source (§4) — post directly after automatic validation, with no per-entry approval.**

```
Build entry (DRAFT)
   → Automatic validation (debits = credits + accounts leaf/active + dimension valid + period open)
   → POSTED directly (affects balances, locked against edit)
```

### 5.2 The human control point = period-close gate (not the individual entry)
- No per-entry approval (events are trusted, and the manual entry likewise posts after automatic validation).
- **The only human approval is at period close:** a period cannot be closed without a human approval that reviews its content (§7).
- **Segregation of Duties (SoD)** moves to the period level: **entry creator ≠ period-close approver** — enforced via RBAC (§8).

### 5.3 Lock after posting
A posted entry is fully locked — no edit, no delete. Any correction is via a reversing entry (§6).

### 5.4 Deliverables
- Journal entries screen (view/create/status detail).

---

## 6. Corrections

### 6.1 Decision (best practice)
A posted entry is **never edited or deleted**. Any correction = a **reversing entry** that zeroes the wrong entry's effect + a new correct entry if needed. It preserves the full audit trail and prevents any suspicion of tampering — a principle adopted in all serious systems.

### 6.2 Mechanism
- The correction is a new entry of type `VOID`/`CORRECTION`, **posted directly after automatic validation** like any entry (§5.1).
- It links by reference to the original entry (tracking the correction chain).
- If the original's period is closed, the reversal posts in the current open period.

### 6.3 Deliverables
- A "reverse entry" action from the posted-entry screen (creates a linked VOID entry, posts directly).

---

## 7. Accounting period lifecycle (fully internal control)

### 7.1 Principle
The decision and execution of opening/closing periods is **from inside accounting only** — no external system has authority over it.

### 7.2 States
- **Open:** accepts posting.
- **Soft Close:** blocks normal posting, allows authorized review/adjustments; re-openable.
- **Hard Close:** no posting after it ever; not re-openable.
- **Year-End Close.**

### 7.3 Approval gate at close
Closing a period (soft/hard) is the single human control point in the system: a period cannot be closed except by an authorized human approval (separate from the entry creator — §5.2).

### 7.4 Year-end close and carryforward (flexible and extensible)
- Balance-sheet accounts (assets/liabilities/equity) → their balances carry forward as **opening balances** for the new year.
- Result accounts (revenue/expense) → their net is closed to **Retained Earnings** and the new year starts from zero.
- **The new year's opening entry is generated automatically** from the closing balances.
- Years and periods are defined as data, not code; adding a year = new data.

### 7.5 Deliverables
- Fiscal periods & years management screen (open/close/year-end + close approval).
- Year-end close procedure generating the closing and opening entries.

---

## 8. Security & permissions (separate RBAC)

### 8.1 Principle
A **fully independent RBAC** system, with users belonging to the accounting system only — not shared with any other system. An access layer separate from accounting logic.

### 8.2 Requirements
- Secure, simple login.
- Roles assigned permissions on screens and actions.
- **Enforces SoD:** the entry-creator role is separate from the period-close-approver role (§5.2 / §7.3).
- Adding a role/permission = data, not code.

### 8.3 Deliverables
- Screens: login, user management, roles & permissions management.

---

## 9. Balances & reporting

### 9.1 Principle
All balances are **derived from posted (POSTED) entries only** — no manually accumulated balance column.

### 9.2 Core reports
- Account Ledger for any account/dimension over a period.
- Trial Balance.
- Financial statements: Balance Sheet, Income Statement — as a presentation layer over the same entries.
- Reports by dimension (e.g., a statement per dimension value) without duplicated accounts.

### 9.3 Drill-down
The ability to go from a financial-statement line → trial balance → account ledger → the original entry → its reference in the event. A standard audit element.

### 9.4 Deliverables
- Screens/reports: account ledger, trial balance, balance sheet, income statement, dimension reports, with drill-down.

---

## 10. Cross-cutting design principles

1. **No hardcode:** the tree, rules, event types, dimensions, period types, years, roles — all data.
2. **No contradiction:** a single source of truth (balance from entries, no duplicated column).
3. **No duplication:** one rule per event type; one lookups screen.
4. **Total separation:** accounting knows nothing of the host system, neither reads from nor writes to it.
5. **Pluggability:** the module is generic — fits any host by changing data (dimensions, event types, rules), not code.

---

## 11. Screen inventory (for initial sizing)

| # | Screen | Group |
|---|---|---|
| 1 | Chart of accounts | Setup |
| 2 | Dimension definition & values | Setup |
| 3 | Generic Lookups (master-detail) | Setup |
| 4 | Engine rules | Setup |
| 5 | Recurring/reversing templates | Setup |
| 6 | Allocation rules | Setup |
| 7 | Journal entries (view + manual entry) | Operations |
| 8 | Reverse/correct entry (action within the entry screen) | Operations |
| 9 | Fiscal periods & years + close approval + year-end close | Control |
| 10 | Account ledger | Reports |
| 11 | Trial balance | Reports |
| 12 | Balance sheet | Reports |
| 13 | Income statement | Reports |
| 14 | Dimension reports | Reports |
| 15 | Login | Security |
| 16 | Users | Security |
| 17 | Roles & permissions | Security |

---

## 12. Explicit boundaries (out of scope)

- The Business Module and any business logic.
- The Event consumer, idempotency logic, the AQ/RabbitMQ layer.
- Any read/write from or to the host system's tables.
- Passing account numbers within the event payload (re-leaks the separated responsibility).
- Multi-currency, multi-ledger/entity and intercompany entries, statistical accounts, multi-pattern calendar, attachments — excluded by explicit decision to avoid complexity.
