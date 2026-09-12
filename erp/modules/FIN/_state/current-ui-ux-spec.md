# UI / UX SPEC — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Stage : P3.2 (Part A — UX design)
Screens: 12 — SCR-FIN-001..012 · UXD : 12 — UXD-FIN-001..012 (one per displayed lookup key)
Fields : copied from SRS A3 per owning ENT, reconciled against the published DTOs
ADRs   : ADR-FIN-002..008 (all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

كل كتلة أدناه تصف شاشة واحدة: حقولها وصلاحياتها منسوخة من SRS بلا إضافة ولا حذف، ونمط
الحاوية مقرَّر هنا وفق §A.4. «نيّة التصميم» اقتراح مُعلَّم بوضوح ولا يُقرأ كقاعدة.

Each block below is one screen. Fields and permissions are copied from the SRS; the
container pattern is decided here; `Design intent` is a clearly marked proposal, never a rule.

**Error states** are stated generically per §A.3; the catalog codes and their routing belong
to Part B (`frontend-execution-plan-fin.md` → F2).

---

## CROSS-MODULE DISPLAY DEPENDENCIES — UXD-FIN-001..012

كل قيمة قائمة تُحمَّل وقت التشغيل من وحدة القوائم (MDL) — لا تُخزَّن FIN نصّ عرض ولا تُعرِّف
أي `enum`. FIN تملك المفاتيح الثلاثة عشر وتُسجّلها في MDL (REQ-FIN-045)، لكن القيم والتسميات
تُخدَم من نداء MDL الاستهلاكي `API-MDL-011` — `GET /api/v1/mdl/lookups` مع وسيط الاستعلام
`type` يساوي مفتاح القائمة؛ الاستجابة `List<LookupValueResponse>` بالقيم النشطة فقط مرتّبةً
بـ`sortOrder`، وكل قيمة تحمل `nameAr` و`nameEn`. هذا بالضبط ما يعرّفه §A.5 كاعتماد عرض
عابر للوحدات، فيُسك له `UXD-*`.

Twelve keys are displayed on a FIN screen and each mints one `UXD-*`; `PAYMENT_METHOD` is
registered by REQ-FIN-045 but no FIN field cites it in this version, so it mints none
(ADR-FIN-004). One `UXD-*` per key, not per screen occurrence: the key is the unit the one
shared hook is built on.

The same reasoning covers one non-lookup dependency, and it is deliberately **not** a `UXD-*`:
a FIN screen's navigation guard reads the caller's effective menu from the security module
(`API-SEC-027`, `GET /api/v1/sec/menu`). That is an authorization gate, not a displayed
field — no screen renders its content as data — so it is recorded in ADR-FIN-005 and in the
plan's SEC-FE phase rather than minted here. §A.5 mints on a displayed field.

### UXD-FIN-001 — نوع الحساب / Account type
Traces      : REQ-FIN-001, AC-FIN-001, REQ-FIN-040, AC-FIN-040
Lookup key  : `ACCOUNT_TYPE` — ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE (SRS §A6)
Owner       : MDL (registered by FIN, REQ-FIN-045) · resolved through API-MDL-011
Screens     : SCR-FIN-001 (the account form and its filter) · SCR-FIN-009 (filter and row
              column) · SCR-FIN-010, SCR-FIN-011 (section headings per account type)
Field       : `ENT-FIN-001.accountTypeCode`, and `accountTypeCode` on every report row
Display     : the code is stored and sent; the label shown is the value's `nameAr` / `nameEn`

### UXD-FIN-002 — الاتجاه والطبيعة / Direction and normal balance side
Traces      : REQ-FIN-001, AC-FIN-001, REQ-FIN-018, AC-FIN-018
Lookup key  : `DEBIT_CREDIT` — DEBIT, CREDIT (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-001 (`natureCode`) · SCR-FIN-003 (a rule line's `directionCode`) ·
              SCR-FIN-004 (a template line's `directionCode`) · SCR-FIN-006 (an entry line's
              `directionCode`) · SCR-FIN-008 (a ledger row's `directionCode`) ·
              SCR-FIN-009, SCR-FIN-010, SCR-FIN-011, SCR-FIN-012 (a row's `natureCode`)
Field       : `ENT-FIN-001.natureCode`, `ENT-FIN-005.directionCode`,
              `ENT-FIN-010.directionCode`, `ENT-FIN-012.directionCode`
Display     : code stored, label per language from the lookup value

### UXD-FIN-003 — حالة الفترة / Period state
Traces      : REQ-FIN-032, AC-FIN-032, REQ-FIN-033, AC-FIN-033, REQ-FIN-034, AC-FIN-034
Lookup key  : `PERIOD_STATE` — OPEN, SOFT_CLOSE, HARD_CLOSE, YEAR_END_CLOSE (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-007 (the period row's status and the status filter)
Field       : `ENT-FIN-008.statusCode`
Display     : code stored, label per language; the row's available actions follow §A7's
              transitions, which are the SRS's, not the lookup's

### UXD-FIN-004 — حالة السنة المالية / Fiscal year status
Traces      : REQ-FIN-031, AC-FIN-031, REQ-FIN-036, AC-FIN-036
Lookup key  : `FISCAL_YEAR_STATUS` — OPEN, CLOSED (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-007 (the year header)
Field       : `ENT-FIN-007.statusCode`
Display     : code stored, label per language

### UXD-FIN-005 — نوع اليومية / Journal type
Traces      : REQ-FIN-027, AC-FIN-027
Lookup key  : `JOURNAL_TYPE` — EVENT_GENERATED, MANUAL, RECURRING, ALLOCATION, REVERSAL
              (SRS §A6; the backend registry records CLOSING and OPENING added as data at
              P3.1 — the select shows whatever MDL serves, and no value is hardcoded here)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-006 (the search filter, and the read-only value on the entry) ·
              SCR-FIN-008 (a ledger row's source column)
Field       : `ENT-FIN-004.journalTypeCode`
Display     : code stored, label per language. On the manual-entry form it is not a select:
              the value is fixed to `MANUAL` and rendered read-only (ADR-FIN-008)

### UXD-FIN-006 — حالة القيد / Journal status
Traces      : REQ-FIN-017, AC-FIN-017, REQ-FIN-027, AC-FIN-027
Lookup key  : `JOURNAL_STATUS` — DRAFT, POSTED, VOID (SRS §A6; VOID is seeded and
              unreachable — classic reversal leaves the original POSTED)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-006 (the search filter and the entry's status)
Field       : `ENT-FIN-004.statusCode`
Display     : code stored, label per language. The screen filters on whatever MDL serves and
              does not hide VOID: a value the ledger never produces simply matches nothing

### UXD-FIN-007 — نوع الحدث المحاسبي / Accounting event type
Traces      : REQ-FIN-007, AC-FIN-007
Lookup key  : `ACCOUNTING_EVENT_TYPE` — host-defined, seeded with zero values (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-003 (the rule header's event type, and the search filter)
Field       : `ENT-FIN-009.eventTypeCode`
Display     : code stored, label per language. The select is legitimately empty until a host
              registers event types — an empty list here is a deployment-data state, never a
              reason to let the user type a free code

### UXD-FIN-008 — نوع اشتقاق الحساب / Account derivation type
Traces      : REQ-FIN-008, AC-FIN-008
Lookup key  : `ACCOUNT_DERIVATION_TYPE` — CONSTANT, DIRECT, MAPPING (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-003 (a rule line)
Field       : `ENT-FIN-010.accountDerivationTypeCode`
Display     : code stored, label per language. The meaning of the sibling
              `accountDerivationValue` follows the chosen code, and the field's helper text
              states that pairing — it is the SRS's §6.2(a), not a new rule

### UXD-FIN-009 — نوع مصدر المبلغ / Amount source type
Traces      : REQ-FIN-008, AC-FIN-008
Lookup key  : `AMOUNT_SOURCE_TYPE` — FIELD, PERCENTAGE, REMAINDER (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-003 (a rule line)
Field       : `ENT-FIN-010.amountSourceTypeCode`
Display     : code stored, label per language

### UXD-FIN-010 — نوع التوزيع / Distribution type
Traces      : REQ-FIN-009, AC-FIN-009, REQ-FIN-025, AC-FIN-025
Lookup key  : `DISTRIBUTION_TYPE` — FIXED, PERCENTAGE, REMAINDER (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-003 (a rule line) · SCR-FIN-005 (an allocation target)
Field       : `ENT-FIN-010.distributionTypeCode`, `ENT-FIN-014.distributionTypeCode`
Display     : code stored, label per language. RULE-FIN-003's remainder marker
              (`isRemainderFl`) is a separate boolean field, not a value of this key

### UXD-FIN-011 — نوع الجدولة / Schedule type
Traces      : REQ-FIN-022, AC-FIN-022
Lookup key  : `RECURRING_SCHEDULE_TYPE` — RECURRING, REVERSING (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-004 (the template header and the search filter)
Field       : `ENT-FIN-011.scheduleTypeCode`
Display     : code stored, label per language. Whether the frequency field applies at all
              follows this value (SRS §A3: frequency is required only for RECURRING)

### UXD-FIN-012 — التكرار / Frequency
Traces      : REQ-FIN-022, AC-FIN-022, REQ-FIN-023, AC-FIN-023
Lookup key  : `RECURRING_FREQUENCY` — MONTHLY, QUARTERLY, ANNUALLY, WEEKLY (SRS §A6)
Owner       : MDL (registered by FIN) · resolved through API-MDL-011
Screens     : SCR-FIN-004 (the template header)
Field       : `ENT-FIN-011.frequencyCode`
Display     : code stored, label per language

---

## SCR-FIN-001 — شجرة الحسابات / Chart of accounts          traces=REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,UXD-FIN-001,UXD-FIN-002
Traces            : REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,AC-FIN-001,AC-FIN-002,AC-FIN-003,UXD-FIN-001,UXD-FIN-002
UI pattern        : true hierarchy (parent/child) — SRS SCR-REQ-FIN-001 B1 "Content shape:
                    true hierarchy (parent/child)"
Container pattern : TREE_MASTER_DETAIL (§A.4 rule 1 — hierarchical parent–child data; two-pane,
                    the account tree beside a permanently visible form)
Sub-views         : Search (the tree and its filters) · Entry (the form beside it) — under this
                    ONE SCR, per the composite-screen rule
Fields shown      : from ENT-FIN-001 —
                    accountPk — معرّف الحساب / Account id (read-only, system, not rendered) ·
                    code — رمز الحساب / Account code (required; editable on create, read-only
                    on edit — `AccountUpdateRequest` does not carry it) ·
                    nameAr — اسم الحساب (عربي) / Account name (Arabic) (required, editable) ·
                    nameEn — اسم الحساب (إنجليزي) / Account name (English) (required, editable) ·
                    accountTypeCode — نوع الحساب / Account type (required; editable on create,
                    read-only on edit — not in the update request; UXD-FIN-001) ·
                    natureCode — الطبيعة / Nature (required; editable on create, read-only on
                    edit — not in the update request; UXD-FIN-002) ·
                    parentAccountId — الحساب الأب / Parent account (optional; editable on
                    create, read-only on edit — not in the update request; null = root) ·
                    isLeafFl — ورقة (يقبل ترحيلاً مباشرًا) / Leaf (accepts direct posting)
                    (editable on create and on edit) ·
                    isActiveFl — نشط / Active (read-only — changed only by the deactivate
                    affordance, API-FIN-004) ·
                    isRetainedEarningsFl — حساب الأرباح المُبقاة / Retained earnings account
                    (read-only, system — the published DTO returns it and states it is never
                    settable through the account APIs; shown as a badge on the row it marks) ·
                    createdBy, createdAt, updatedBy, updatedAt — audit fields (read-only)
                    Search filters, per SRS B2: code (LIKE), nameAr/nameEn (LIKE),
                    accountTypeCode (EXACT), isActiveFl (EXACT) — each corresponds to a result
                    column.
Permissions       : FIN_ACCOUNTS — VIEW (tree, search), CREATE (new account), UPDATE (edit and
                    deactivate — there is no DELETE endpoint and no `PERM_FIN_ACCOUNTS_DELETE`;
                    deactivate is gated by UPDATE). SRS Access summary. Names as the backend
                    declares them: `PERM_FIN_ACCOUNTS_VIEW`, `PERM_FIN_ACCOUNTS_CREATE`,
                    `PERM_FIN_ACCOUNTS_UPDATE`. Reference only — enforcement is the server's.
Cross-module data : accountTypeCode → UXD-FIN-001 (MDL) · natureCode → UXD-FIN-002 (MDL)
States            : empty (no account matches the filters — distinguished from an empty chart)
                    · loading (tree and form load independently) · error (generic here; catalog
                    codes and their routing are Part B's) · offline — the SRS states no offline
                    behaviour, so none is specified
Design intent     : PROPOSAL — the tree stays visible while a node is edited, so the structure
                    that determines where a value may be posted is never off-screen. Creating a
                    child pre-fills the selected node as the parent, which is the common act;
                    the parent stays editable until the account is saved and immutable after.
                    "Accepts direct posting" sits directly under the parent field, because
                    RULE-FIN-001 ties the two: a node with children may not carry it.
                    Deactivate confirms and keeps the row in the tree, since a deactivated
                    account still carries history [POL-FIN-013].
Mockup            : not produced this run (optional per §A.7)

---

## SCR-FIN-002 — تعريف الأبعاد وقيمها / Dimension definition & values   traces=REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006
Traces            : REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,AC-FIN-004,AC-FIN-005,AC-FIN-006
UI pattern        : header + repeating lines — SRS SCR-REQ-FIN-002 B1 "master dimensions +
                    detail values"
Container pattern : TREE_MASTER_DETAIL (§A.4 rule 1 — a dimension and its values are
                    parent–child data; the dimension list beside the selected dimension's
                    values)
Sub-views         : Search (dimensions) · Detail (that dimension's values, with their own
                    search and entry) — under this ONE SCR
Fields shown      : from ENT-FIN-002 (dimension) —
                    dimensionPk — معرّف البُعد / Dimension id (read-only, system, not rendered) ·
                    code — رمز البُعد / Dimension code (required, editable on create) ·
                    nameAr — الاسم (عربي) / Name (Arabic) (required, editable on create) ·
                    nameEn — الاسم (إنجليزي) / Name (English) (required, editable on create) ·
                    isActiveFl — نشط / Active (read-only, and never changed from this screen —
                    the parent dimension has no deactivate endpoint by decision, SRS §B4) ·
                    audit fields (read-only)
                    from ENT-FIN-003 (value) —
                    dimensionValuePk — معرّف قيمة البُعد / Value id (read-only, system) ·
                    dimensionId — البُعد / Dimension (read-only — taken from the selected
                    parent, never typed) ·
                    code — الرمز / Code (required, editable on create; unique within the
                    dimension — RULE-FIN-002) ·
                    nameAr, nameEn — الاسم (عربي/إنجليزي) / Name (Arabic/English) (required,
                    editable on create) ·
                    sortOrder — ترتيب العرض / Sort order (required, editable on create) ·
                    isActiveFl — نشط / Active (read-only — changed only by the deactivate
                    affordance, API-FIN-035) ·
                    audit fields (read-only)
                    Search filters, per SRS B2: dimension code (LIKE); value code (LIKE).
Permissions       : FIN_DIMENSIONS — VIEW, CREATE, UPDATE. UPDATE covers exactly one
                    operation: deactivating a dimension **value** (`PERM_FIN_DIMENSIONS_UPDATE`,
                    SRS §B4). No DELETE endpoint and no `PERM_FIN_DIMENSIONS_DELETE`.
Cross-module data : none — every field on this screen is FIN's own. The dimension **is** what
                    other screens' lookups are built from, but its own values are not read
                    from another module
States            : empty (no dimension, or a dimension with no values yet — the two are
                    distinguished) · loading · error (generic) · offline — not specified
Design intent     : PROPOSAL — values are the working surface, so the selected dimension's
                    values fill the detail pane immediately rather than behind a second click.
                    Deactivating a value confirms and names the consequence in the SRS's own
                    terms: a retired value is refused on any later journal line (REQ-FIN-021).
                    The parent dimension shows its active flag without an affordance to change
                    it, rather than hiding the field, so the asymmetry is visible instead of
                    looking like an oversight.
Mockup            : not produced this run

---

## SCR-FIN-003 — قواعد المحرك / Engine rules                traces=REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,UXD-FIN-002
Traces            : REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,AC-FIN-007,AC-FIN-008,AC-FIN-009,UXD-FIN-007,UXD-FIN-008,UXD-FIN-009,UXD-FIN-010,UXD-FIN-002
UI pattern        : header + repeating lines — SRS SCR-REQ-FIN-003 B1 "rule header + its lines"
Container pattern : FULL_PAGE (§A.4 rule 2 — header plus repeating line items whose
                    percentage distribution has to total, document-style; the rule and its
                    lines are read and judged as one page)
Sub-views         : Search (the rule list) · Entry (the rule page with its line grid) — under
                    this ONE SCR
Fields shown      : from ENT-FIN-009 (rule) —
                    eventTypeRulePk — معرّف قاعدة الحدث / Rule id (read-only, system) ·
                    eventTypeCode — نوع الحدث / Event type (required, editable on create;
                    one rule per event type; UXD-FIN-007) ·
                    nameAr, nameEn — الاسم (عربي/إنجليزي) / Name (Arabic/English) (required,
                    editable on create) ·
                    isActiveFl — نشط / Active (read-only — changed only by the deactivate
                    affordance, API-FIN-034) · audit fields (read-only)
                    from ENT-FIN-010 (line) —
                    ruleLinePk — معرّف سطر القاعدة / Line id (read-only, system) ·
                    lineNo — رقم السطر / Line number (read-only, server-assigned) ·
                    accountDerivationTypeCode — نوع اشتقاق الحساب / Account derivation type
                    (required; UXD-FIN-008) ·
                    accountDerivationValue — قيمة الاشتقاق / Derivation value (required; a
                    constant account code, an event field name or a mapping-set key, per the
                    chosen derivation type) ·
                    amountSourceTypeCode — نوع مصدر المبلغ / Amount source type (required;
                    UXD-FIN-009) ·
                    amountSourceValue — قيمة مصدر المبلغ / Amount source value (required
                    unless the source type is REMAINDER) ·
                    directionCode — الاتجاه / Direction (required; UXD-FIN-002) ·
                    distributionTypeCode — نوع التوزيع / Distribution type (required;
                    UXD-FIN-010) ·
                    isRemainderFl — سطر الباقي / Remainder line (editable; exactly one true
                    per rule whenever any line is PERCENTAGE — RULE-FIN-003)
                    Search filters, per SRS B2: eventTypeCode (EXACT), isActiveFl (EXACT).
Permissions       : FIN_RULES — VIEW, CREATE, UPDATE. UPDATE covers both adding a rule line
                    (API-FIN-011) and deactivating a rule (API-FIN-034), under the single
                    `PERM_FIN_RULES_UPDATE`. No DELETE endpoint, no `PERM_FIN_RULES_DELETE`.
Cross-module data : eventTypeCode → UXD-FIN-007 · accountDerivationTypeCode → UXD-FIN-008 ·
                    amountSourceTypeCode → UXD-FIN-009 · distributionTypeCode → UXD-FIN-010 ·
                    directionCode → UXD-FIN-002 (all MDL)
States            : empty (no rule matches; or a rule with no lines yet — a rule with no line
                    builds nothing, and the empty state says so) · loading · error (generic) ·
                    offline — not specified
Design intent     : PROPOSAL — the three references §6.2 keeps separate (account derivation,
                    amount source, direction) stay three separate columns on the line, never
                    collapsed into one "mapping" control, because that separation is the
                    design the SRS protects [POL-FIN-014]. The remainder marker is a single
                    exclusive choice across the line grid rather than a free checkbox per row,
                    which is how RULE-FIN-003's "exactly one" reads to a user before the
                    server says it. A rule with no update endpoint shows no Edit affordance;
                    the header is created once (ADR-FIN-006).
Mockup            : not produced this run

---

## SCR-FIN-004 — قوالب متكررة/عكسية / Recurring / reversing templates   traces=REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,UXD-FIN-011,UXD-FIN-012,UXD-FIN-002
Traces            : REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,AC-FIN-022,AC-FIN-023,AC-FIN-024,UXD-FIN-011,UXD-FIN-012,UXD-FIN-002
UI pattern        : header + repeating lines — SRS SCR-REQ-FIN-004 B1
Container pattern : FULL_PAGE (§A.4 rule 2 — header plus repeating line items with a debit /
                    credit total the user must see while entering)
Sub-views         : Search (the template list) · Entry (the template page with its line grid)
                    — under this ONE SCR
Fields shown      : from ENT-FIN-011 (template) —
                    recurringTemplatePk — معرّف القالب / Template id (read-only, system) ·
                    nameAr, nameEn — الاسم (عربي/إنجليزي) / Name (Arabic/English) (required,
                    editable on create) ·
                    scheduleTypeCode — نوع الجدولة / Schedule type (required; UXD-FIN-011) ·
                    frequencyCode — التكرار / Frequency (required when the schedule type is
                    RECURRING, not applicable to a pure reversing template; UXD-FIN-012) ·
                    startDate — تاريخ البدء / Start date (required, editable on create) ·
                    nextRunDate — تاريخ التشغيل القادم / Next run date (read-only,
                    system-maintained — it advances after each run) ·
                    endDate — تاريخ الانتهاء / End date (optional, editable on create) ·
                    isActiveFl — نشط / Active (read-only — changed only by the deactivate
                    affordance, API-FIN-036) ·
                    lineCount — عدد السطور / Line count (read-only, derived by the server) ·
                    audit fields (read-only)
                    from ENT-FIN-012 (line) —
                    recurringTemplateLinePk, lineNo (read-only, system) ·
                    accountId — الحساب / Account (required — a leaf, active account) ·
                    amount — المبلغ / Amount (required, positive) ·
                    directionCode — الاتجاه / Direction (required; UXD-FIN-002) ·
                    dimensionValueId — قيمة البُعد / Dimension value (optional — one per line,
                    per the §9.3.3 simplification recorded in the SRS)
                    Search filters, per SRS B2: nameAr/nameEn (LIKE), scheduleTypeCode
                    (EXACT), isActiveFl (EXACT).
Permissions       : FIN_RECURRING_TEMPLATES — VIEW, CREATE, UPDATE. UPDATE covers both running
                    a template (API-FIN-014) and deactivating it (API-FIN-036), under the
                    single `PERM_FIN_RECURRING_TEMPLATES_UPDATE`. No DELETE endpoint.
Cross-module data : scheduleTypeCode → UXD-FIN-011 · frequencyCode → UXD-FIN-012 ·
                    directionCode → UXD-FIN-002 (all MDL)
States            : empty (no template matches the filters) · loading · error (generic) ·
                    offline — not specified
Design intent     : PROPOSAL — the line grid shows a running debit and credit total while the
                    template is drafted, because the balance the run will be judged on is the
                    one being typed; the total is a display, and the judgement stays the
                    server's at run time. The frequency field is hidden, not merely disabled,
                    when the schedule type is REVERSING — the SRS calls it "not applicable",
                    not "empty". Run and Deactivate both confirm, and the deactivate
                    confirmation states plainly that the template will no longer run. No Edit
                    affordance is drawn: no update endpoint exists (ADR-FIN-006), and the
                    empty-state text says a wrong template is retired and replaced.
Mockup            : not produced this run

---

## SCR-FIN-005 — قواعد التوزيع / Allocation rules           traces=REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,UXD-FIN-010
Traces            : REQ-FIN-025,REQ-FIN-026,AC-FIN-025,AC-FIN-026,UXD-FIN-010
UI pattern        : header + repeating lines — SRS SCR-REQ-FIN-005 B1 (rule + its targets)
Container pattern : FULL_PAGE (§A.4 rule 2 — header plus repeating targets whose distribution
                    values have to total, document-style)
Sub-views         : Search (the rule list) · Entry (the rule page with its target grid) —
                    under this ONE SCR
Fields shown      : from ENT-FIN-013 (rule) —
                    allocationRulePk — معرّف قاعدة التوزيع / Rule id (read-only, system) ·
                    nameAr, nameEn — الاسم (عربي/إنجليزي) / Name (Arabic/English) (required,
                    editable on create) ·
                    sourceAccountId — الحساب المصدر / Source account (required — the balance
                    being distributed) ·
                    isActiveFl — نشط / Active (read-only — changed only by the deactivate
                    affordance, API-FIN-037) ·
                    targetCount — عدد الأهداف / Target count (read-only, derived) ·
                    audit fields (read-only)
                    from ENT-FIN-014 (target) —
                    allocationTargetPk, lineNo (read-only, system) ·
                    targetAccountId — الحساب الهدف / Target account (required) ·
                    dimensionValueId — قيمة البُعد / Dimension value (optional — one per
                    target) ·
                    distributionTypeCode — نوع التوزيع / Distribution type (required;
                    UXD-FIN-010) ·
                    distributionValue — قيمة التوزيع / Distribution value (required unless the
                    distribution type is REMAINDER) ·
                    isRemainderFl — هدف الباقي / Remainder target (editable; exactly one true
                    whenever any target is PERCENTAGE — RULE-FIN-003)
                    Search filters, per SRS B2: nameAr/nameEn (LIKE), sourceAccountId (EXACT),
                    isActiveFl (EXACT).
Permissions       : FIN_ALLOCATION_RULES — VIEW, CREATE, UPDATE. UPDATE covers both running the
                    rule (API-FIN-017) and deactivating it (API-FIN-037), under the single
                    `PERM_FIN_ALLOCATION_RULES_UPDATE`. No DELETE endpoint.
Cross-module data : distributionTypeCode → UXD-FIN-010 (MDL)
States            : empty (no rule matches the filters) · loading · error (generic) ·
                    offline — not specified
Design intent     : PROPOSAL — the target grid shows the percentage targets' running sum, and
                    the remainder target's cell shows "الباقي / remainder" instead of a number,
                    because RULE-FIN-010 computes it as a difference and never as a
                    percentage; showing a predicted figure would invite the user to trust a
                    number the server has not produced. The source account is chosen once in
                    the header and is the subject of every target row below it. Run and
                    Deactivate confirm; no Edit affordance is drawn (ADR-FIN-006).
Mockup            : not produced this run

---

## SCR-FIN-006 — قيود اليومية / Journal entries            traces=REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,UXD-FIN-005,UXD-FIN-006,UXD-FIN-002
Traces            : REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-014,REQ-FIN-015,REQ-FIN-016,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,AC-FIN-014,AC-FIN-015,AC-FIN-016,AC-FIN-017,AC-FIN-018,AC-FIN-019,AC-FIN-020,AC-FIN-021,AC-FIN-027,AC-FIN-028,AC-FIN-029,AC-FIN-030,UXD-FIN-005,UXD-FIN-006,UXD-FIN-002
UI pattern        : header + repeating lines with totals — SRS SCR-REQ-FIN-006 B1
                    "debit/credit totals shown live while entering"
Container pattern : FULL_PAGE (§A.4 rule 2 — the document-style case exactly: a header, a
                    repeating line grid, and a computed total that decides whether the
                    document may post)
Sub-views         : Search (the entry list) · Entry (the entry page, in create mode or
                    read-only on a posted entry, with the Reverse action) — under this ONE SCR
Fields shown      : from ENT-FIN-004 (header) —
                    journalEntryPk — معرّف القيد / Entry id (read-only, system) ·
                    docNo — رقم المستند / Document number (read-only, system — generated on
                    first save and never editable) ·
                    docDate — تاريخ المستند / Document date (required, editable on create) ·
                    fiscalYearId — السنة المالية / Fiscal year (required, editable on create —
                    B3 does not list it, the published request requires it, and RULE-FIN-017
                    checks it against the period and the date; ADR-FIN-008) ·
                    periodId — الفترة / Period (required, editable on create; the select is
                    narrowed to the chosen year) ·
                    journalTypeCode — نوع اليومية / Journal type (in the form model as the
                    fixed value MANUAL, rendered read-only — ADR-FIN-008; a real filter on the
                    search; UXD-FIN-005) ·
                    statusCode — الحالة / Status (read-only, system — DRAFT then POSTED;
                    UXD-FIN-006) ·
                    eventReference — مرجع الحدث / Event reference (read-only — present only on
                    an event-sourced entry, and the end of the REQ-FIN-046 drill-down) ·
                    originalEntryId — القيد الأصلي / Original entry (read-only, a link) ·
                    reversalEntryId — قيد العكس / Reversal entry (read-only, a link) ·
                    descriptionAr, descriptionEn — الوصف (عربي/إنجليزي) / Description
                    (Arabic/English) (optional, editable on create) ·
                    postedAt — تاريخ الترحيل / Posted at (read-only, system) ·
                    lineCount — عدد السطور / Line count (read-only, derived) ·
                    audit fields (read-only)
                    from ENT-FIN-005 (line, repeating) —
                    journalLinePk, lineNo (read-only, system) ·
                    accountId — الحساب / Account (required — a leaf, active account) ·
                    amount — المبلغ / Amount (required, always positive) ·
                    directionCode — الاتجاه / Direction (required — it carries the sign, the
                    amount never does; UXD-FIN-002) ·
                    isRemainderFl — سطر الباقي / Remainder line (read-only on this screen — it
                    is set by the engine on a built entry, never typed on a manual one) ·
                    descriptionAr, descriptionEn (optional)
                    from ENT-FIN-006 (line dimensions, repeating under a line) —
                    dimensionId — البُعد / Dimension (required when a dimension is used) ·
                    dimensionValueId — قيمة البُعد / Dimension value (required with it)
                    Search filters, per SRS B2: docNo (LIKE), docDate (DATE_RANGE), periodId
                    (EXACT), statusCode (EXACT), journalTypeCode (EXACT).
Permissions       : FIN_JOURNAL_ENTRIES — VIEW (search and read), CREATE (the manual entry,
                    posting included). Reverse is a custom action with its own name,
                    `PERM_FIN_JOURNAL_ENTRIES_REVERSE` (SRS Access summary: modelled as an
                    update-class action). There is no UPDATE and no DELETE on a posted entry —
                    RULE-FIN-016 locks it and correction is only by reversal.
Cross-module data : journalTypeCode → UXD-FIN-005 · statusCode → UXD-FIN-006 ·
                    directionCode → UXD-FIN-002 (all MDL)
States            : empty (no entry matches the filters — distinguished from a ledger with no
                    entries at all) · loading (list and entry load independently) · error
                    (generic here; the catalog codes and their routing are Part B's, and
                    REQ-FIN-015's "every failing check" is an F2 concern) · offline — not
                    specified
Design intent     : PROPOSAL — the debit and credit totals sit at the foot of the line grid and
                    update as the user types, with the difference shown when they disagree.
                    The Post affordance stays enabled regardless: REQ-FIN-015 asks for every
                    failing check to come back at once, which means the submission has to
                    happen. A posted entry opens read-only with no edit affordance anywhere on
                    it, and Reverse is the only action — its confirmation names the period the
                    reversal will land in, because RULE-FIN-012 may move it to the current open
                    one. Dimensions are entered under their line rather than as a separate
                    section, so the account-and-dimension combination REQ-FIN-043 later reports
                    on is visible as one thing.
Mockup            : not produced this run

---

## SCR-FIN-007 — الفترات والسنوات المالية / Fiscal periods & years   traces=REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,UXD-FIN-003,UXD-FIN-004
Traces            : REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,REQ-FIN-034,REQ-FIN-035,REQ-FIN-036,REQ-FIN-037,REQ-FIN-038,AC-FIN-031,AC-FIN-032,AC-FIN-033,AC-FIN-034,AC-FIN-035,AC-FIN-036,AC-FIN-037,AC-FIN-038,UXD-FIN-003,UXD-FIN-004
UI pattern        : header + repeating lines — SRS SCR-REQ-FIN-007 B1 "year + its periods"
Container pattern : TREE_MASTER_DETAIL (§A.4 rule 1 — a year and its periods are parent–child
                    data; the years beside the selected year's periods)
Sub-views         : Search (the period list, optionally narrowed to one year) · Entry (the
                    create-year form) · the per-period actions — under this ONE SCR
Fields shown      : from ENT-FIN-007 (year) —
                    fiscalYearPk — معرّف السنة المالية / Fiscal year id (read-only, system) ·
                    code — رمز السنة / Year code (required on create) ·
                    startDate — تاريخ البداية / Start date (required on create) ·
                    endDate — تاريخ النهاية / End date (required on create) ·
                    periodCount — عدد الفترات / Period count (required on create — it is an
                    input to generation, and the response returns it with the generated
                    periods) ·
                    statusCode — الحالة / Status (read-only; UXD-FIN-004) ·
                    isActiveFl — نشط / Active (read-only) · audit fields (read-only)
                    from ENT-FIN-008 (period) —
                    fiscalPeriodPk — معرّف الفترة / Period id (read-only, system) ·
                    fiscalYearId — السنة المالية / Fiscal year (read-only) ·
                    periodNo — رقم الفترة / Period number (read-only, generated) ·
                    nameAr, nameEn — الاسم (عربي/إنجليزي) / Name (Arabic/English) (read-only,
                    generated — month names for a twelve-period year, "الفترة N" / "Period N"
                    otherwise) ·
                    startDate, endDate — تاريخ البداية / تاريخ النهاية / Start date / End date
                    (read-only, generated) ·
                    statusCode — الحالة / Status (read-only — changed only by the open,
                    soft-close and hard-close affordances; UXD-FIN-003) ·
                    closedBy — أُغلقت بواسطة / Closed by (read-only, set at hard-close) ·
                    closedAt — تاريخ الإغلاق / Closed at (read-only, set at hard-close) ·
                    audit fields (read-only)
                    Search filters, per SRS B2: fiscalYearId (EXACT, optional), statusCode
                    (EXACT, optional). Omitting the year is a legitimate "all periods" request.
Permissions       : FIN_PERIODS — VIEW (the period search, and the screen gateway), CREATE
                    (the fiscal year), UPDATE (open and soft-close), plus the distinct custom
                    action `PERM_FIN_PERIODS_CLOSE_APPROVE` for hard-close and year-end close —
                    the separate permission RULE-FIN-015 requires. No DELETE.
Cross-module data : period statusCode → UXD-FIN-003 · year statusCode → UXD-FIN-004 (MDL)
States            : empty (no period matches the filters — and, on a fresh deployment, no
                    fiscal year at all, which the empty state names as the first thing to
                    create) · loading · error (generic) · offline — not specified
Design intent     : PROPOSAL — the year list on the left is derived from the `fiscalYearId` of
                    the period rows, since no fiscal-year search is published (ADR-FIN-006);
                    the screen presents that as an ordinary list and does not expose the
                    indirection. Each period row carries only the transitions §A7 allows from
                    its current state, so a hard-closed row shows no Open affordance at all
                    rather than one that always fails. Hard-close confirms with the word
                    "permanent", because RULE-FIN-014 makes it exactly that. "Run year-end
                    close" sits on the year header and shows the count of periods not yet
                    hard-closed beside it as context, not as a gate — the gate is the
                    server's.
Mockup            : not produced this run

---

## SCR-FIN-008 — دفتر الحساب / Account ledger              traces=REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,UXD-FIN-002,UXD-FIN-005
Traces            : REQ-FIN-039,REQ-FIN-046,AC-FIN-039,AC-FIN-046,UXD-FIN-002,UXD-FIN-005
UI pattern        : flat record — SRS SCR-REQ-FIN-008 B1 "running balance list"
Container pattern : FULL_PAGE (no entry sub-view — ADR-FIN-003; a read-only report)
Sub-views         : none — a single report screen, no entry (SRS B3 "not applicable")
Fields shown      : the report header returned by the endpoint —
                    accountId, accountCode — رمز الحساب / Account code ·
                    accountNameAr, accountNameEn — اسم الحساب / Account name ·
                    accountTypeCode — نوع الحساب / Account type (UXD-FIN-001) ·
                    natureCode — الطبيعة / Nature (UXD-FIN-002) ·
                    fromDate, toDate — من / إلى / From / To ·
                    dimensionId, dimensionValueId — البُعد وقيمته / Dimension and value ·
                    debitTotal — إجمالي المدين / Debit total ·
                    creditTotal — إجمالي الدائن / Credit total ·
                    closingBalance — الرصيد الختامي / Closing balance
                    per row (ENT-FIN-005, live-derived) —
                    docNo — رقم المستند / Document number (a link to SCR-FIN-006) ·
                    docDate — تاريخ المستند / Document date ·
                    journalTypeCode — نوع اليومية / Journal type (UXD-FIN-005) ·
                    eventReference — مرجع الحدث / Event reference (the drill-down's end) ·
                    lineNo — رقم السطر / Line number ·
                    amount — المبلغ / Amount · directionCode — الاتجاه / Direction
                    (UXD-FIN-002) · signedAmount — المبلغ بالإشارة / Signed amount ·
                    runningBalance — الرصيد الجاري / Running balance ·
                    descriptionAr, descriptionEn — الوصف / Description
                    Filters, per SRS B2: accountId (EXACT, required), a date range
                    (DATE_RANGE), dimension and dimension value (EXACT).
                    All fields are read-only: this screen writes nothing.
Permissions       : FIN_ACCOUNT_LEDGER — VIEW only (`PERM_FIN_ACCOUNT_LEDGER_VIEW`). The SRS
                    Access summary gives this screen no CREATE, UPDATE, DELETE or custom action.
Cross-module data : accountTypeCode → UXD-FIN-001 · natureCode and directionCode →
                    UXD-FIN-002 · journalTypeCode → UXD-FIN-005 (all MDL)
States            : empty (the account has no posted line in the range — distinguished from an
                    account that has never been posted to) · loading · error (generic) ·
                    offline — not specified
Design intent     : PROPOSAL — the running balance is the point of the screen, so it is the
                    rightmost, most prominent column, and the header totals restate it at the
                    top rather than only at the foot of a long list. Every row's document
                    number is a link to its entry, which is the third hop of REQ-FIN-046's
                    chain. The account and the range live in the route's search params, so a
                    ledger view arrived at by drill-down is the same address a user can share.
                    Nothing here is cached between visits: POL-FIN-009 means the figure is
                    computed at request time, and a stale copy would be exactly the defect the
                    policy exists to prevent.
Mockup            : not produced this run

---

## SCR-FIN-009 — ميزان المراجعة / Trial balance            traces=REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,UXD-FIN-001,UXD-FIN-002
Traces            : REQ-FIN-040,REQ-FIN-046,AC-FIN-040,AC-FIN-046,UXD-FIN-001,UXD-FIN-002
UI pattern        : flat record — SRS SCR-REQ-FIN-009 B1 "one row per account"
Container pattern : FULL_PAGE (no entry sub-view — ADR-FIN-003)
Sub-views         : none — a single report screen
Fields shown      : the report header — periodId — الفترة / Period · accountTypeCode — نوع
                    الحساب / Account type (UXD-FIN-001) · totalDebitBalance — إجمالي الأرصدة
                    المدينة / Total debit balances · totalCreditBalance — إجمالي الأرصدة
                    الدائنة / Total credit balances · balanced — متوازن / Balanced
                    per row — accountId · accountCode — رمز الحساب / Account code ·
                    accountNameAr, accountNameEn — اسم الحساب / Account name ·
                    accountTypeCode (UXD-FIN-001) · natureCode (UXD-FIN-002) ·
                    debitTotal, creditTotal — إجمالي المدين / الدائن / Debit / Credit total ·
                    debitBalance, creditBalance — الرصيد المدين / الدائن / Debit / Credit
                    balance · signedBalance — الرصيد بالإشارة / Signed balance
                    Filters, per SRS B2: periodId (EXACT, optional), accountTypeCode (EXACT,
                    optional). All fields read-only.
Permissions       : FIN_TRIAL_BALANCE — VIEW only (`PERM_FIN_TRIAL_BALANCE_VIEW`).
Cross-module data : accountTypeCode → UXD-FIN-001 · natureCode → UXD-FIN-002 (MDL)
States            : empty (no posted line in the selected period) · loading · error (generic —
                    including the not-found the endpoint answers when a supplied period id
                    does not resolve) · offline — not specified
Design intent     : PROPOSAL — `balanced` is rendered as a single, unmissable statement at the
                    top, not a quiet column: REQ-FIN-040 makes the equality a property of the
                    report, and a controller's first question is whether it holds. Each row's
                    account links to SCR-FIN-008 for that account, carrying the period's range,
                    which is the second hop of the drill-down chain. Both filters are optional,
                    and the unfiltered view is a legitimate whole-ledger trial balance rather
                    than an error state.
Mockup            : not produced this run

---

## SCR-FIN-010 — الميزانية العمومية / Balance sheet        traces=REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,UXD-FIN-001,UXD-FIN-002
Traces            : REQ-FIN-041,REQ-FIN-046,AC-FIN-041,AC-FIN-046,UXD-FIN-001,UXD-FIN-002
UI pattern        : header + repeating lines with totals — SRS SCR-REQ-FIN-010 B1
                    (assets / liabilities / equity sections)
Container pattern : FULL_PAGE (no entry sub-view — ADR-FIN-003)
Sub-views         : none — a single report screen
Fields shown      : the report header — fiscalYearId — السنة المالية / Fiscal year ·
                    asOfDate — حتى تاريخ / As of date
                    per group — accountTypeCode — نوع الحساب / Account type (the section
                    heading; UXD-FIN-001) · groupTotal — إجمالي المجموعة / Group total
                    per row — accountId · accountCode · accountNameAr, accountNameEn ·
                    accountTypeCode (UXD-FIN-001) · natureCode (UXD-FIN-002) ·
                    debitTotal, creditTotal · debitBalance, creditBalance · signedBalance
                    Filters, per SRS B2: fiscalYearId (EXACT, required), asOfDate (optional
                    cut-off). All fields read-only.
Permissions       : FIN_BALANCE_SHEET — VIEW only (`PERM_FIN_BALANCE_SHEET_VIEW`).
Cross-module data : accountTypeCode → UXD-FIN-001 · natureCode → UXD-FIN-002 (MDL)
States            : empty (a year with no posted balance-sheet line) · loading · error
                    (generic — including the not-found the endpoint answers for an unknown
                    fiscal year, which is the required keying id) · offline — not specified
Design intent     : PROPOSAL — the fiscal year is required, so the screen asks for it before it
                    asks for anything else and does not render a blank statement while it is
                    unset. Sections follow the account-type grouping the endpoint returns
                    rather than a grouping composed on the client, so the statement's shape is
                    the server's. Each row links to SCR-FIN-009 narrowed to that account type,
                    which is the first hop of REQ-FIN-046's chain.
Mockup            : not produced this run

---

## SCR-FIN-011 — قائمة الدخل / Income statement            traces=REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,UXD-FIN-001,UXD-FIN-002
Traces            : REQ-FIN-042,REQ-FIN-046,AC-FIN-042,AC-FIN-046,UXD-FIN-001,UXD-FIN-002
UI pattern        : header + repeating lines with totals — SRS SCR-REQ-FIN-011 B1
                    (revenue / expense sections)
Container pattern : FULL_PAGE (no entry sub-view — ADR-FIN-003)
Sub-views         : none — a single report screen
Fields shown      : the report header — fiscalYearId — السنة المالية / Fiscal year ·
                    fromPeriodId, toPeriodId — من فترة / إلى فترة / From period / To period ·
                    fromDate, toDate — من تاريخ / إلى تاريخ / From date / To date (read-only,
                    derived by the server from the chosen periods) · netResult — صافي النتيجة
                    / Net result
                    per group — accountTypeCode (the section heading; UXD-FIN-001) ·
                    groupTotal — إجمالي المجموعة / Group total
                    per row — accountId · accountCode · accountNameAr, accountNameEn ·
                    accountTypeCode (UXD-FIN-001) · natureCode (UXD-FIN-002) ·
                    debitTotal, creditTotal · debitBalance, creditBalance · signedBalance
                    Filters, per SRS B2: fiscalYearId (EXACT, required); the period range as
                    two optional period ids, fromPeriodId and toPeriodId. All read-only.
Permissions       : FIN_INCOME_STATEMENT — VIEW only (`PERM_FIN_INCOME_STATEMENT_VIEW`).
Cross-module data : accountTypeCode → UXD-FIN-001 · natureCode → UXD-FIN-002 (MDL)
States            : empty (a new year before any posting — which REQ-FIN-042 makes a
                    meaningful, correct result of zero rather than an error) · loading · error
                    (generic — including the not-found for an unknown year or period) ·
                    offline — not specified
Design intent     : PROPOSAL — the period range is expressed as two period selects narrowed to
                    the chosen year, not as free dates, because that is what the endpoint
                    takes; the dates it derives are shown read-only beside them so the user can
                    see what the range resolved to. An all-zero statement immediately after a
                    year-end close is labelled as such rather than shown as an empty list —
                    REQ-FIN-042 makes zero the right answer.
Mockup            : not produced this run

---

## SCR-FIN-012 — تقارير الأبعاد / Dimension reports        traces=REQ-FIN-043,AC-FIN-043,UXD-FIN-002
Traces            : REQ-FIN-043,AC-FIN-043,UXD-FIN-002
UI pattern        : flat record — SRS SCR-REQ-FIN-012 B1 "account × dimension-value rows"
Container pattern : FULL_PAGE (no entry sub-view — ADR-FIN-003)
Sub-views         : none — a single report screen
Fields shown      : the report header — dimensionId — البُعد / Dimension ·
                    dimensionValueId — قيمة البُعد / Dimension value · periodId — الفترة /
                    Period
                    per row — accountId · accountCode — رمز الحساب / Account code ·
                    accountNameAr, accountNameEn — اسم الحساب / Account name ·
                    natureCode — الطبيعة / Nature (UXD-FIN-002) ·
                    dimensionId · dimensionValueId ·
                    dimensionValueCode — رمز قيمة البُعد / Dimension value code ·
                    dimensionValueNameAr, dimensionValueNameEn — اسم قيمة البُعد / Dimension
                    value name · debitTotal, creditTotal — إجمالي المدين / الدائن /
                    Debit / Credit total · signedBalance — الرصيد بالإشارة / Signed balance
                    Filters, per SRS B2: dimensionId (EXACT, required), dimensionValueId
                    (EXACT, optional), periodId (EXACT, optional). All fields read-only.
Permissions       : FIN_DIMENSION_REPORTS — VIEW only (`PERM_FIN_DIMENSION_REPORTS_VIEW`).
Cross-module data : natureCode → UXD-FIN-002 (MDL). The dimension and its values are FIN's own
                    entities (ENT-FIN-002, ENT-FIN-003) and their names come from the report
                    rows themselves, so they are not a cross-module dependency
States            : empty (no posted line carries the chosen dimension in the chosen period) ·
                    loading · error (generic — including the not-found for an unknown
                    dimension, which is the required keying id) · offline — not specified
Design intent     : PROPOSAL — the account and the dimension value are shown as two columns of
                    the same row and never collapsed into one label, because REQ-FIN-043's
                    whole point is that the same account appears once per dimension value.
                    Rows are grouped by account with the dimension values under it, so the
                    duplication reads as a breakdown rather than as repeated accounts. Each row
                    links to SCR-FIN-008 for that account carrying the dimension and its value,
                    so the ledger behind the figure shows the same slice.
Mockup            : not produced this run

══════════════════════════════════════════════════════════════════
