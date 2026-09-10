# Full Plan — Generic Security Module (Authentication + Hierarchical RBAC), Shared

```
Status        : Ready as input for the Factory stage (domain-profile / idea-to-brief)
Scope         : A standalone, GENERIC security module — authentication + hierarchical
                role-based access control (Module → Screen → Action) — consumed by any
                module in the platform (Accounting and others)
Nature        : Not owned by or specific to any one module; a shared platform capability
Build         : Spring (backend) + React (frontend) on PostgreSQL
Governing rule: Everything that can change = defined data, not code
Related        : Every module CONSUMES this module; no module owns any security of its own
```

---

## 1. Technology stack

- **Backend:** Spring.
- **Frontend:** React.
- **Database:** **PostgreSQL** (target for the new build). The legacy Oracle/ADF system remains only an upstream event source; all new modules, this one included, are built on PostgreSQL.

---

## 2. Principle & boundary

- **One security system for the whole platform.** No module carries its own users, roles, or login. Every module (Accounting included) authenticates and authorizes **through** this module.
- **Generic, not module-specific.** Modules, their screens, actions, roles and permissions are registered here **as data** — the security module knows nothing hardcoded about any consumer.
- **Two concerns cleanly separated:**
  - **Authentication (identity):** who the user is — login, sign-up, password reset, session/token issuance.
  - **Authorization (RBAC):** what the identified user may do — via a hierarchy (§4).

---

## 3. Authentication

- **Login** — secure sign-in issuing a session/token consuming modules trust.
- **Sign-up** — self-registration (a pending user holds no permissions until granted).
- **Forgot / reset password** — secure self-service reset.
- Secure password storage; the client never receives a hash.
- **Deliverables:** Login, Sign-up, Forgot/Reset password screens.

---

## 4. Hierarchical RBAC — Module → Screen → Action

### 4.1 The three levels (the core improvement)
Authorization is a strict hierarchy, granted to a **role**:

1. **Module grant (top).** A role is first granted the *modules* it may reach at all (e.g. Accounting, Sales). This is an **access gate**, evaluated first.
2. **Screen grant (middle).** Within a granted module only, the role is granted specific screens.
3. **Action grant (bottom).** On a granted screen, the specific actions VIEW / CREATE / UPDATE / DELETE (and custom actions such as *reverse entry*, *approve period close*).

### 4.2 The module gate — the key rule
- **If a role does not hold a module, nothing under it exists for that user:** its screens never appear in the menu, are never evaluated, and are unreachable even by direct URL. Module-level access is checked **before** any screen/action evaluation — a user without the module is blocked up front, not merely hidden.
- **Structural integrity (no contradiction):** a screen or action grant cannot be assigned for a module the role does not hold. Screen/action permissions only exist *inside* a granted module. This makes an orphaned screen grant impossible by construction.

### 4.3 Registration as data
- Every consuming module registers, **as data**: itself (a module entry), its screens, and its actions. Granting them to roles is then pure data.
- **Adding a whole new module to the platform** (as Accounting will be) = registering a new module + its screens as data, then granting it to roles — **no change to security code**. Fully consistent with "generic, data not code".

### 4.4 Users & roles
- **Users:** add/edit/activate/deactivate; assign one or more roles (effective permissions = union).
- **Roles:** full control — create/edit/deactivate, and assign module/screen/action grants at all three levels.
- **Segregation of Duties for consumers:** because grants live here, a consumer (e.g. Accounting) can require two conflicting actions be held by distinct roles/users (entry-creator ≠ period-close-approver).

### 4.5 Deliverables
- Screens: Users, Roles & Permissions (three-level grant editor), Module/Screen/Action registry.

---

## 5. Admin dashboard (recommended baseline)

A landing dashboard for security administrators, composed of the widgets standard to user-management / security admin consoles (per RBAC-admin and session-management best practice). Every widget is itself gated by permissions and respects the module gate.

### 5.1 Recommended widgets
- **Users overview** — total, active, inactive/disabled, pending sign-ups awaiting activation.
- **Failed logins** — count over the last 24h and a short trend, to surface brute-force or compromised-account patterns early.
- **Active sessions** — currently signed-in users, with the ability (for an authorized admin) to force-terminate a session.
- **Recent activity / audit feed** — latest logins, logouts, password resets, role/permission changes — searchable, with a link to the full audit log.
- **Roles & permissions summary** — number of roles, privileged roles, and users per role (spotting over-privileged accounts).
- **Onboarding funnel** — pending invitations / sign-ups, and stalled activations.

### 5.2 Principles
- Every figure is **derived** (queried live), not a stored counter — same single-source-of-truth discipline used across the platform.
- Every widget is **permission-gated**; an admin sees only the widgets their role grants.
- The activity feed is the visible surface of an **immutable audit log** (logins, failed logins, role changes, resets) — an audit trail is a security requirement, not a nicety.

### 5.3 Deliverables
- Admin dashboard screen; audit-log screen (searchable/filterable, CSV export); active-sessions management.

---

## 6. Dynamic menu — two levels, permission-driven

- The menu is built **per user** from effective grants, in **two tiers**: only **granted modules** appear as top-level entries, and under each only its **granted screens**.
- A module the user's roles don't hold is **absent entirely** — not greyed out, not present.
- Menu structure (modules, grouping, screen order) is **data** registered per module, never hardcoded.
- **Deliverable:** dynamic two-tier menu.

---

## 7. Integration contract (how modules consume it)

A consumer owns **no users, no roles, no login, no lookups-of-its-own-security**. It:
- relies on this module to authenticate and to issue identity + the effective Module/Screen/Action grants;
- registers its module, screens and actions here as data;
- gates its own screens/actions on the grants issued here, honoring the module gate first.
This is the only coupling; the consumer's business logic stays independent.

---

## 8. Available platform resources (use only on real need)

**Notifications** and **File Service** are implemented, ready modules. This module or any consumer MAY use them only when genuinely needed (e.g. a reset-password message via Notifications; a user avatar via File Service) — resources, not mandatory dependencies.

---

## 9. Cross-cutting design principles

1. **No hardcode:** modules, screens, actions, users, roles, menu — all data.
2. **No duplication:** one security system platform-wide.
3. **Generic:** knows nothing module-specific; each consumer registers itself as data.
4. **Separation of concerns:** authentication distinct from authorization.
5. **Module gate first:** coarse module access precedes fine screen/action checks.

---

## 10. Screen inventory (for initial sizing)

| # | Screen | Group |
|---|---|---|
| 1 | Login | Authentication |
| 2 | Sign-up | Authentication |
| 3 | Forgot / reset password | Authentication |
| 4 | Users | Authorization |
| 5 | Roles & permissions (3-level grant editor) | Authorization |
| 6 | Module / screen / action registry | Authorization |
| 7 | Admin dashboard | Monitoring |
| 8 | Audit log (searchable, CSV export) | Monitoring |
| 9 | Active sessions management | Monitoring |
| 10 | Dynamic two-tier menu (rendered per user) | Navigation |

---

## 11. Explicit boundaries (out of scope)

- Any module-specific business logic.
- Any module owning its own users/roles/login — forbidden.
- Reference data / lookups — a **separate** shared module (`lookup-module-plan-en.md`), not this one.
- Notifications and File Service — ready modules, used only on real need.
