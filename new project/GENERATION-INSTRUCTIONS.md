# Generation Instructions — Analysis order & dependency rules

```
Purpose : Tell the analysis agent the exact order to generate the analysis for the
          plans in this folder, so shared modules are analyzed before their consumers
          and no dependency is analyzed after something that needs it.
Scope   : Analysis (specification) only — not implementation. Read every plan as the
          source of truth; do not invent scope beyond it.
Folder  : "new project" — contains the plan files below plus
          `integration-notifications-fileservice.md`, extracted from the old codebase,
          documenting how to call the already-implemented Notifications and File
          Service modules if needed.
```

---

## 1. What is in this folder

**Plans to analyze (each is a standalone module):**
1. `security-module-plan-en.md` — generic Security module (authentication + hierarchical RBAC + admin dashboard).
2. `lookup-module-plan-en.md` — generic Reference-data (Lookup) module.
3. `general-accounting-system-plan-en.md` — the General Ledger (Accounting / FIN) module.

(Arabic twins `*-plan.md` are the same content; analyze from either, keep names/titles bilingual if the pipeline requires it.)

**Reference material (do NOT analyze; use only if a plan needs it):**
- `integration-notifications-fileservice.md` — extracted from the old project's real code: how to call the already-implemented **Notifications** and **File Service** modules (endpoint/entry point, request/response, auth, errors, a minimal example), from the caller's perspective only. These are ready services; consume them only where a plan explicitly says an integration is needed, and never re-specify or redesign them.

---

## 2. The dependency picture (why the order matters)

- **Security** and **Lookup** are **shared, foundational** modules. They depend on nothing here (each is generic and self-contained), and other modules consume them.
- **Accounting** is a **consumer**: it owns no security and no lookups; it registers itself into Security (as a module, with its screens/actions) and registers its lookup types into Lookup, then reads identity/permissions and reference values from them.
- **Notifications** and **File Service** are already implemented (see `integration-notifications-fileservice.md`) — optional integrations, used only on real need. Never analyzed here.

Dependency edges:
```
Security   → (depends on nothing here)   ← consumed by Accounting (and any module)
Lookup     → (depends on nothing here)   ← consumed by Accounting (and any module)
Accounting → consumes Security + Lookup  (+ optional Notifications / File Service)
```

---

## 3. Required generation order

Analyze strictly in this order:

1. **Security module** first.
   Rationale: every other module registers into it and is gated by it; its module/screen/action model and the identity/permission contract must exist before any consumer can reference them.

2. **Lookup module** second.
   Rationale: consumers register their lookup types and read coded values from it; its master-detail model and ownership/namespacing must exist before a consumer cites a lookup.

   (Security and Lookup are independent of each other; if the pipeline can parallelize, they may be done in parallel — but both must precede step 3.)

3. **Accounting (FIN) module** last.
   Rationale: it is a pure consumer of the two above. Its analysis must reference the already-defined Security integration (module registration, permission gating, SoD across roles) and the already-defined Lookup integration (its registered lookup types), not redefine them.

---

## 4. Rules the agent must honor across all three

1. **Consumers never redefine a shared capability.** Accounting must not specify its own users, roles, login, or lookup tables. Where it needs them, it *references* the Security / Lookup modules generated in steps 1–2.
2. **Register-as-data, not code.** A consumer joining Security (its module + screens + actions) or Lookup (its lookup types) is expressed as data registration, never as new security/lookup logic.
3. **Honor the module gate.** For any consumer screen, its access presupposes the consumer's module grant in Security; a screen permission cannot exist without its module grant.
4. **Respect each plan's explicit boundaries** (the "out of scope" section of every plan) — especially: Accounting knows nothing of the host business world; no account numbers in event payloads; the four excluded GL features (multi-currency, multi-ledger/entity, statistical accounts, multi-pattern calendar, attachments) stay excluded.
5. **Accounting's §"details the analysis agent MUST honor"** (14 points: debit=credit invariant, normal-balance sign, leaf-only posting, period gate at post time, positive-amount-with-direction, remainder line, exact linked reversal, trial balance always balances, balances recomputed not stored, opening-balance continuity, dimensions as posting identity, boundary idempotency assumed, immutable audit trail, no business meaning inside accounting) — apply every one; do not simplify any away.
6. **Optional integrations stay optional.** Use Notifications / File Service (per `integration-notifications-fileservice.md`) only where a plan calls for it; core posting/reporting must work without them.
7. **DB target is PostgreSQL** for all three modules. The legacy Oracle/ADF system is only an upstream event source, never a build target here.
8. **Read the live plans as the source of truth.** If any earlier assumption (e.g. an isolated FIN RBAC or FIN-owned lookups) conflicts with these plans, the plans win — Accounting consumes the shared modules.

---

## 5. Output expectation per module

For each module, in the order above, produce the analysis the pipeline defines (e.g. platform-summary / module-registry / business-policies → PRD → SRS, per the Factory stages), each tracing back to its plan. Do not start a consumer's analysis before its dependencies' analysis is complete.