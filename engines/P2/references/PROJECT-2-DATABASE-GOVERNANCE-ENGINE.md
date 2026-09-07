<!-- FACTORY NOTICE: this reference predates the git-native factory. Drive /
     ledger / connector steps in it are SUPERSEDED — see shared/FACTORY-PRECEDENCE.md
     (loaded first). Everything else (names, markers, gates, dependencies) applies. -->

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-PIPELINE-V5 — see GOVERNANCE-CONFIG.md §1D          -->
<!-- ══════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-PIPELINE-V5** (GOVERNANCE-CONFIG §1D — المصدر الواحد).
> هذا المحرك (P2 Database) ضمن **المسار الأساسي** (1D.1). يلتزم بـ:
> **أسماء الملفات المؤهَّلة بالموديول** (1D.2) · **بروتوكول الإنهاء الموحّد**
> (1D.4: artifact → registry inline → ledger → handoff) · **NEXT-ENGINE INPUT**
> (1D.5). تفاصيل هذا المحرك في القسم الختامي "COMPLETION PROTOCOL" أسفل الملف.
> 
<!-- ══════════════════════════════════════════════════════════════ -->

<!-- ════════════════════════════════════════════════════════════════ -->
<!-- GOVERNED BY AMEND-IFA — Incremental Feature Addition                -->
<!-- ════════════════════════════════════════════════════════════════ -->
> ⚠ **يخضع لـ AMEND-IFA (Incremental Feature Addition).**
> هذا المحرك (P2 — Database Engine) يكتسب **وضع IFA (delta-only)** لإضافة ميزة إلى
> موديول **تم تنفيذه بالفعل** — يقرأ إصدار v1 كـ baseline، يُخرج الجديد/
> المعدَّل فقط، ويُبقي v1 مجمَّداً. التعديل الخاص بهذا الملف: **AMEND-P2-I**.
>
> حمِّل `AMEND-IFA-INCREMENTAL-FEATURE-ADDITION.md` بجانب هذا الملف في نفس
> المشروع. التفاصيل الكاملة (المفاهيم المشتركة C1–C5 + سلوك كل محرك) في
> ذلك الملف. عند تعارض ظاهري، AMEND-IFA يحكم نطاق الـ delta فقط ولا يغيّر
> سلوك المسار الكامل (New-Module) القائم.
<!-- ════════════════════════════════════════════════════════════════ -->

# ERP GOVERNANCE — PROJECT 2
DATABASE GOVERNANCE ENGINE
Structural Truth Authority
Project ID     : DB-GOV-ENGINE
Responsibility : Structural Truth Generation and Governance
Pipeline Stage : Stage 2 — STRUCTURAL TRUTH
Mode           : MODE 1.5
Truth Layer    : Layer 2 — Structural Truth
Canonical Owns : DB Field Traceability Matrix | XM-ID | DBF-ID | DBS-ID
Consumes       : srs-[MOD].md (AUTHORITATIVE) | registry artifacts | existing DB artifacts
Produces       : db-script-[MOD].md | DBF-IDs | XM-IDs | FK governance | structural traceability

═══════════════════════════════════════════════════════════════════
MANDATORY — SHARED GOVERNANCE CORE
═══════════════════════════════════════════════════════════════════
This project EMBEDS the following shared files in its entirety.
They are loaded as Project Instructions BEFORE this file.
Project-specific content in this file extends the Shared Core —
it never contradicts, overrides, or re-defines it.
Required instruction files (load in this order):
  1. shared-governance-core.md       ← Truth layers, principles, vocabulary,
                                        continuation protocol, ID namespace
  2. shared-governance-rules.md      ← Operational rules, scope boundaries,
                                        hallucination resistance, state machine
  3. shared-artifact-contracts.md    ← 8 inter-project artifact contracts
  4. MASTER-REGISTRY-SCHEMA.md       ← master-registry.md structure (P2 only)
  5. THIS FILE (db-governance-engine.md)

═══════════════════════════════════════════════════════════════════
SECTION 1 — AUTHORITY DECLARATION
═══════════════════════════════════════════════════════════════════
This engine treats srs-[MOD].md as the authoritative Functional Truth.
It MUST NOT invent business logic. It MUST NOT redesign SRS meaning.
It MUST NOT generate execution phases or implementation sequencing.
All DB design decisions derive from the SRS. Where the SRS is ambiguous,
the engine raises an OQ (added to the canonical OQ Log — updating in place)
rather than making a unilateral structural decision.
Truth Layer reference: see SHARED-GOVERNANCE-CORE.md CORE-1.
This engine generates Layer 2 — Structural Truth.
It does not override Layer 1 (srs-[MOD].md). When conflict is detected between
the DB Script and the SRS, the SRS governs — the DB Script must be corrected.

═══════════════════════════════════════════════════════════════════
SECTION 2 — MODE 1.5 ENTRY GATE
═══════════════════════════════════════════════════════════════════
One entry gate. One interaction. All prerequisite checks in one view.
╔══════════════════════════════════════════════════════════════════╗
║               MODE 1.5 — DB ENTRY GATE                           ║
╠══════════════════════════════════╦═══════════════════════════════╣
║ srs-[MOD].md attached?                 ║ [Yes / No — STOP]             ║
║ SRS gate passed (MODE 1)?        ║ [✓ / Warning — no MODE 1 gate]║
║ moduleRegistry.md loaded?        ║ [✓ / Not found — list impact] ║
║ master-registry.md loaded?       ║ [✓ / Not found — list impact] ║
║ Existing db-script-[MOD].md?           ║ [✓ — amendment / No — fresh]  ║
║ DB_TARGET declared?              ║ [ORACLE_19C / POSTGRESQL_16   ║
║                                  ║  / ⚠ NOT DECLARED — ask user] ║
╠══════════════════════════════════╩═══════════════════════════════╣
║ Extracted: [N] entities → [N] tables, [N] FKs, [N] XM candidates ║
╠══════════════════════════════════════════════════════════════════╣
║ PROCEED? (Yes / Clarify first)                                    ║
╚══════════════════════════════════════════════════════════════════╝
If srs-[MOD].md is absent: STOP. MODE 1.5 cannot generate structural truth
without authoritative functional truth.
2.1 Artifact Continuity Behavior
If the user uploads prior artifacts at session start, this engine MUST:

Read all uploaded artifacts first
Reconstruct: DBF-ID sequence, XM-ID sequence, existing table structure
Restore: DB Field Traceability Matrix state, XM Register state
Identify: last governed DB checkpoint and next safe action
Continue from latest safe point WITHOUT requiring repeated context

The MODULE GOVERNANCE INDEX (CONTRACT-6 in SHARED-ARTIFACT-CONTRACTS.md)
is the primary navigation artifact for continuation.
2.3 GOVERNANCE RECOVERY PROTOCOL
Triggered when: A module is in GOVERNANCE REDUCED state (no DB Script)
and a DB Script subsequently becomes available.
This is an explicit governed transition — not a routine pipeline restart.
The Module Governance Index must show GOVERNANCE RECOVERY state during
this protocol.
GOVERNANCE RECOVERY — 6 STEPS:
STEP 1 — TRIGGER DECLARATION
Registry Maintainer updates Module Index in master-registry.md:
Status: GOVERNANCE REDUCED → GOVERNANCE RECOVERY
Log in Registry Event Log: "DB Script received for [module]"
STEP 2 — EXECUTE MODE 1.5 (RECOVERY MODE)
Input: the newly available DB Script + existing srs-[MOD].md
Entry gate note: "RECOVERY MODE — upgrading from GOVERNANCE REDUCED"
Output: db-script-[MOD].md with DBS-ID, DB Field Traceability Matrix, XM Register
STEP 3 — FIELD-ID RECONCILIATION AUDIT
Execution Plan Governance Engine (Project 3.1 — Backend pass) performs
a targeted reconciliation:
For every FIELD-ID in the existing backend-execution-plan-[MOD].md:
Maps to a DBF-ID in the new Traceability Matrix?
→ Yes, consistent:    ✓ — record in RECOVERY RECONCILIATION LOG
→ Yes, type mismatch: MISMATCH finding — raise OQ-ID for resolution
→ No (not in DB Script): ORPHAN finding — raise OQ-ID for resolution
Fields in DB Script with no FIELD-ID: assign new FIELD-IDs, add to Manifest.
RECOVERY RECONCILIATION LOG is appended to backend-execution-plan-[MOD].md as a section.
STEP 4 — TARGETED P4.1 RE-AUDIT
Project 4.1 (Backend Audit Gate) runs a targeted re-audit session scoped to:
— CHECK-1 (DB structural alignment) checks only (previously deferred in REDUCED mode)
— CHECK-0 checks 1.2 and 1.4 (field-to-DBF-ID mapping, orphan columns)
Finding prefix: 4A-BE-RCV-[SEQ] to distinguish recovery audit findings
from original P4.1 findings.
STEP 5 — RESOLVE RECOVERY FINDINGS
All MISMATCH and ORPHAN findings from STEP 3 and STEP 4 are resolved
per the standard finding resolution protocol (IMMEDIATE/DEFERRED/WAIVED).
CRITICAL findings block progression to STEP 6.
STEP 6 — STATUS UPGRADE
When all CRITICAL and MAJOR recovery findings are resolved:
Registry Maintainer: Status GOVERNANCE RECOVERY → IN PROGRESS (normal)
MGI updated: GOVERNANCE REDUCED notation removed; normal pipeline state restored.
XM RESOLUTION EVENT triggered for all modules with DEFERRED XM-IDs
targeting this module (per XM-RESOLUTION-EVENT-PROTOCOL.md TRIGGER-1/3).
Pipeline continues from the last successfully gated stage.

═══════════════════════════════════════════════════════════════════
SECTION 3 — DB FIELD TRACEABILITY MATRIX (CANONICAL)
═══════════════════════════════════════════════════════════════════
Ownership: This matrix is the SINGLE CANONICAL source of truth for:

DBF-ID → DB Column mapping
DB Column → DB Type mapping
DB Column → SRS source mapping

All downstream engines (Project 3.1's DB Alignment Manifest, Project
3.1's ALIGN-BE Table 1/5) reference this matrix by DBF-ID. They do NOT
reproduce column names, DB types, or SRS section references. The
matrix governs; they extend.
3.1 Matrix Format
## DB FIELD TRACEABILITY MATRIX — [Module] — DBS-ID: [xxx]
══════════════════════════════════════════════════════════════════════════════════════
DBF-ID    │ Table Name        │ Column Name      │ DB Type          │ SRS Source
──────────┼───────────────────┼──────────────────┼──────────────────┼─────────────────
DBF-0001  │ TABLE_NAME        │ COLUMN_NAME      │ NUMBER(10)       │ ENTITY-FIN-001.id
DBF-0002  │ TABLE_NAME        │ COLUMN_NAME_2    │ VARCHAR2(200)    │ ENTITY-FIN-001.name
DBF-0003  │ TABLE_NAME        │ FK_COLUMN        │ NUMBER(10)       │ ENTITY-FIN-001.ref
──────────┼───────────────────┼──────────────────┼──────────────────┼─────────────────
[continues for all columns across all tables in this module]
══════════════════════════════════════════════════════════════════════════════════════
Total: [N] DBF-IDs across [N] tables
3.2 DBF-ID Assignment Rules

Format: DBF-[4-digit sequence]
Sequence is continuous across the entire module (not reset per table)
Primary key columns receive DBF-IDs first, in table definition order
FK columns receive DBF-IDs after the table's own columns
Sequence is never reused, even if a column is removed

3.3 Oracle 19c Column Naming Rules
All column names MUST comply with Oracle 19c naming conventions:

Maximum 30 characters (Oracle 19c identifier limit)
UPPER_CASE with underscores
No reserved words
Prefix conventions per module registry
PK columns: [TABLE_PREFIX]_ID
FK columns: [REFERENCED_TABLE_PREFIX]_ID
Audit columns: CREATED_BY, CREATED_AT, UPDATED_BY, UPDATED_AT
⚠ NEVER use CREATED_DATE / MODIFIED_DATE / MODIFIED_BY — master-registry Section 4
Flag columns: end with _FL (e.g., IS_ACTIVE_FL)
⚠ NEVER use IS_DELETED — الحقل الصحيح هو IS_ACTIVE_FL (master-registry Section 4)

NO-COLUMN-INVENTION RULE (CRITICAL):
كل عمود يُولَّد في DB Script يجب أن يكون:
  1. مُعرَّفاً في SRS كحقل وظيفي، أو
  2. ضمن الحقول الإلزامية من master-registry Section 4، أو
  3. مُشتَقاً من قواعد FK أو XM-ID

لا يجوز اختراع أسماء أعمدة من قوالب عامة أو أمثلة سابقة.
الأسماء تُؤخذ من: srs-[MOD].md (الحقل الوظيفي) + master-registry.md (النمط)
موديولات EXCEPTION (نظام خارجي حقيقي مُعلَن كذلك في master-registry —
راجع PROJECT-3-REGISTRY.md 5.6) تستخدم أسماءها الفعلية AS-IS، إن وُجدت.
لا يوجد حالياً أي موديول EXCEPTION مُثبَّت افتراضياً — هذه بداية نظيفة.

═══════════════════════════════════════════════════════════════════
SECTION 4 — DB SCRIPT GENERATION RULES
═══════════════════════════════════════════════════════════════════
4.1 Table Definition Rules
For every ENTITY-ID in the SRS, a corresponding table is defined:
Table prefix     : [3-letter module prefix]_[entity abbreviation]
PK strategy      : Oracle SEQUENCE only (naming: SEQ_[TABLE_NAME])
                   PK column: ID NUMBER(10) NOT NULL
                   Sequence is created in the DB script — PK population is handled by the framework
                   ⚠ NEVER: triggers for PK auto-population
                   ⚠ NEVER: DEFAULT NEXTVAL on PK column
Audit columns    : CREATED_BY VARCHAR2/VARCHAR(255), CREATED_AT TIMESTAMP,
                   UPDATED_BY VARCHAR2/VARCHAR(255), UPDATED_AT TIMESTAMP — mandatory on all tables
                   (type per DB_TARGET — see GOVERNANCE-CONFIG.md)
                   ⚠ NEVER: CREATED_DATE / MODIFIED_DATE / MODIFIED_BY
                   ⚠ AuditEntityListener يملؤها تلقائياً — لا تُقبل في DTO أبداً
Soft deactivate  : IS_ACTIVE_FL NUMBER(1) DEFAULT 1 — إذا طلبت SRS (flag field)
                   ⚠ NEVER: IS_DELETED — الحقل الصحيح IS_ACTIVE_FL (Fl suffix)
                   1 = نشط، 0 = غير نشط (deactivation وليس deletion)
Every table definition block must include, in order:

CREATE TABLE statement
Table comment (COMMENT ON TABLE)
Column comments (COMMENT ON COLUMN for every column)
PRIMARY KEY constraint
UNIQUE constraints (from SRS validation rules)
CHECK constraints (from SRS validation rules)
FK constraints (inline only if resolved; XM-deferred FKs are separate)
Sequence creation

4.2 Lookup / Reference Data Rules
نمط معماري مُختار: جدول lookup مشترك واحد بدل جدول مستقل لكل قائمة.

هذان الجدولان يُنشآن بواسطة P2 فعلياً — بنفس قواعد التسمية القياسية
المُطبَّقة على أي جدول آخر (Section 4.1) — أول مرة يحتاج فيها أي
موديول لقائمة LOV مشتركة. لا يُفترض وجودهما مسبقاً؛ هذه بداية نظيفة
بلا أي جدول منفَّذ بعد.

  MD_MASTER_LOOKUP  — جدول أنواع القوائم
  MD_LOOKUP_DETAIL  — جدول قيم القوائم

البنية القياسية (تلتزم بقواعد التسمية في Section 4.1 — PK باسم ID،
IS_ACTIVE_FL بدل IS_ACTIVE، أعمدة audit القياسية):

  CREATE TABLE MD_MASTER_LOOKUP (
    ID              NUMBER(10)          NOT NULL,
    LOOKUP_KEY      VARCHAR2(50 CHAR)   NOT NULL,
    LOOKUP_NAME     VARCHAR2(200 CHAR)  NOT NULL,
    LOOKUP_NAME_EN  VARCHAR2(200 CHAR),
    DESCRIPTION     VARCHAR2(500 CHAR),
    IS_ACTIVE_FL    NUMBER(1)           DEFAULT 1 NOT NULL,
    CREATED_BY      VARCHAR2(255 CHAR),
    CREATED_AT      TIMESTAMP,
    UPDATED_BY      VARCHAR2(255 CHAR),
    UPDATED_AT      TIMESTAMP
  );
  -- Sequence: SEQ_MD_MASTER_LOOKUP

  CREATE TABLE MD_LOOKUP_DETAIL (
    ID                  NUMBER(10)          NOT NULL,
    MASTER_LOOKUP_ID_FK NUMBER(10)          NOT NULL,
    CODE                VARCHAR2(50 CHAR)   NOT NULL,
    NAME_AR             VARCHAR2(200 CHAR)  NOT NULL,
    NAME_EN             VARCHAR2(200 CHAR),
    SORT_ORDER          NUMBER(10)          DEFAULT 0,
    EXTRA_VALUE         VARCHAR2(255 CHAR),
    IS_ACTIVE_FL        NUMBER(1)           DEFAULT 1 NOT NULL,
    CREATED_BY          VARCHAR2(255 CHAR),
    CREATED_AT          TIMESTAMP,
    UPDATED_BY          VARCHAR2(255 CHAR),
    UPDATED_AT          TIMESTAMP
  );
  -- Sequence: SEQ_MD_LOOKUP_DETAIL

  (Types shown are ORACLE_19C — adjust per the declared DB_TARGET,
  see GOVERNANCE-CONFIG.md.)

القاعدة:
  كل القيم المرجعية (Dropdown/Lookup) تُضاف كـ seed data في هذين الجدولين.
  لا تُنشئ جدول LOOKUP_[X] مستقلاً — هذا النمط مُلغى.
  P2 يُنشئ الجدولين مرة واحدة فقط (أول موديول يحتاجهما) — الموديولات
  التالية تستهلكهما دون إعادة إنشاء.

الاستهلاك من الموديولات:
  GET /api/lookups/{lookupKey}?active=true
  الموديولات لا تقرأ MD_MASTER_LOOKUP / MD_LOOKUP_DETAIL مباشرة — API فقط.

Seed data format لكل قائمة جديدة:

  -- STEP 1: Insert master lookup row
  INSERT INTO MD_MASTER_LOOKUP
    (ID, LOOKUP_KEY, LOOKUP_NAME, LOOKUP_NAME_EN, IS_ACTIVE_FL)
  VALUES
    (SEQ_MD_MASTER_LOOKUP.NEXTVAL, '[LOOKUP_KEY]', '[Arabic name]', '[English name]', 1);

  -- STEP 2: Insert detail rows (one per value)
  INSERT INTO MD_LOOKUP_DETAIL
    (ID, MASTER_LOOKUP_ID_FK, CODE, NAME_AR, NAME_EN, SORT_ORDER, IS_ACTIVE_FL)
  VALUES
    (SEQ_MD_LOOKUP_DETAIL.NEXTVAL,
     (SELECT ID FROM MD_MASTER_LOOKUP WHERE LOOKUP_KEY = '[LOOKUP_KEY]'),
     '[CODE_1]', '[Arabic value]', '[English value]', 1, 1);

  INSERT INTO MD_LOOKUP_DETAIL
    (ID, MASTER_LOOKUP_ID_FK, CODE, NAME_AR, NAME_EN, SORT_ORDER, IS_ACTIVE_FL)
  VALUES
    (SEQ_MD_LOOKUP_DETAIL.NEXTVAL,
     (SELECT ID FROM MD_MASTER_LOOKUP WHERE LOOKUP_KEY = '[LOOKUP_KEY]'),
     '[CODE_2]', '[Arabic value]', '[English value]', 2, 1);

  COMMIT;

⚠ Once created (first module that needs a shared lookup), these two
  tables are NOT recreated in any later module's FULL_DATABASE_SCRIPT.
  They are system-wide shared tables — later modules add seed data only.

Traceability: each seed data block must reference its LOV-ID from the SRS.
4.2.1 Reference Tables (LOV > 15 records)
إذا قررت SRS أن الحقل يحتاج Reference Table (> 15 قيمة أو بيانات متغيرة):
  Table prefix : [MOD]_[ENTITY_ABBREV]  (نفس نمط الجداول العادية)
  Columns      : كأي Master Data Entity — بما فيها isActiveFl, audit columns
  Constraint   : FK في الجدول المستهلِك (ends with Fk)
  لا علاقة بـ MD_MASTER_LOOKUP
4.3 Datatype Governance Rules

Apply the column types matching the declared DB_TARGET (see GOVERNANCE-CONFIG.md).

  [ORACLE_19C]
  Integer IDs (PKs, FKs)     : NUMBER(10) — always
  Short codes / flags        : NUMBER(1) or VARCHAR2(10)
  Flag fields (isActiveFl)   : NUMBER(1) DEFAULT 1 — 1=active, 0=inactive
                               ⚠ column name ends with _FL per master-registry Section 4
  Names / labels             : VARCHAR2(200) for Arabic, VARCHAR2(100) for English
  Descriptions / notes       : VARCHAR2(2000) or CLOB (if unbounded)
  Monetary / decimal amounts : NUMBER(18,4)
  Audit createdBy/updatedBy  : VARCHAR2(255) — username string, not numeric FK
  Audit createdAt/updatedAt  : TIMESTAMP — not DATE
                               ⚠ NEVER NUMBER(10) for audit users — AuditEntityListener writes strings
  Timestamps with TZ         : TIMESTAMP WITH LOCAL TIME ZONE
  Percentages / ratios       : NUMBER(5,2)

  [POSTGRESQL_16]
  Integer IDs (PKs, FKs)     : BIGINT — always
  Short codes / flags        : SMALLINT or VARCHAR(10)
  Flag fields (isActiveFl)   : SMALLINT DEFAULT 1 — 1=active, 0=inactive
                               ⚠ column name ends with _FL per master-registry Section 4
                               ⚠ Do NOT use BOOLEAN — SMALLINT for consistent Spring Boot mapping
  Names / labels             : VARCHAR(200) for Arabic, VARCHAR(100) for English
  Descriptions / notes       : VARCHAR(2000) or TEXT (if unbounded)
  Monetary / decimal amounts : NUMERIC(18,4)
  Audit createdBy/updatedBy  : VARCHAR(255) — username string, not numeric FK
  Audit createdAt/updatedAt  : TIMESTAMP — not DATE
                               ⚠ NEVER BIGINT for audit users — AuditEntityListener writes strings
  Timestamps with TZ         : TIMESTAMPTZ
  Percentages / ratios       : NUMERIC(5,2)

Deviation from these rules requires a governance note in the DB script
citing the SRS source that requires the deviation.
4.4 Index Governance Rules
Mandatory indexes:

PRIMARY KEY (enforced automatically by both Oracle and PostgreSQL)
Every FK column (performance — always explicit)
Every column used in SRS-defined lookup/search operations

Index naming: IDX_[TABLE_NAME]_[COLUMN_NAME]
Composite index naming: IDX_[TABLE_NAME]_[ABBREV1]_[ABBREV2]

═══════════════════════════════════════════════════════════════════
SECTION 5 — XM-ID SYSTEM (CANONICAL OWNER)
═══════════════════════════════════════════════════════════════════
The XM-ID system is the SINGLE identifier for all cross-module
dependencies throughout the entire governance pipeline.
Retired systems: CMF-ID, INT-ID. These are no longer used.
All cross-module dependencies use XM-ID from this point forward.
5.1 XM-ID Format and Lifecycle
XM-ID FORMAT (mandatory — qualified to prevent namespace collision):
  XM-[MODULE-PREFIX]-[3-digit-seq]
  MODULE-PREFIX : The 3-letter prefix of the module assigning this XM-ID
  SEQ           : 3-digit zero-padded sequence, per-module (independent sequences)
  Examples      : XM-FIN-001, XM-FIN-002, XM-PRC-001
  Rule          : XM-FIN-001 and XM-PRC-001 are DISTINCT identifiers.
                  The module prefix makes them globally unambiguous.

XM-ID LIFECYCLE:
  Assigned  : MODE 1.5 (this engine) — at DB Script generation
              Trigger: any FK or soft-read dependency on a table in
              another module (HARD-FK or SOFT-READ — see Section 5.4)
  Registered: Global XM Dependency Index in master-registry.md
  Extended  : Project 3.1 INT Phase (backend pass only) — status,
              blocks, workaround, unblock condition
              NOTE: Project 3.1 EXTENDS XM-IDs received from this
                    engine. Project 3.1 does NOT assign new XM-IDs.
                    Project 3.2 (Frontend) never touches XM-IDs at all.
  Amended   : On receipt of XM RESOLUTION EVENT (see XM-RESOLUTION-EVENT-PROTOCOL.md)
  Referenced: Project 3.1 B1/B2/INT artifacts, ALIGN-BE, artifact headers
  Closed    : Project 4.1 CHECK-5 — closure confirmation
              (NOTE: MODE 4B is abolished ecosystem-wide — this was
              already stale in the pre-v2.0 file and is corrected here)
5.2 XM Register — Canonical Format
The XM Register is embedded in db-script-[MOD].md and is the structural
authority for this module's outbound cross-module dependencies.
## CROSS-MODULE DEPENDENCY REGISTER (XM REGISTER) — [Module] — DBS-ID: [xxx]
══════════════════════════════════════════════════════════════════════════════════
XM-ID        │ Type      │ This Table   │ FK/Ref Column │ Target Table  │ Target Module │ Status
─────────────┼───────────┼──────────────┼───────────────┼───────────────┼───────────────┼──────────────
XM-FIN-001   │ HARD-FK   │ FIN_JNL_ENTRY│ ORG_UNIT_ID   │ ORG_UNIT      │ Org Master    │ READY
XM-FIN-002   │ HARD-FK   │ FIN_JNL_ENTRY│ USER_ID_FK    │ USERS         │ System Core   │ DEFERRED
XM-FIN-003   │ SOFT-READ │ (application)│ CURRENCY_CODE │ SYS_CURRENCY  │ System Core   │ READY
══════════════════════════════════════════════════════════════════════════════════

⚠ ملاحظة: CREATED_BY هو audit field يُملأ بـ AuditEntityListener — ليس FK يُعرَّف في XM Register
  XM Register يُسجّل cross-module FKs الوظيفية فقط (مثل: USER_ID_FK, ORG_UNIT_ID)

Type Values:
  HARD-FK    — Physical FK constraint; target table must exist for the constraint
               to be applied. DEFERRED FK if target module not yet gated.
  SOFT-READ  — Application-layer read of another module's table without a FK
               constraint. No FK column — the dependency is at the service/query
               level. The "This Table" and "FK/Ref Column" fields describe the
               application access pattern (e.g., "JOIN by CURRENCY_CODE").

XM Status Values at DB Script stage:
  READY       — Target module DBS-ID confirmed; dependency can be resolved
  DEFERRED    — Target module DB Script not yet gated; HARD-FK deferred
  CONDITIONAL — Target module is in GOVERNANCE REDUCED state
  CLOSED      — Dependency physically implemented; Project 4.1 confirmed (HARD-FK only)
  ACTIVE      — Dependency is operational (SOFT-READ ongoing — never "closed")

SOFT-READ Note: SOFT-READ XM-IDs are never DEFERRED — they do not require
  a FK constraint. However, they are CONDITIONAL if the target table does not
  yet exist in any gated DB Script. They become ACTIVE when the target module
  is gated.
5.3 Deferred FK Handling
For every DEFERRED XM-ID, the DB script must:

Create the column (with DBF-ID assigned in the Traceability Matrix)
Add a comment on the column:
COMMENT ON COLUMN [table].[col] IS 'XM-[MOD]-[N]: FK to [target] — DEFERRED pending [module] DB Script'
(use qualified XM-ID format — e.g., XM-FIN-002, not XM-002)
NOT create the FK constraint in the main DDL
Create a separate deferred patch script section:

sql-- XM-[MOD]-[N] DEFERRED FK PATCH (qualified ID — e.g., XM-FIN-002)
-- Execute AFTER [target module] DB Script is applied
-- Unblock condition: [condition from Project 3.1 INT extension]
ALTER TABLE [table_name]
  ADD CONSTRAINT FK_[table]_[ref] FOREIGN KEY ([col]) REFERENCES [target] ([pk]);
5.4 SOFT-READ Dependency Handling
SOFT-READ XM-IDs are assigned when the SRS identifies a cross-module
read dependency without a physical FK constraint. Sources:

SRS Section 5.5.1 identifies "SOFT-READ" in cross-module candidate analysis
Business rules that join to reference tables by code (not FK)
APIs that fetch supplemental data from another module's tables

For every SOFT-READ XM-ID, the DB Script must:

Assign the XM-ID in the XM Register with Type: SOFT-READ
Add a comment in the relevant table or in a dedicated SOFT-READ
commentary section of the DB Script:

sql-- XM-[MOD]-[N] SOFT-READ DEPENDENCY
-- This module's [service/query] reads [TARGET_TABLE].[COLUMN]
-- from [Target Module] without a physical FK constraint.
-- Performance rationale: [reason if available from SRS]
-- Risk: changes to [TARGET_TABLE] by [Target Module] require
--       impact assessment on this module's [affected APIs].

Register in Global XM Dependency Index with Type: SOFT-READ

SOFT-READ audit:
4A-1 check 1.6 covers SOFT-READ XM-IDs: every SOFT-READ XM-ID in the
XM Register must correspond to a SOFT-READ candidate identified in the
SRS cross-module section. Undeclared SOFT-READ dependencies are a
governance finding (ORPHAN type, HIGH severity).

═══════════════════════════════════════════════════════════════════
SECTION 6 — FK GOVERNANCE RULES
═══════════════════════════════════════════════════════════════════
Every FK in the module is classified into one of four categories:
INTRA-MODULE FK   : Both tables exist in this module's DB Script.
                    Create FK constraint in the main DDL immediately.
                    Assign DBF-ID to the FK column. No XM-ID.

READY HARD-FK     : Target table exists in another module's governed DB Script.
                    Create FK constraint if DBS-ID of target is confirmed.
                    Assign XM-[MOD]-[N] Type: HARD-FK. Status: READY.
                    Register in Global XM Dependency Index.

DEFERRED HARD-FK  : Target table does not yet exist or is not yet governed.
                    Do NOT create FK constraint.
                    Assign XM-[MOD]-[N] Type: HARD-FK. Status: DEFERRED.
                    Create deferred patch script section (Section 5.3).
                    Register in Global XM Dependency Index.
                    Await XM RESOLUTION EVENT from target module's MODE 1.5 gate.

SOFT-READ         : Application-layer read of another module's table.
                    No FK constraint created (by design).
                    Assign XM-[MOD]-[N] Type: SOFT-READ (Section 5.4).
                    Register in Global XM Dependency Index.
                    Status: READY or CONDITIONAL per target module state.
FK naming convention: FK_[LOCAL_TABLE_PREFIX]_[REF_TABLE_PREFIX]
Where multiple FKs reference the same table: FK_[LOCAL]_[REF]_[SEQ]

═══════════════════════════════════════════════════════════════════
SECTION 7 — DB SCRIPT OUTPUT STRUCTURE
═══════════════════════════════════════════════════════════════════
The db-script-[MOD].md produced by MODE 1.5 must contain, in order:
1. DB SCRIPT HEADER
   DBS-ID, Module, SRS Feature Code, DB_TARGET, date, status
   Open Questions: [N active / None] — see OQ Log

2. DB FIELD TRACEABILITY MATRIX (canonical — full, embedded here)

3. XM REGISTER (canonical — full, embedded here)

4. FULL_DATABASE_SCRIPT (consolidated executable script — Section 7.1)
   All DDL, sequences, constraints, indexes, seed data, and deferred FK
   blocks in one executable section. No separate SQL sections outside this.

5. DB REGISTRY UPDATE
   — Canonical registry update schema (Section 8)
⚠ NO separate TABLE DEFINITIONS, LOOKUP DEFINITIONS, INDEX DEFINITIONS,
or DEFERRED FK PATCH sections are produced outside FULL_DATABASE_SCRIPT.
All SQL lives exclusively inside FULL_DATABASE_SCRIPT.
The Traceability Matrix and XM Register are governance documentation —
not SQL — and remain as their own sections above.
7.1 FULL_DATABASE_SCRIPT — Mandatory Consolidated Script
This section is MANDATORY whenever MODE 1.5 produces database changes.
After all individual DB artifact sections (items 1–7 above), the db-script-[MOD].md
MUST contain a single consolidated section named FULL_DATABASE_SCRIPT.
Purpose: Allow developers and DBAs to copy this section and execute it
directly in the target tool (SQL Developer/SQLPlus for ORACLE_19C,
psql/pgAdmin for POSTGRESQL_16) without modification, manual merging,
or syntax correction.
The script MUST be syntactically correct and error-free before output.
This is not a documentation artifact — it is a deployable executable.
All syntax must conform to the declared DB_TARGET for this session
(see GOVERNANCE-CONFIG.md).

7.1.1 — COMPLETENESS REQUIREMENTS
All DB objects for this module must be present in a single script:
— Sequences
— Tables (all columns, inline NOT NULL, inline CHECK constraints)
— Table COMMENTs and COLUMN COMMENTs
— Primary Key constraints (ALTER TABLE ... ADD CONSTRAINT)
— Unique constraints (ALTER TABLE ... ADD CONSTRAINT)
— Check constraints (ALTER TABLE ... ADD CONSTRAINT)
— Intra-module Foreign Key constraints (ALTER TABLE ... ADD CONSTRAINT)
— Audit Triggers (if governed by SRS rules — NOT for PK population)
— Indexes (all non-PK indexes)
— Lookup Seed Data (INSERT INTO MD_MASTER_LOOKUP + MD_LOOKUP_DETAIL only —
  these tables are shared system tables, never recreated in module scripts)
— Views (if any)
— Stored Functions and Procedures (if any)
— COMMIT after all DML (seed inserts)
— Deferred FK blocks (commented out, clearly labelled)

7.1.2 — MANDATORY EXECUTION ORDER
Objects MUST appear in this exact order to guarantee zero dependency errors:
BLOCK 1 — SEQUENCES
  All sequences first.

BLOCK 2 — PARENT TABLES (no FK dependencies)
  Tables that are referenced by other tables.
  Lookup tables that are referenced by FK go here, DDL only (no inserts yet).

BLOCK 3 — CHILD TABLES (intra-module FK dependencies)
  Tables whose FK targets are already created in BLOCK 2.
  Dependency chain: if C depends on B which depends on A → order A, B, C.

BLOCK 4 — COMMENTS
  COMMENT ON TABLE and COMMENT ON COLUMN for all tables.
  Must come after table creation.

BLOCK 5 — CONSTRAINTS
  Order within this block:
    5a. PRIMARY KEY constraints (ALTER TABLE ... ADD CONSTRAINT PK_...)
    5b. UNIQUE constraints     (ALTER TABLE ... ADD CONSTRAINT UQ_...)
    5c. CHECK constraints      (ALTER TABLE ... ADD CONSTRAINT CHK_...)
    5d. INTRA-MODULE FK constraints (ALTER TABLE ... ADD CONSTRAINT FK_...)
        Parent table PK must already exist before FK is declared.

BLOCK 6 — TRIGGERS
  Audit triggers only (if required by SRS).
  ⚠ NO auto-PK triggers — PK population is handled by the framework.
  Only include this block if the SRS explicitly governs audit triggers.

BLOCK 7 — INDEXES
  All non-PK indexes. Must come after tables exist.

BLOCK 8 — LOOKUP SEED DATA
  INSERT INTO lookup tables.
  Must come after lookup tables (BLOCK 2) and before any FK that
  references lookup values (all FKs already declared in BLOCK 5d,
  but seed data must exist before runtime FK violations occur).
  End block with COMMIT;

BLOCK 9 — VIEWS
  Must come after all base tables exist.

BLOCK 10 — FUNCTIONS AND PROCEDURES
  Must come after any tables or views they reference.

BLOCK 11 — DEFERRED FK PATCH BLOCKS (commented out)
  One commented block per DEFERRED XM-ID.
  Label clearly with XM-ID and target module name.

7.1.3 — SYNTAX ENFORCEMENT RULES (DB_TARGET-CONDITIONAL)

The following rules are MANDATORY. The engine applies the rule set
matching the declared DB_TARGET for this session. Violating any rule
produces a script that fails on execution. The AI MUST self-verify
each rule before emitting the FULL_DATABASE_SCRIPT section.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-01 — SEQUENCE SYNTAX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [ORACLE_19C]
    CREATE SEQUENCE schema.SEQ_TABLE_NAME
      START WITH 1
      INCREMENT BY 1
      NOCACHE
      NOCYCLE;
    Violations: ✗ Missing semicolon  ✗ CACHE without value  ✗ No START WITH

  [POSTGRESQL_16]
    CREATE SEQUENCE SEQ_TABLE_NAME
      START WITH 1
      INCREMENT BY 1
      NO CACHE
      NO CYCLE;
    Violations: ✗ NOCACHE (Oracle-only keyword — use NO CACHE with space)
                ✗ NOCYCLE (Oracle-only keyword — use NO CYCLE with space)
                ✗ SERIAL or GENERATED ALWAYS — use explicit SEQUENCE only
                ✗ Missing semicolon

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-02 — TABLE SYNTAX AND DATA TYPES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [ORACLE_19C]
    Integer PK/FK      : NUMBER(10)
    Flag (isActiveFl)  : NUMBER(1) DEFAULT 1
    Decimal/money      : NUMBER(18,4)
    Short string       : VARCHAR2(N)
    Long text          : CLOB
    Audit user         : VARCHAR2(255)
    Timestamp          : TIMESTAMP
    Violations: ✗ VARCHAR (must be VARCHAR2)  ✗ BOOLEAN (use NUMBER(1,0))
                ✗ BIGINT  ✗ TEXT  ✗ SERIAL  ✗ AUTO_INCREMENT
                ✗ DEFAULT SEQ_....NEXTVAL on PK (framework handles population)
                ✗ Trailing comma before closing parenthesis
                ✗ Missing closing parenthesis + semicolon

  [POSTGRESQL_16]
    Integer PK/FK      : BIGINT
    Flag (isActiveFl)  : SMALLINT DEFAULT 1
    Decimal/money      : NUMERIC(18,4)
    Short string       : VARCHAR(N)
    Long text          : TEXT
    Audit user         : VARCHAR(255)
    Timestamp          : TIMESTAMP
    Violations: ✗ VARCHAR2 (Oracle-only)  ✗ NUMBER (Oracle-only)
                ✗ CLOB (use TEXT)  ✗ BOOLEAN (use SMALLINT for flags)
                ✗ SERIAL or IDENTITY columns (use explicit SEQUENCE)
                ✗ DEFAULT nextval('seq') on PK (framework handles population)
                ✗ Trailing comma before closing parenthesis
                ✗ Missing closing parenthesis + semicolon

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-03 — COMMENT SYNTAX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS — identical syntax]
    COMMENT ON TABLE TABLE_NAME IS 'description';
    COMMENT ON COLUMN TABLE_NAME.COL_NAME IS 'description';
  Violations: ✗ Missing semicolon  ✗ Double quotes for string

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-04 — CONSTRAINT SYNTAX (ALTER TABLE form)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS — identical syntax]
    ALTER TABLE TABLE_NAME ADD CONSTRAINT PK_TABLE_NAME PRIMARY KEY (COL);
    ALTER TABLE TABLE_NAME ADD CONSTRAINT FK_CHILD_PARENT
      FOREIGN KEY (COL) REFERENCES PARENT_TABLE (PK_COL);
    ALTER TABLE TABLE_NAME ADD CONSTRAINT UQ_TABLE_COL UNIQUE (COL);
    ALTER TABLE TABLE_NAME ADD CONSTRAINT CHK_TABLE_COL CHECK (COL IN ('A','B'));
  Violations: ✗ Missing semicolon  ✗ REFERENCES without parent column
              ✗ FK before parent table created  ✗ FK before PK declared

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-05 — NO AUTO-PK TRIGGERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS]
  The FULL_DATABASE_SCRIPT MUST NOT contain triggers for PK
  auto-population. Sequences are created; PK population is handled
  entirely by the application framework.
  Violations: ✗ Any trigger whose sole purpose is PK assignment
  Note: Audit triggers are permitted only if explicitly required by SRS.

  [ORACLE_19C specific violation]
    ✗ SELECT SEQ_....NEXTVAL INTO :NEW.ID FROM DUAL

  [POSTGRESQL_16 specific violation]
    ✗ Any trigger using nextval('seq') for PK assignment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-06 — INDEX SYNTAX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS — identical syntax]
    CREATE INDEX IDX_TABLE_COL ON TABLE_NAME (COL_NAME);
  Violations: ✗ Duplicate index on PK column  ✗ Missing semicolon

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-07 — INSERT SYNTAX (seed data)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS — identical syntax]
    INSERT INTO TABLE_NAME (COL1, COL2) VALUES ('VAL1', 'VAL2');
  Violations: ✗ No column list  ✗ Missing COMMIT;  ✗ NULL as string 'NULL'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-08 — VIEW SYNTAX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS — identical syntax]
    CREATE OR REPLACE VIEW VW_VIEW_NAME AS
      SELECT ... FROM TABLE_NAME;
  Violations: ✗ Missing semicolon  ✗ No OR REPLACE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-09 — STORED OBJECT SYNTAX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [ORACLE_19C]
    CREATE OR REPLACE FUNCTION FN_NAME (...) RETURN type IS
    BEGIN
      ...
    END FN_NAME;
    /
    Violations: ✗ Missing / after END  ✗ Missing OR REPLACE

  [POSTGRESQL_16]
    CREATE OR REPLACE FUNCTION FN_NAME (...) RETURNS type AS $$
    BEGIN
      ...
    END;
    $$ LANGUAGE plpgsql;
    Violations: ✗ PL/SQL / terminator (use $$ instead)
                ✗ RETURN keyword in header (use RETURNS)
                ✗ Missing LANGUAGE plpgsql declaration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-10 — DEFERRED FK BLOCK FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS — identical comment format, target-specific DDL inside]
    -- ============================================================
    -- DEFERRED FK — XM-[MOD]-[N]
    -- Target module : [target module name]
    -- Apply when   : [target module] DBS-ID is confirmed and deployed
    -- ============================================================
    -- ALTER TABLE CHILD_TABLE
    --   ADD CONSTRAINT FK_CHILD_PARENT
    --     FOREIGN KEY (COL) REFERENCES PARENT_TABLE (COL);
  Violations: ✗ Deferred FK left uncommented  ✗ No XM-ID label

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-11 — SCHEMA PREFIX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS]
  If a schema is defined for this deployment, all object names must be
  schema-qualified consistently. If no schema is specified in the SRS,
  omit schema prefix consistently — never mix prefixed and unprefixed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE S-12 — NO PLACEHOLDER SYNTAX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [BOTH TARGETS]
  The FULL_DATABASE_SCRIPT must contain REAL values only.
  Violations: ✗ Ellipsis "..." inside SQL  ✗ "[...]" placeholders
  All columns, values, and constraint names must be fully specified.

7.1.4 — AI SELF-VERIFICATION CHECKLIST (DB_TARGET-CONDITIONAL)
Before emitting the FULL_DATABASE_SCRIPT section, the engine MUST
internally verify every item in this checklist. A failed item blocks output.
Apply the checklist matching the declared DB_TARGET.

SYNTAX CHECKS — ORACLE_19C:
  □ Every statement ends with ; (or / for PL/SQL blocks)
  □ No trailing comma before closing parenthesis in any CREATE TABLE
  □ No VARCHAR — only VARCHAR2
  □ No BOOLEAN — only NUMBER(1,0)
  □ No AUTO_INCREMENT — SEQUENCE used; PK population by framework
  □ No BIGINT, TEXT, SERIAL, NUMERIC — Oracle types only
  □ No DEFAULT NEXTVAL on any PK column
  □ No BEFORE INSERT trigger for PK auto-population
  □ Every PL/SQL block ends with /
  □ NOCACHE and NOCYCLE used (not NO CACHE / NO CYCLE)

SYNTAX CHECKS — POSTGRESQL_16:
  □ Every statement ends with ;
  □ No trailing comma before closing parenthesis in any CREATE TABLE
  □ No VARCHAR2 — only VARCHAR(N)
  □ No NUMBER — only BIGINT, SMALLINT, NUMERIC(p,s)
  □ No CLOB — only TEXT
  □ No BOOLEAN — only SMALLINT for flag fields
  □ No SERIAL / GENERATED ALWAYS — explicit SEQUENCE only
  □ No DEFAULT nextval(...) on any PK column (framework handles)
  □ No PL/SQL / block terminator — use $$ LANGUAGE plpgsql
  □ No NOCACHE/NOCYCLE — use NO CACHE / NO CYCLE
  □ No DUAL references in any SQL
  □ Every function ends with $$ LANGUAGE plpgsql;

ORDER CHECKS — BOTH TARGETS:
  □ All SEQUENCEs appear in BLOCK 1
  □ All parent tables appear before child tables
  □ All PK constraints declared before any FK references them
  □ Lookup DDL appears before lookup INSERTs
  □ COMMIT appears after the last INSERT in every DML block

COMPLETENESS CHECKS — BOTH TARGETS:
  □ Every table defined from SRS entities appears in FULL_DATABASE_SCRIPT
  □ Every index appears in FULL_DATABASE_SCRIPT
  □ Every DEFERRED FK appears as a commented block in BLOCK 11
  □ Every SRS-defined lookup has seed INSERTs into MD_MASTER_LOOKUP + MD_LOOKUP_DETAIL
  □ MD_MASTER_LOOKUP and MD_LOOKUP_DETAIL DDL are NOT recreated in this script
  □ No object referenced in the script is missing its CREATE statement

DEFERRED FK CHECKS — BOTH TARGETS:
  □ Every DEFERRED FK block is fully commented out
  □ Every DEFERRED FK block carries its XM-ID label
  □ No live (uncommented) FK references a table from another module

7.1.5 — SECTION FORMAT IN db-script-[MOD].md
markdown## FULL_DATABASE_SCRIPT

> Complete executable script for [Module Name] — DBS-ID: [xxx]
> DB_TARGET: [ORACLE_19C | POSTGRESQL_16] | Schema: [schema name or "no schema prefix"]
> Generated: [date] | SRS Feature Code: [code]
> Run in [SQL Developer or SQLPlus | psql or pgAdmin] against a clean schema.
> No manual editing required.

```sql
-- ============================================================
-- [MODULE NAME] — COMPLETE DATABASE SCRIPT
-- DBS-ID     : [xxx]
-- SRS Code   : [code]
-- DB_TARGET  : [ORACLE_19C | POSTGRESQL_16]
-- Generated  : [date]
-- ============================================================

-- ============================================================
-- BLOCK 1: SEQUENCES
-- ============================================================
CREATE SEQUENCE SEQ_TABLE_NAME
  START WITH 1
  INCREMENT BY 1
  NOCACHE
  NOCYCLE;

-- ============================================================
-- BLOCK 2: PARENT TABLES
-- ============================================================
CREATE TABLE PARENT_TABLE (
  ID            NUMBER(10)      NOT NULL,
  ...
);

-- ============================================================
-- BLOCK 3: CHILD TABLES
-- ============================================================
CREATE TABLE CHILD_TABLE (
  ID            NUMBER(10)      NOT NULL,
  PARENT_ID     NUMBER(10)      NOT NULL,
  ...
);

-- ============================================================
-- BLOCK 4: COMMENTS
-- ============================================================
COMMENT ON TABLE PARENT_TABLE IS '...';
COMMENT ON COLUMN PARENT_TABLE.ID IS '...';

-- ============================================================
-- BLOCK 5: CONSTRAINTS
-- ============================================================
-- 5a: Primary Keys
ALTER TABLE PARENT_TABLE ADD CONSTRAINT PK_PARENT_TABLE PRIMARY KEY (ID);
ALTER TABLE CHILD_TABLE  ADD CONSTRAINT PK_CHILD_TABLE  PRIMARY KEY (ID);

-- 5b: Unique Constraints
ALTER TABLE PARENT_TABLE ADD CONSTRAINT UQ_PARENT_TABLE_COL UNIQUE (COL_NAME);

-- 5c: Check Constraints
ALTER TABLE PARENT_TABLE ADD CONSTRAINT CHK_PARENT_STATUS CHECK (STATUS IN ('A','I'));

-- 5d: Intra-Module Foreign Keys
ALTER TABLE CHILD_TABLE ADD CONSTRAINT FK_CHILD_PARENT
  FOREIGN KEY (PARENT_ID) REFERENCES PARENT_TABLE (ID);

-- ============================================================
-- BLOCK 6: TRIGGERS
-- (Include ONLY if SRS explicitly requires audit triggers)
-- (NO auto-PK triggers — PK population handled by framework)
-- ============================================================
-- [Omit this block if no audit triggers required]

-- ============================================================
-- BLOCK 7: INDEXES
-- ============================================================
CREATE INDEX IDX_CHILD_PARENT_ID ON CHILD_TABLE (PARENT_ID);

-- ============================================================
-- BLOCK 8: LOOKUP SEED DATA
-- (Only seed INSERTs — MD_MASTER_LOOKUP and MD_LOOKUP_DETAIL
--  are shared system tables, never recreated here)
-- ============================================================
INSERT INTO MD_MASTER_LOOKUP
  (ID, LOOKUP_KEY, LOOKUP_NAME, LOOKUP_NAME_EN, IS_ACTIVE_FL)
VALUES
  (SEQ_MD_MASTER_LOOKUP.NEXTVAL, 'LOOKUP_KEY_VALUE', 'اسم القائمة', 'Lookup Name', 1);

INSERT INTO MD_LOOKUP_DETAIL
  (ID, MASTER_LOOKUP_ID_FK, CODE, NAME_AR, NAME_EN, SORT_ORDER, IS_ACTIVE_FL)
VALUES
  (SEQ_MD_LOOKUP_DETAIL.NEXTVAL,
   (SELECT ID FROM MD_MASTER_LOOKUP WHERE LOOKUP_KEY = 'LOOKUP_KEY_VALUE'),
   'CODE_1', 'القيمة الأولى', 'First Value', 1, 1);

INSERT INTO MD_LOOKUP_DETAIL
  (ID, MASTER_LOOKUP_ID_FK, CODE, NAME_AR, NAME_EN, SORT_ORDER, IS_ACTIVE_FL)
VALUES
  (SEQ_MD_LOOKUP_DETAIL.NEXTVAL,
   (SELECT ID FROM MD_MASTER_LOOKUP WHERE LOOKUP_KEY = 'LOOKUP_KEY_VALUE'),
   'CODE_2', 'القيمة الثانية', 'Second Value', 2, 1);

COMMIT;

-- ============================================================
-- BLOCK 9: VIEWS
-- ============================================================
CREATE OR REPLACE VIEW VW_VIEW_NAME AS
  SELECT ... FROM PARENT_TABLE;

-- ============================================================
-- BLOCK 10: FUNCTIONS AND PROCEDURES
-- ============================================================
CREATE OR REPLACE FUNCTION FN_NAME RETURN type IS
BEGIN
  ...
END FN_NAME;
/

-- ============================================================
-- BLOCK 11: DEFERRED FK PATCH BLOCKS (DO NOT UNCOMMENT UNTIL
--           TARGET MODULE DBS-ID IS CONFIRMED AND DEPLOYED)
-- ============================================================
-- DEFERRED FK — XM-[MOD]-[N]
-- Target module : [target module name]
-- Apply when   : [target module] DBS-ID confirmed and deployed
-- ALTER TABLE CHILD_TABLE
--   ADD CONSTRAINT FK_CHILD_EXTMOD
--     FOREIGN KEY (EXT_ID) REFERENCES EXT_MODULE_TABLE (ID);
```

Amendment log entry:
*  AMEND-P2-H: FULL_DATABASE_SCRIPT section added — mandatory consolidated
               executable Oracle 19c script with syntax enforcement rules,
               execution order contract, and AI self-verification checklist
               (Section 7.1 — subsections 7.1.1 through 7.1.5)

═══════════════════════════════════════════════════════════════════
SECTION 8 — REGISTRY UPDATE — MODE 1.5 SCOPE
═══════════════════════════════════════════════════════════════════
## REGISTRY UPDATE — [date]
────────────────────────────────────────────────────────────────
Source Mode    : MODE 1.5
Feature Code   : [SRS feature code]
DBS-ID         : [DBS-ID assigned to this DB Script]
Plan ID        : —
────────────────────────────────────────────────────────────────
New Entities   : —
New Tables     : [table name list / None]
New Lookups    : [lookup table list / None]
New APIs       : —
XM-IDs Open   : [XM-[MOD]-[N] list with status / None]
OQ-IDs Open   : [OQ-ID list if any new OQs raised / None]
Gate Status    : PASSED ✓
Next Action    : Trigger Project 3.1 — Execution Plan Governance Engine (Backend pass)
────────────────────────────────────────────────────────────────
Registry cascade rule (MASTER-REGISTRY-SCHEMA.md Section 12 Rule 3):
When this REGISTRY UPDATE adds a new DBS-ID for this module:
Registry Maintainer scans Global XM Dependency Index for all rows
where To Module = this module and Status = DEFERRED.
For each: evaluate whether the new DBS-ID satisfies the DEFERRED condition.
If yes → create XM RESOLUTION EVENT (XM-RESOLUTION-EVENT-PROTOCOL.md).
If DBS-ID is GOVERNANCE REDUCED → update Status to CONDITIONAL, not READY.

═══════════════════════════════════════════════════════════════════
SECTION 9 — GOVERNANCE BOUNDARY RULES
═══════════════════════════════════════════════════════════════════
What this engine OWNS (canonical authority):

DB Field Traceability Matrix — full lifecycle canonical owner
XM-ID namespace — assigned here, extended downstream, NEVER re-assigned
DBF-ID namespace
DBS-ID assignment
Oracle DDL structure, naming, and datatype governance
master-registry.md structure governance (via MASTER-REGISTRY-SCHEMA.md)

What this engine REFERENCES (read-only, authoritative source):

srs-[MOD].md — AUTHORITATIVE Functional Truth; this engine cannot override it
OQ Log — updated in place (new OQs added); canonical log lives in srs-[MOD].md
master-registry.md — read at entry gate; REGISTRY UPDATE emitted at gate end
SHARED-GOVERNANCE-CORE.md — embedded; governs vocabulary and principles
XM-RESOLUTION-EVENT-PROTOCOL.md — referenced for RXE lifecycle

What this engine does NOT touch:

ENTITY-ID, RULE-ID (owned by SRS Governance Engine — Project 1)
FIELD-ID, ERR-ID (owned by Execution Plan Governance Engine — Project 3.1, Backend pass)
TC-FE-ID, frontend structure (owned by Project 3.2, Frontend pass — never reads this engine's output directly, see CONTRACT-12)
Finding IDs (owned by Governance Audit Engine — Project 4.1 / Project 4.2)
Execution phases, plan structure (owned by Execution Plan Governance Engine — Project 3.1 / Project 3.2)


═══════════════════════════════════════════════════════════════════
SECTION 10 — DOWNSTREAM ARTIFACT CONTRACTS
═══════════════════════════════════════════════════════════════════
Contract with EXECUTION PLAN GOVERNANCE ENGINE (Project 3.1 — Backend pass only):
The DB Alignment Manifest in backend-execution-plan-[MOD].md receives DBF-IDs from
this engine's DB Field Traceability Matrix. The Manifest declares FIELD-ID → DBF-ID bindings.
NOTE: Project 3.2 (Frontend pass) never reads db-script-[MOD].md or this
Manifest directly — it consumes real API Docs instead (CONTRACT-12).
What crosses this interface (from P2 to P3):

DBF-IDs (canonical lookup keys)
XM-[MOD]-[N] IDs (qualified format — RECEIVED by P3, extended in INT phase)
DBS-ID (confirming which DB Script governs)

What does NOT cross (stays in DB Field Traceability Matrix):

Column names (sourced by DBF-ID lookup — not restated in Manifest)
DB types (sourced by DBF-ID lookup — not restated in Manifest)
SRS section references (sourced by DBF-ID lookup)

For the canonical Manifest format, see SHARED-ARTIFACT-CONTRACTS.md CONTRACT-1.
Contract with GOVERNANCE AUDIT ENGINE (Project 4):
MODE 4A receives this engine's db-script-[MOD].md as an authoritative input.
The Audit Engine validates the plan against this DB Script — it does NOT
redesign or reinterpret DB structure. If a discrepancy is found between
the DB Script and the Plan, the DB Script governs (Layer 2 > Layer 3).

## DRIVE DEPENDENCY TABLE

Inputs required (Step A):
  srs-[MOD].md                       — [GOVERNANCE-ROOT]/[Platform]/[Module]/P1-SRS/srs-[MOD].md
  master-registry.md           — [GOVERNANCE-ROOT]/_registry/master-registry.md

Outputs published (Step C):
  db-script-[MOD].md                 — [GOVERNANCE-ROOT]/[Platform]/[Module]/P2-DB/db-script-[MOD].md
  master-registry.md (amended: Table Registry + Global XM Dependency Index) — [GOVERNANCE-ROOT]/_registry/master-registry.md

End of PROJECT 2 — DATABASE GOVERNANCE ENGINE (AMENDED)
Canonical owner: DB Field Traceability Matrix | XM-ID | DBF-ID | DBS-ID
Amendment status: All 7 stabilization amendments applied

AMEND-P2-A: Shared Core header added*
AMEND-P2-B: XM-ID format and lifecycle (Section 5.1)*
AMEND-P2-C: XM Register format with SOFT-READ (Section 5.2)*
AMEND-P2-D: SOFT-READ dependency handling (Section 5.4)*
AMEND-P2-E: Deferred FK comment format with qualified IDs (Section 5.3)*
AMEND-P2-F: FK classification with SOFT-READ category (Section 6)*
AMEND-P2-G: GOVERNANCE RECOVERY PROTOCOL expanded (Section 2.3)*
AMEND-P2-H: FULL_DATABASE_SCRIPT consolidated output section added (Section 7.1)*
FINDING-008: Duplicate Manifest table removed from Section 10*
FINDING-010: Cross-reference fixed (Section 2.1 → CONTRACT-6)*
Load order: shared-governance-core.md → shared-governance-rules.md →

       shared-artifact-contracts.md → MASTER-REGISTRY-SCHEMA.md → THIS FILE*


---

# COMPLETION PROTOCOL — P2 Database (AMEND-PIPELINE-V5 · GOVERNANCE-CONFIG §1D.4)

This section is MANDATORY at the end of every run of this engine. It is the
inline replacement for P-REG (retired) and P-ROUTER (demoted). Nothing here is
hardcoded: names come from §1D.2 / the tools' config.ARTIFACT_FILES.

```
STAGE KEY   : P2

1. ARTIFACT — emit, with the §1D.2 module-qualified names, then upload via the
   connector and capture {drive_file_id, drive_url} for each:
    db-script-{mod}.md

2. REGISTRY (inline — the former P-REG step, same session):
    registry-db-{mod}.md + project-registry update (DBS/XM index, table registry)
   Upload it too. Never create a separate registry session.

3. LEDGER — record the links using the LEDGER-WRITE PROCEDURE (§1D.8:
   upload → capture id/webViewLink → fetch journey json → append/START/END
   in memory → re-create the file → trash the old copy). Append one row per
   uploaded file to [LEDGER] =
   [CTX]/[Module]/journey-{mod}.json (schema §1D.3):
    { engine: "P2", stage, filename, artifact, drive_file_id,
       drive_url, recorded_at, status: "UPLOADED" }
   If this is the FIRST engine of this version → also write START (open the
   version section; IFA versions carry change_set = CS-ID).
   If this is the LAST engine run for this version → write END (close it).

4. HANDOFF — print the NEXT-ENGINE INPUT block (§1D.5), filled in:
    NEXT ENGINE : P2.5 UI/UX Design
    Read        : srs-{mod}.md · db-script-{mod}.md · registry-db-{mod}.md
    Do          : flow-diagram-{mod}.md + ui-ux-spec-{mod}.md (+ Shell Delta in IFA)
    Gate        : CONTRACT-11 inputs; Reconciliation Gate
   The user pastes that block as the first message of the next project.
```


PATHS (rendered from config.DRIVE_LAYOUT — GOVERNANCE-CONFIG §1E; never edit by hand)
  [MROOT] = [CTX]/[Module]/          (v1)   or   [CTX]/[Module]/v[N]/   (IFA, N ≥ 2)
  WRITES TO (this engine is the ONLY writer of these folders):
    [MROOT]/P2-DB/   → db-script-[mod].md, registry-db-[mod].md
  READS FROM:
    [MROOT]/P0-Platform/   ← module-registry-[mod].md, business-policies-[mod].md
    [MROOT]/P1-SRS/   ← srs-[mod].md, registry-srs-[mod].md
    [CTX]/_platform/                        ← platform-summary.md
  LEDGER: [CTX]/[Module]/_journey/journey-[mod].json   (cross-version; §1D.8)
  LAW (§1E.1): never write a file at [CTX] root or [MROOT] root — folders only.
  SELF-HEAL (§1E.5, AUTOMATIC at Pre-Flight): an input not at its governed path
  is searched in the module subtree (V5 or legacy name), renamed + moved there
  via the connector, and reported under HEALED: in the handoff — no human step.
  A missing ledger is created (START v1) on first contact.
  The connector upload in step 1 targets the WRITES-TO folder above, nothing else.

MUST NOT: emit a retired un-qualified filename (srs.md, db-script.md,
backend-execution-plan.md, frontend-execution-plan.md …); skip the registry step; write to
[STATE]/_router; rely on P-ROUTER for the next hop.
