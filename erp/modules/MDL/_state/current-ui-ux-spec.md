# UI / UX SPEC — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Stage : P3.2 (Part A — UX design)
Screens: 2 — SCR-MDL-001..002 · UXD : 1 — UXD-MDL-001 (the owner module, owned by SEC)
Fields : copied from SRS A3 per owning ENT, reconciled against the published DTOs
ADRs   : ADR-MDL-001..007 (all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

كل كتلة أدناه تصف شاشة واحدة: حقولها وصلاحياتها منسوخة من SRS بلا إضافة ولا حذف، ونمط
الحاوية مقرَّر هنا وفق §A.4. «نيّة التصميم» اقتراح مُعلَّم بوضوح ولا يُقرأ كقاعدة.

Each block below is one screen. Fields and permissions are copied from the SRS; the container
pattern is decided here; `Design intent` is a clearly marked proposal, never a rule.

**Error states** are stated generically per §A.3; the catalog codes and their routing belong to
Part B (`frontend-execution-plan-mdl.md` → F2).

**No lookup of MDL's own.** SRS §A6 records it: MDL introduces no domain-specific coded list,
because it *is* the mechanism every other module's lists run on. So no field on either screen
below is a lookup-backed code, and the `UXD-*` this module mints is not a lookup dependency —
it is the owner-module field, whose valid set the security module owns.

---

## CROSS-MODULE DISPLAY DEPENDENCIES — UXD-MDL-001

### UXD-MDL-001 — الوحدة المالكة / Owner module
Traces      : REQ-MDL-002, AC-MDL-002, REQ-MDL-013, AC-MDL-013
Owner       : SEC — `ModuleRegistry` (ENT-SEC-004), the authoritative list of registered
              modules · resolved through `API-SEC-021`
              (`POST /api/v1/sec/registry/search`, `registry-exec-be-sec.md`)
Screens     : SCR-MDL-001 (the owner select on the type form, the owner filter, and the owner
              column) · SCR-MDL-002 (the group heading every type is listed under)
Field       : `ENT-MDL-001.ownerModuleCode`
Display     : MDL stores and sends the module **code**; the set of valid codes, and any label
              shown beside one, come from the security module's registry. MDL owns no module
              list and holds no copy of one
Why it is a UXD and not a lookup : SRS §A8 records `ModuleRegistry` as the one entity MDL
              consumes, through XM-MDL-001 (SOFT-READ, application layer). RULE-MDL-001 refuses
              a type whose owner module has no registry row, so the field's valid set is
              literally another module's data — §A.5's definition exactly. It is not
              `ACCOUNT_TYPE`-style lookup data, and it is not read through API-MDL-011
Behaviour   : the control is a **select** over registered module codes, never free text — a
              free-text field would let a user type a code the server is certain to refuse when
              the valid set is readable (ADR-MDL-004). One shared hook, long-lived cache,
              serving both screens. If the registry read is unreachable the select renders
              empty and the create affordance says so; no module code is invented and no
              fallback to free text is offered

`frontend-execution-plan-mdl.md` cites `UXD-MDL-001` and never the foreign path or the foreign
API id: C9.5 requires every `API-*` cited in that plan to be defined in MDL's own api-docs, and
another module's id is by construction not. The endpoint is named here, once, where the
dependency is defined.

The same applies to the screen gate: a caller's effective menu is the security module's to
serve, and MDL publishes no permission-read endpoint. That is an authorization gate, not a
displayed field — no screen renders its content as data — so it is recorded in the plan's
SEC-FE phase rather than minted here. §A.5 mints on a displayed field.

---

## SCR-MDL-001 — اللوكبات العامة / Generic Lookups        traces=REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,UXD-MDL-001
Traces            : REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,REQ-MDL-010,AC-MDL-001,AC-MDL-002,AC-MDL-003,AC-MDL-004,AC-MDL-005,AC-MDL-006,AC-MDL-007,AC-MDL-008,AC-MDL-009,AC-MDL-010,UXD-MDL-001
UI pattern        : header + repeating lines — SRS SCR-REQ-MDL-001 B1 "رئيسي (أنواع) + تفصيلي
                    (قيم) قابل لإعادة الترتيب" (master types + reorderable detail values)
Container pattern : TREE_MASTER_DETAIL (§A.4 rule 1 — a lookup type and its values are
                    parent–child data; the type list beside the selected type's values, with
                    the entry form permanently visible in the detail pane)
Sub-views         : Search (the type list) · Detail (that type's values, with their own search
                    and entry) · Entry (the type form, and the value form) — all under this ONE
                    SCR, per the composite-screen rule
Fields shown      : from ENT-MDL-001 (type) —
                    lookupTypePk — معرّف نوع اللوكب / LookupType id (read-only, system, not
                    rendered as a field) ·
                    key — المفتاح / Key (required; editable on create, **read-only on edit** —
                    RULE-MDL-003, and `LookupTypeUpdateRequest` does not carry it) ·
                    ownerModuleCode — رمز الوحدة المالكة / Owner module code (required;
                    editable on create, read-only on edit — not in the update request; a select
                    over registered modules, UXD-MDL-001) ·
                    nameAr — الاسم (عربي) / Name (Arabic) (required, editable) ·
                    nameEn — الاسم (إنجليزي) / Name (English) (required, editable) ·
                    isActiveFl — نشط / Active (read-only — changed only by the deactivate
                    affordance, API-MDL-004; ADR-MDL-006) ·
                    createdBy, createdAt, updatedBy, updatedAt — audit fields (read-only)
                    from ENT-MDL-002 (value) —
                    lookupValuePk — معرّف قيمة اللوكب / LookupValue id (read-only, system) ·
                    lookupTypeId — نوع اللوكب / Lookup type (read-only — taken from the
                    selected parent, never typed) ·
                    code — الرمز / Code (required; editable on create, **read-only on edit** —
                    `LookupValueUpdateRequest` does not carry it; unique within the type —
                    RULE-MDL-002) ·
                    nameAr — الاسم (عربي) / Name (Arabic) (required, editable) ·
                    nameEn — الاسم (إنجليزي) / Name (English) (required, editable) ·
                    sortOrder — ترتيب العرض / Sort order (required, editable — and also what
                    the drag-to-reorder gesture writes, through API-MDL-009) ·
                    isActiveFl — نشط / Active (read-only — changed only by the deactivate
                    affordance, API-MDL-008; SRS B3 lists it as an input and no write DTO
                    accepts it — ADR-MDL-006) ·
                    audit fields (read-only)
                    Search filters, per SRS B2: master — key (LIKE), ownerModuleCode (EXACT),
                    isActiveFl (EXACT); detail — code (LIKE). Each corresponds to a result
                    column.
Permissions       : MDL_LOOKUPS — VIEW (both lists), CREATE (a type, and a value under it),
                    UPDATE (edit either level, and reorder the values), DELETE (deactivate at
                    either level — the SRS Access summary's DELETE column is the deactivate,
                    and no hard delete exists). Names as the backend declares them:
                    `PERM_MDL_LOOKUPS_VIEW`, `PERM_MDL_LOOKUPS_CREATE`,
                    `PERM_MDL_LOOKUPS_UPDATE`, `PERM_MDL_LOOKUPS_DELETE`. Reference only —
                    enforcement is the server's. The screen-level grant is the whole
                    granularity: per-type permissions are an explicit SRS scope exception
Cross-module data : ownerModuleCode → UXD-MDL-001 (SEC)
States            : empty (no type matches the filters — distinguished from a platform with no
                    type registered at all, which the empty state names as the first thing to
                    create; and separately, a type with no values yet) · loading (the two panes
                    load independently) · error (generic here; catalog codes and their routing
                    are Part B's) · offline — the SRS states no offline behaviour, so none is
                    specified
Design intent     : PROPOSAL — the values are the working surface, so the selected type's
                    values fill the detail pane immediately rather than behind a second click,
                    and the type list stays visible so a manager moving between lists never
                    loses the set. The key sits first on the type form with its immutability
                    stated beside it rather than discovered on edit. Inactive values stay
                    visible in the detail pane, marked — a manager needs to see what consumers
                    no longer receive, which is exactly what the consumer read hides.
                    Deactivate confirms at both levels and names the consequence in the SRS's
                    own terms: consumer reads stop returning the row (RULE-MDL-004 for a type,
                    REQ-MDL-009 for a value), and there is no activate affordance to undo it
                    (ADR-MDL-005). Reordering is a drag on the value rows, submitted as one
                    ordered list rather than as a per-row edit.
Mockup            : not produced this run (optional per §A.7)

---

## SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner   traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,UXD-MDL-001
Traces            : REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,UXD-MDL-001
UI pattern        : true hierarchy (parent/child) — SRS SCR-REQ-MDL-002 B1 "وحدة مالكة →
                    أنواعها" (owner module → its types)
Container pattern : FULL_PAGE (no entry sub-view — ADR-MDL-003; the screen is a read-only
                    browse, so §A.4's decision order, which chooses where a form lives, has
                    nothing to place. The hierarchy is rendered as the grouped list the
                    endpoint returns)
Sub-views         : none — a single grouped browse (SRS B3 "read-only browse; no create/update
                    here")
Fields shown      : the group, from the response —
                    ownerModuleCode — رمز الوحدة المالكة / Owner module code (the group
                    heading; UXD-MDL-001)
                    per type in the group, from ENT-MDL-001 —
                    lookupTypePk (read-only, system, not rendered as a field) ·
                    key — المفتاح / Key (read-only) ·
                    nameAr — الاسم (عربي) / Name (Arabic) (read-only) ·
                    nameEn — الاسم (إنجليزي) / Name (English) (read-only) ·
                    isActiveFl — نشط / Active (read-only) ·
                    audit fields (read-only)
                    Search filters, per SRS B2: ownerModuleCode (EXACT), key (LIKE) — both
                    correspond to result columns. There is no paging: the endpoint takes
                    filters alone and returns the whole grouped set.
                    All fields are read-only: this screen writes nothing.
Permissions       : MDL_TYPE_REGISTRY — VIEW only (`PERM_MDL_TYPE_REGISTRY_VIEW`). The SRS
                    Access summary gives this screen no CREATE, UPDATE or DELETE, which is the
                    same statement as B3's "management happens on SCR-REQ-MDL-001"
Cross-module data : ownerModuleCode → UXD-MDL-001 (SEC) — here it is the grouping itself, not
                    a field of a form
States            : empty (no type matches the filters — distinguished from a platform where no
                    module has registered a type yet) · loading · error (generic) · offline —
                    not specified
Design intent     : PROPOSAL — the grouping is the screen, so each owner module is a heading
                    with its types beneath it and the count of types beside it; a reader's
                    first question is which module registered what. Every type row links to
                    SCR-MDL-001 with that type selected, because reviewing and managing are
                    two steps of one task and this screen deliberately does neither half of the
                    second. The filters live in the route's search params so a narrowed
                    registry view is shareable, which is the only state this screen has.
                    The consumer read (REQ-MDL-011, REQ-MDL-012) has no representation on this
                    screen at all: its caller is another module's backend (ADR-MDL-007). What a
                    user sees of it is indirect — a type deactivated on SCR-MDL-001 stops
                    appearing in this registry's active set, and stops being served to
                    consumers, for the same reason.
Mockup            : not produced this run

══════════════════════════════════════════════════════════════════
