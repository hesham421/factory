# Full Plan — Generic Reference-Data (Lookup) Module, Shared

```
Status        : Ready as input for the Factory stage (domain-profile / idea-to-brief)
Scope         : A standalone, GENERIC reference-data (lookup) module — one central,
                governed hub for all coded value lists, consumed by any module
Nature        : A shared platform capability; not owned by or specific to any one module
Build         : Spring (backend) + React (frontend) on PostgreSQL
Governing rule: Everything that can change = defined data, not code
Related        : Every module (Accounting included) CONSUMES this module for its lookups
```

---

## 1. Technology stack
- **Backend:** Spring. **Frontend:** React. **Database:** **PostgreSQL**.

---

## 2. Principle & boundary (why central, per best practice)

- **One governed hub for reference data.** The recommended pattern in reference-data / master-data management is to centralize coded value lists in a single authoritative store rather than let each module keep its own copies — scattered copies drift and the same concept ends up with different values across modules.
- **Generic master-detail.** A lookup is a *type* (master) + its *values* (detail). Any module registers its lists here **as data**; the module knows nothing hardcoded about any consumer's domain.
- **Central storage & screen, module-owned meaning.** Storage and the management screen are central; the *meaning* of a domain-specific list (e.g. accounting event types) still belongs to the module that defines it — centralization is of the mechanism, not of semantic ownership. This removes duplication without stripping a module's authority over its own lists' meaning.

---

## 3. Requirements

- **One generic master-detail screen** manages every list: pick a lookup type in the master, manage its values in the detail — the same screen for every list, no screen per list.
- **Namespacing by owner** — each lookup type records the module that owns its meaning, so two modules can't collide on a key and each module can find its own lists.
- **Consumers read and (for their own lists) manage** values through this module; they store no lookup tables of their own.
- Standard value fields: code, labels (bilingual), sort order, active flag.
- Adding a new list or value = data, not code.

---

## 4. Integration contract (how modules consume it)

A consumer (Accounting or any other) owns **no lookup tables**. It:
- registers its lookup types (with itself as owner) here as data;
- reads values from this module wherever it needs a coded value;
- manages its own lists' values through the shared screen (subject to Security grants).
This is the only coupling; the consumer's business logic stays independent.

---

## 5. Available platform resources (use only on real need)
**Notifications** and **File Service** are ready modules, used only when genuinely needed — not dependencies.

---

## 6. Cross-cutting design principles
1. **No hardcode:** every list and value is data.
2. **No duplication:** one hub platform-wide; no module keeps its own lookup tables.
3. **No contradiction:** one authoritative value per coded concept.
4. **Generic:** one master-detail mechanism serves every module.

---

## 7. Screen inventory
| # | Screen | Group |
|---|---|---|
| 1 | Generic Lookups (master-detail, all lists) | Reference data |
| 2 | Lookup-type registry (per owning module) | Reference data |

---

## 8. Explicit boundaries (out of scope)
- Any module-specific business logic.
- Any module keeping its own lookup tables — forbidden; all reference data is here.
- Security/RBAC — a separate shared module (`security-module-plan-en.md`).
- Notifications and File Service — ready modules, used only on real need.
