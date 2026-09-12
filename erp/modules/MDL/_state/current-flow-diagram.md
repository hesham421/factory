# FLOW DIAGRAM — البيانات المرجعية / Master Data Lookup (MDL)
══════════════════════════════════════════════════════════════════
Module : MDL   Version : v1   Profile : erp   Stage : P3.2 (Part A — UX design)
Inputs : srs (v1), prd (v1, APPROVED), api-docs (v1), registry-srs (v1), registry-exec-be (v1)
Screens: 2 — SCR-MDL-001..002 (one per SRS Part B screen requirement)
Flows  : 5 · ADRs raised : 7 — ADR-MDL-001..007 (all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

يصف هذا المستند مسارات التنقّل فقط: كل مسار يبدأ من شاشة معرّفة في متطلبات الشاشات
(SRS Part B) وينتهي عند مخرج واضح. لا يُنشئ هذا المستند شاشة ولا قاعدة عمل ولا صلاحية؛
كل شاشة هنا لها كتلة واحدة مقابلة في `ui-ux-spec-mdl.md`.

This document describes navigation paths only. Every flow starts at a screen the SRS declares,
cites the `US-*` that asks for it, and ends at a stated exit. No flow invents a screen, a rule
or a permission.

## SCREEN INDEX — SRS screen requirement → SCR

| SCR | Name (ar / en) | SRS screen req | Page code |
|---|---|---|---|
| SCR-MDL-001 | اللوكبات العامة / Generic Lookups | SCR-REQ-MDL-001 | MDL_LOOKUPS |
| SCR-MDL-002 | سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner | SCR-REQ-MDL-002 | MDL_TYPE_REGISTRY |

Two SRS screen requirements, two `SCR-*` — B4 of the reconciliation holds by construction.
MDL is a small module with one working screen and one browse screen: the whole platform's
coded value lists are managed through `SCR-MDL-001`, which is the point of the module
(POL-MDL-004 — one generic screen, not one screen per list).

## FLOWS

```
FLOW — Lookup type registration                 traces=US-MDL-001,US-MDL-004,REQ-MDL-001,REQ-MDL-002,REQ-MDL-003,REQ-MDL-004,SCR-MDL-001
Screens   : SCR-MDL-001
Sequence  : (menu) → SCR-MDL-001 type list → [New] → the type form beside the list
            → pick the owner module from the registered modules, set the key and both names
            → save → the type appears in the list and its (empty) value pane opens
            → [type selected → Edit] → both names are editable, the key is not
            → [Deactivate] → confirmation naming that consumer reads will stop returning its
              values → the row's state changes and the row stays in the list
            → [an owner module that is not registered] → nothing is saved, the message is shown
              on the owner field
Trigger   : وحدة مستهلكة تحتاج قائمة قيم جديدة / a consuming module needing a new value list
Priority  : HIGH (PRD US-MDL-001, US-MDL-004)
```
المفتاح يُكتب مرة واحدة عند الإنشاء ولا يُعدَّل بعدها (RULE-MDL-003)، لأنه ما تستشهد به كل
وحدة مستهلكة بالفعل. الوحدة المالكة تُختار من قائمة الوحدات المسجّلة لا تُكتب يدويًا
(ADR-MDL-004)، فالمسار المرفوض يبقى استثناءً لا القاعدة.
Deactivating a type is one-way from this screen: no activate endpoint is published
(ADR-MDL-005), and the confirmation says so rather than offering a toggle whose second half
would fail.

```
FLOW — Value management                         traces=US-MDL-002,REQ-MDL-005,REQ-MDL-006,REQ-MDL-007,REQ-MDL-008,REQ-MDL-009,SCR-MDL-001
Screens   : SCR-MDL-001
Sequence  : SCR-MDL-001 → [type selected] → its values in the detail pane, ordered by sort order
            → [New value] → code, both names, sort order → save → the value list refreshes
            → [value → Edit] → both names and the sort order are editable, the code is not
            → [value → Deactivate] → confirmation → the row's state changes and consumer reads
              stop returning it
            → [a code already used under this type] → nothing is saved, the message is shown
              on the code field
Trigger   : إضافة أو تصحيح قيمة ضمن قائمة قائمة / adding or correcting a value in an existing list
Priority  : HIGH (PRD US-MDL-002)
```
نطاق تفرّد الرمز هو النوع الأب لا النظام كله (RULE-MDL-002): الرمز نفسه مشروع تحت نوع آخر،
والفحص الاستباقي يعمل ضمن النوع المحدَّد وحده.
The detail pane shows inactive values as well as active ones — a manager needs to see what a
consumer no longer receives, which is exactly what the consumer read hides.

```
FLOW — Value reordering                         traces=US-MDL-002,REQ-MDL-010,SCR-MDL-001
Screens   : SCR-MDL-001
Sequence  : SCR-MDL-001 → [type selected] → the value list
            → [drag a row to a new position] → the new order is submitted as the whole ordered
              list of value ids → the list re-renders in the persisted order
            → [the submitted set does not match the type's values] → the order is unchanged and
              the message is shown
Trigger   : ترتيب العرض الذي يراه المستهلك / the display order every consumer will receive
Priority  : LOW (PRD US-MDL-002 — REQ-MDL-010 is the module's only LOW-priority requirement)
```
الترتيب ليس تفضيلًا محليًا: `sortOrder` حقل مخزَّن يعيده نداء المستهلك، فإعادة الترتيب كتابة
حقيقية لا حالة واجهة. The same field is editable on the value form, so the two paths write one
field and the form shows whatever the last drag produced.

```
FLOW — Registry browse by owner                 traces=US-MDL-005,REQ-MDL-013,SCR-MDL-002
Screens   : SCR-MDL-002, SCR-MDL-001
Sequence  : (menu) → SCR-MDL-002 → the active types grouped under their owner module
            → [filter by owner module or by key] → the groups narrow
            → [a type] → SCR-MDL-001 with that type selected, where it can be managed
Trigger   : مراجعة ما سجّلته الوحدات من أنواع / reviewing what the modules have registered
Priority  : MEDIUM (PRD US-MDL-005)
```
الشاشة للقراءة فقط: لا إنشاء ولا تعديل هنا، والإدارة كلها على `SCR-MDL-001` (SRS §B3).
التجميع يأتي من الخادم كما هو ولا يُعاد تركيبه في الواجهة.
The link into SCR-MDL-001 is the one navigation this screen offers, and the target route
carries its own guard.

```
FLOW — Consumer read by key (no screen)         traces=US-MDL-003,REQ-MDL-011,REQ-MDL-012,SCR-MDL-002
Screens   : — (none; SCR-MDL-002 is where the SRS records the contract)
Sequence  : (a consuming module's backend asks for a type's values by key — no screen)
            → the active values are returned in sort order
            → [the type is inactive] → its values are excluded
            → [the key was never registered] → a not-found answer, never an empty success
Trigger   : أي وحدة مستهلكة تحتاج قيم قائمة وقت التشغيل / any consuming module at runtime
Priority  : HIGH — PRD US-MDL-003; POL-MDL-001 calls this the module's entire reason to exist
```
هذا المسار لا يبدأ بفعل مستخدم ولا ينتهي بشاشة: المستدعي وحدة أخرى عبر واجهة الوحدات داخل
العملية، والشاشة الوحيدة التي تؤثر فيه هي `SCR-MDL-001` — حيث تُنشأ القيم وتُعطَّل وحيث
يُعطَّل النوع كله. It is recorded here so the module's five stories all have a stated path;
no MDL screen calls it (ADR-MDL-007). What a user *can* observe of it is the consequence:
deactivating a value or its type on SCR-MDL-001 is what makes it stop being returned.

## RECONCILIATION — MDL v1

```
RECONCILIATION — MDL v1
B1 every US-* used in a flow has an SRS counterpart (REQ/AC/screen)
   → US-MDL-001..005 are each cited by at least one flow and each resolves to ≥1 REQ and ≥1
     SCR-REQ (SRS traceability matrix). No flow was excluded and no screen was invented. The
     consumer-read flow carries no screen of its own and says so, rather than inventing one
     for a server-to-server call.
B2 no RULE-* contradicts a flow/spec outcome
   → RULE-MDL-001 is the rejected branch of "Lookup type registration"; RULE-MDL-002 of
     "Value management"; RULE-MDL-003 is why the key is read-only on edit in the first flow;
     RULE-MDL-004 is the consequence the deactivate confirmation names and the behaviour the
     fifth flow describes. No contradiction found.
B3 every field/permission on a screen exists in the SRS
   → fields copied from SRS A3 per owning ENT and reconciled against the api-docs DTOs in
     ui-ux-spec-mdl.md; permission names taken from the SRS Access summary and the backend
     plan, never minted here. Extra removed: none. Missing added: none. One divergence, on
     SCR-MDL-001 and resolved against SRS A3 in ADR-MDL-006:
     SCR-MDL-001 · `isActiveFl` is read-only although B3 lists it among the detail input
       fields — no published write DTO accepts it, and it is changed by the deactivate
       endpoints alone.
     The other screen matches its B3 list exactly, which for a read-only browse is "no inputs".
B4 every screen entry of the SRS has exactly one SCR-* block
   → 2 SRS screen requirements ↔ SCR-MDL-001..002, 1:1 (SCREEN INDEX above).
RESULT  reconciled 2 · reworked 1 (SCR-MDL-001's isActiveFl, per B3 above) ·
        ADRs ADR-MDL-001, ADR-MDL-002, ADR-MDL-003, ADR-MDL-004, ADR-MDL-005, ADR-MDL-006,
        ADR-MDL-007 (all ACCEPTED, all non-breaking; raised in Part B's binding to the
        published api-docs and recorded here for completeness)
```
══════════════════════════════════════════════════════════════════
