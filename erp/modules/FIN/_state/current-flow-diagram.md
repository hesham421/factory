# FLOW DIAGRAM — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module : FIN   Version : v1   Profile : erp   Stage : P3.2 (Part A — UX design)
Inputs : srs (v1), prd (v1, APPROVED), api-docs (v1), registry-srs (v1), registry-exec-be (v1)
Screens: 12 — SCR-FIN-001..012 (one per SRS Part B screen requirement)
Flows  : 13 · ADRs raised : 7 — ADR-FIN-002..008 (all ACCEPTED, all non-breaking)
══════════════════════════════════════════════════════════════════

يصف هذا المستند مسارات التنقّل فقط: كل مسار يبدأ من شاشة معرّفة في متطلبات الشاشات
(SRS Part B) وينتهي عند مخرج واضح. لا يُنشئ هذا المستند شاشة ولا قاعدة عمل ولا صلاحية؛
كل شاشة هنا لها كتلة واحدة مقابلة في `ui-ux-spec-fin.md`.

This document describes navigation paths only. Every flow starts at a screen the SRS
declares, cites the `US-*` that asks for it, and ends at a stated exit. No flow invents a
screen, a rule or a permission.

## SCREEN INDEX — SRS screen requirement → SCR

| SCR | Name (ar / en) | SRS screen req | Page code |
|---|---|---|---|
| SCR-FIN-001 | شجرة الحسابات / Chart of accounts | SCR-REQ-FIN-001 | FIN_ACCOUNTS |
| SCR-FIN-002 | تعريف الأبعاد وقيمها / Dimension definition & values | SCR-REQ-FIN-002 | FIN_DIMENSIONS |
| SCR-FIN-003 | قواعد المحرك / Engine rules | SCR-REQ-FIN-003 | FIN_RULES |
| SCR-FIN-004 | قوالب متكررة/عكسية / Recurring / reversing templates | SCR-REQ-FIN-004 | FIN_RECURRING_TEMPLATES |
| SCR-FIN-005 | قواعد التوزيع / Allocation rules | SCR-REQ-FIN-005 | FIN_ALLOCATION_RULES |
| SCR-FIN-006 | قيود اليومية / Journal entries | SCR-REQ-FIN-006 | FIN_JOURNAL_ENTRIES |
| SCR-FIN-007 | الفترات والسنوات المالية / Fiscal periods & years | SCR-REQ-FIN-007 | FIN_PERIODS |
| SCR-FIN-008 | دفتر الحساب / Account ledger | SCR-REQ-FIN-008 | FIN_ACCOUNT_LEDGER |
| SCR-FIN-009 | ميزان المراجعة / Trial balance | SCR-REQ-FIN-009 | FIN_TRIAL_BALANCE |
| SCR-FIN-010 | الميزانية العمومية / Balance sheet | SCR-REQ-FIN-010 | FIN_BALANCE_SHEET |
| SCR-FIN-011 | قائمة الدخل / Income statement | SCR-REQ-FIN-011 | FIN_INCOME_STATEMENT |
| SCR-FIN-012 | تقارير الأبعاد / Dimension reports | SCR-REQ-FIN-012 | FIN_DIMENSION_REPORTS |

Twelve SRS screen requirements, twelve `SCR-*` — B4 of the reconciliation holds by
construction. The two onboarding stories (US-FIN-017 SEC registration, US-FIN-018 MDL lookup
registration) carry no screen in the SRS traceability matrix and therefore no flow: they are
deployment acts, not navigation.

## FLOWS

```
FLOW — Chart of accounts maintenance          traces=US-FIN-001,REQ-FIN-001,REQ-FIN-002,REQ-FIN-003,SCR-FIN-001
Screens   : SCR-FIN-001
Sequence  : (menu) → SCR-FIN-001 tree + search → [node selected] → the account's form beside
            the tree → save → the tree refreshes at that node
            → [New] → an empty form with the selected node pre-filled as the parent
            → [Deactivate] → confirmation → the node's status changes, the row stays in the tree
            → [isLeafFl set true on a node that has children] → the form stays open with the
              rule message, nothing saved
Trigger   : مسؤول مالي يبني أو يعدّل بنية الحسابات / an administrator shaping the account structure
Priority  : HIGH (PRD US-FIN-001)
```
الشاشة مركّبة (بحث + إدخال) بمعرّف `SCR-FIN-001` واحد، والنموذج يُملأ من صف نتيجة البحث
نفسه — لا يوجد نداء قراءة بالمعرّف وهذا استبعاد مقصود في v1 (SRS §B5، ADR-FIN-006).
RULE-FIN-001 is the rejected branch of this same flow, not a flow of its own: the form stays
open, the account is unchanged, and the message is the server's.

```
FLOW — Dimension definition                   traces=US-FIN-002,REQ-FIN-004,REQ-FIN-005,REQ-FIN-006,SCR-FIN-002
Screens   : SCR-FIN-002
Sequence  : (menu) → SCR-FIN-002 dimension list → [dimension selected] → its values beside it
            → [New value] → the value form → save → the value list refreshes
            → [value → Deactivate] → confirmation → the value is retired and is refused on any
              later journal line (REQ-FIN-021)
            → [duplicate code under the same dimension] → the form stays open with the rule message
Trigger   : مسؤول مالي يضيف بُعدًا أو قيمة بُعد / an administrator adding a dimension or a value
Priority  : HIGH (PRD US-FIN-002)
```
لا يوجد مسار تعطيل للبُعد الأب — لا REQ ولا AC ولا RULE يطلبه، والعَلَم لا يقود سلوكًا
(SRS §B4). التعطيل الوحيد هنا على مستوى القيمة، وهو ما يجعل RULE-FIN-009 قابلًا للبلوغ أصلًا.
The parent dimension has no deactivate path on purpose; only the value level does.

```
FLOW — Engine rule configuration              traces=US-FIN-003,REQ-FIN-007,REQ-FIN-008,REQ-FIN-009,SCR-FIN-003
Screens   : SCR-FIN-003
Sequence  : (menu) → SCR-FIN-003 rule search → [rule selected] → the rule header and its lines
            → [Add line] → a line row with its derivation, amount source, direction and
              distribution → save
            → [save with a percentage line and no remainder line] → the line set stays open
              with the rule message, nothing saved
            → [Deactivate rule] → confirmation → the rule is retired
Trigger   : مسؤول مالي يربط نوع حدث بسطور القيد / an administrator mapping an event type to entry lines
Priority  : HIGH — the PRD names the rules engine "the core" (§6.1)
```
تعطيل القاعدة لا يُحرِّر نوع الحدث لقاعدة بديلة — قيد مُعلَن في الخلفية (SRS §B4)، والشاشة
تذكره في تأكيد التعطيل بدل أن تعد بما لا يحدث. There is no rule update and no line delete:
neither is published (ADR-FIN-006), so neither is drawn.

```
FLOW — Recurring / reversing template lifecycle   traces=US-FIN-006,REQ-FIN-022,REQ-FIN-023,REQ-FIN-024,SCR-FIN-004
Screens   : SCR-FIN-004, SCR-FIN-006
Sequence  : (menu) → SCR-FIN-004 template search → [New] → header + its lines in ONE submission
            → save → the list refreshes
            → [row → Run] → confirmation → the posted entry is returned and the user is offered
              the entry on SCR-FIN-006
            → [row → Deactivate] → confirmation naming that the template will no longer run
            → [Run on a deactivated template] → refused with the message, nothing posted
Trigger   : محاسب يجهّز قيدًا متكررًا أو عكسيًا / an accountant preparing a recurring or reversing entry
Priority  : MEDIUM (PRD US-FIN-006)
```
القالب يُنشأ بسطوره في طلب واحد ولا يُعدَّل بعد ذلك — لا نداء تعديل منشور (ADR-FIN-006)،
فالتصحيح الوحيد المتاح هو التعطيل ثم إنشاء قالب جديد، والشاشة تقول ذلك صراحة.
The scheduled run (REQ-FIN-023) and the automatic next-period reversal (REQ-FIN-024) happen
server-side; this flow is the manual run of the same endpoint, and both land in the same list.

```
FLOW — Allocation rule lifecycle               traces=US-FIN-007,REQ-FIN-025,REQ-FIN-026,SCR-FIN-005
Screens   : SCR-FIN-005, SCR-FIN-006
Sequence  : (menu) → SCR-FIN-005 rule search → [New] → header + its targets in ONE submission
            → save → the list refreshes
            → [row → Run] → confirmation → the posted distribution entry is returned and the
              user is offered the entry on SCR-FIN-006
            → [row → Deactivate] → confirmation naming that the rule will no longer run
            → [percentage targets with no remainder target] → the target set stays open with
              the rule message, nothing saved
Trigger   : محاسب يوزّع رصيد حساب مصدر على أهدافه / an accountant distributing a source balance
Priority  : MEDIUM (PRD US-FIN-007)
```
سطر الباقي يُحسب كفرق لا كنسبة (RULE-FIN-010)، والمسار لا يعرض حسابًا مسبقًا للمبالغ: التوزيع
الفعلي يُحسب على الخادم عند التشغيل من رصيد الحساب المصدر لحظتئذٍ.
As with templates, there is no rule update (ADR-FIN-006).

```
FLOW — Manual journal entry                    traces=US-FIN-005,REQ-FIN-014,REQ-FIN-015,REQ-FIN-017,REQ-FIN-018,REQ-FIN-019,REQ-FIN-020,REQ-FIN-021,SCR-FIN-006
Screens   : SCR-FIN-006
Sequence  : (menu) → SCR-FIN-006 search → [New] → the entry page: header (date, year, period,
            descriptions) + repeating lines with live debit/credit totals
            → [Post] → [every check passes] → the entry is POSTED and opens read-only with its
              document number
            → [any check fails] → the page stays open with every failing check listed and
              nothing posted
Trigger   : محاسب يسجّل تسوية أو قيدًا بلا حدث مصدر / an accountant recording an adjustment
Priority  : HIGH (PRD US-FIN-005)
```
التوازن يُعرض حيًا أثناء الإدخال لكن الحكم خادمي: الزر لا يُعطَّل بناءً على حساب العميل،
لأن REQ-FIN-015 يطلب عرض كل الفحوص الفاشلة معًا بعد الإرسال لا منع الإرسال.
There is no DRAFT the user can return to: a build that fails validation is never stored
(SRS §A7), so this flow has no "saved draft" exit.

```
FLOW — Journal review and reversal             traces=US-FIN-008,US-FIN-009,REQ-FIN-016,REQ-FIN-027,REQ-FIN-028,REQ-FIN-029,REQ-FIN-030,SCR-FIN-006
Screens   : SCR-FIN-006
Sequence  : (menu) → SCR-FIN-006 search, filtered by document number, date range, period,
            status or journal type → [row] → the entry read-only with its lines and dimensions
            → [Reverse] → confirmation naming the period the reversal will land in
              → the new reversal entry opens, and both entries now link to each other
            → [Reverse on an entry already reversed] → refused with the message, nothing posted
Trigger   : مراجعة ما تم ترحيله، أو تصحيح خطأ / reviewing what posted, or correcting a mistake
Priority  : HIGH (PRD US-FIN-008, US-FIN-009)
```
لا يوجد مسار تعديل ولا حذف: القيد المُرحَّل مقفل (RULE-FIN-016) والتصحيح الوحيد هو العكس.
When the original's period is closed the reversal posts into the current open period
(RULE-FIN-012) — the confirmation names which period before the user commits, so the
consequence is visible rather than discovered afterwards.

```
FLOW — Event-sourced postings appear           traces=US-FIN-004,REQ-FIN-010,REQ-FIN-011,REQ-FIN-012,REQ-FIN-013,REQ-FIN-046,SCR-FIN-006
Screens   : SCR-FIN-006
Sequence  : (a host system posts an accounting event — no screen) → the entry exists
            → SCR-FIN-006 search filtered by journal type "event generated" → [row]
            → the entry read-only, its event reference shown as the source
Trigger   : وصول حدث محاسبي من نظام مضيف / an accounting event arriving from a host system
Priority  : HIGH (PRD US-FIN-004)
```
هذا المسار لا يبدأ بفعل مستخدم: المحرك يبني القيد من الحدث، والشاشة هي مكان رؤيته فقط.
لا تُدخل أي شاشة حدثًا يدويًا — ADR-FIN-007. The rejected branches (no active rule, duplicate
event reference) are server outcomes the host is answered with; no FIN screen shows a queue
of them, because the SRS declares no such entity.

```
FLOW — Fiscal calendar setup                   traces=US-FIN-010,REQ-FIN-031,REQ-FIN-032,REQ-FIN-033,SCR-FIN-007
Screens   : SCR-FIN-007
Sequence  : (menu) → SCR-FIN-007 period list (optionally narrowed to one year)
            → [New year] → code, start, end, period count → save → the year and its generated
              periods appear, each Open
            → [period row → Soft-close] → confirmation → the row becomes soft-closed
            → [soft-closed row → Open] → confirmation → the row is Open again
Trigger   : بداية سنة مالية، أو ضبط فترة / opening a fiscal year, or adjusting a period
Priority  : HIGH (PRD US-FIN-010)
```
لا يوجد بحث عن السنوات المالية — فجوة مُسجَّلة في SRS §B5 وفي ADR-FIN-006؛ معرّف السنة
يُكتشف من صفوف الفترات نفسها، وهو المسار الذي تصفه SRS. The year list on this screen is
therefore derived from the period rows, not fetched as a list of its own.

```
FLOW — Period close approval                   traces=US-FIN-011,REQ-FIN-034,REQ-FIN-035,REQ-FIN-037,REQ-FIN-038,SCR-FIN-007
Screens   : SCR-FIN-007
Sequence  : (menu) → SCR-FIN-007 → [soft-closed period → Hard-close] → confirmation stating
            that the close is permanent → the row becomes hard-closed and shows who closed it
            and when
            → [Hard-close attempted without the approval permission] → the server refuses and
              the message is shown; the row is unchanged
            → [Open attempted on a hard-closed period] → refused with the message
Trigger   : مراقب مالي يعتمد إغلاق فترة / a financial controller approving a period close
Priority  : HIGH (PRD US-FIN-011 — the single human control point)
```
الاعتماد فعل منفصل بصلاحية منفصلة (RULE-FIN-015)، والشاشة لا تُخفي الزر: الصلاحية غير قابلة
للقراءة من أي نداء منشور، فالخادم هو الحَكَم (ADR-FIN-005). `closedBy`/`closedAt` are shown on
the row afterwards, which is the visible half of REQ-FIN-037.

```
FLOW — Year-end close                          traces=US-FIN-010,REQ-FIN-036,REQ-FIN-041,REQ-FIN-042,SCR-FIN-007
Screens   : SCR-FIN-007, SCR-FIN-006
Sequence  : (menu) → SCR-FIN-007 → [year with every period hard-closed → Run year-end close]
            → confirmation → the closing entry and the next year's opening entry are returned
            → [either entry] → SCR-FIN-006 read-only
            → [any period not hard-closed] → refused with the message, nothing posted
Trigger   : انتهاء السنة المالية / the end of a fiscal year
Priority  : HIGH (PRD US-FIN-010)
```
الإجراء يُعرض دائمًا ويُمنع خادميًا عند عدم اكتمال الإغلاق؛ الشاشة تعرض عدد الفترات غير
المغلقة كسياق لا كبوابة. Its two entries are ordinary POSTED entries afterwards, and are what
REQ-FIN-041 and REQ-FIN-042 read as the next year's opening continuity.

```
FLOW — Financial reporting and drill-down      traces=US-FIN-012,US-FIN-013,US-FIN-014,US-FIN-015,US-FIN-019,REQ-FIN-039,REQ-FIN-040,REQ-FIN-041,REQ-FIN-042,REQ-FIN-046,SCR-FIN-008,SCR-FIN-009,SCR-FIN-010,SCR-FIN-011
Screens   : SCR-FIN-010, SCR-FIN-011, SCR-FIN-009, SCR-FIN-008, SCR-FIN-006
Sequence  : (menu) → SCR-FIN-010 balance sheet │ SCR-FIN-011 income statement
            → [a statement line] → SCR-FIN-009 trial balance narrowed to that account type
            → [a trial-balance row] → SCR-FIN-008 account ledger for that account and range
            → [a ledger row] → SCR-FIN-006 the originating entry, read-only
            → the entry's event reference (or its manual / recurring / allocation type) is the
              end of the chain
Trigger   : مراقب مالي يفسّر رقمًا في قائمة مالية / a controller explaining a figure
Priority  : HIGH for the statements (PRD US-FIN-012..015) · MEDIUM for the drill-down (US-FIN-019)
```
كل شاشة في السلسلة قابلة للعنونة: المرشّحات تُعكس في وسائط المسار، فالانتقال نازلًا يحافظ على
الحساب والنطاق الزمني ويمكن مشاركته كرابط. Every figure is computed live from posted lines at
request time — no screen caches a balance and no screen reads a stored balance column
[POL-FIN-009].

```
FLOW — Dimension analysis                      traces=US-FIN-016,REQ-FIN-043,SCR-FIN-012
Screens   : SCR-FIN-012, SCR-FIN-008
Sequence  : (menu) → SCR-FIN-012 → choose a dimension, optionally one of its values and a
            period → the account × dimension-value rows
            → [a row] → SCR-FIN-008 account ledger narrowed to that account and that dimension
              value
Trigger   : تحليل النتائج حسب مشروع أو قسم أو مستثمر / analysis per project, department or investor
Priority  : MEDIUM (PRD US-FIN-016)
```
الصفوف لا تُجمَع على الحساب وحده عندما يكون البُعد مطلوبًا — هذا هو جوهر REQ-FIN-043،
والانتقال إلى دفتر الحساب يحمل البُعد وقيمته معه حتى يبقى الرقم نفسه.

## RECONCILIATION — FIN v1

```
RECONCILIATION — FIN v1
B1 every US-* used in a flow has an SRS counterpart (REQ/AC/screen)
   → US-FIN-001..016 and US-FIN-019 are each cited by at least one flow and each resolves to
     ≥1 REQ and ≥1 SCR-REQ (SRS traceability matrix). US-FIN-017 and US-FIN-018 are cited by
     no flow: the matrix itself maps both to "— (onboarding, no screen)". No flow was
     excluded and no screen was invented.
B2 no RULE-* contradicts a flow/spec outcome
   → RULE-FIN-001 is the rejected branch of "Chart of accounts maintenance"; RULE-FIN-002 of
     "Dimension definition"; RULE-FIN-003 of the two rule-set flows; RULE-FIN-006..009 are
     the post-time checks "Manual journal entry" lists back to the user; RULE-FIN-010 is the
     remainder computation the allocation flow does not pre-compute; RULE-FIN-011..013 shape
     "Journal review and reversal"; RULE-FIN-014 and RULE-FIN-015 shape "Period close
     approval"; RULE-FIN-016 is why no edit or delete path exists on a posted entry;
     RULE-FIN-017 is why the entry header submits year, period and date together. No
     contradiction found.
B3 every field/permission on a screen exists in the SRS
   → fields copied from SRS A3 per owning ENT and reconciled against the api-docs DTOs in
     ui-ux-spec-fin.md; permission names taken from the SRS Access summary and the backend
     plan, never minted here. Extra removed: none. Missing added: two, both on SCR-FIN-006
     and both resolved against SRS A3 and RULE-FIN-017 in ADR-FIN-008:
     SCR-FIN-006 · `fiscalYearId` is an input although B3 lists only docDate and periodId —
       `JournalEntryCreateRequest` requires it and RULE-FIN-017 checks the three together;
     SCR-FIN-006 · `journalTypeCode` is in the form model although B3 marks it system-set —
       the request requires it; it is submitted as the fixed value `MANUAL`, read-only.
     Eleven of the twelve screens match their B3 list exactly.
B4 every screen entry of the SRS has exactly one SCR-* block
   → 12 SRS screen requirements ↔ SCR-FIN-001..012, 1:1 (SCREEN INDEX above).
RESULT  reconciled 12 · reworked 1 (SCR-FIN-006's header field list, per B3 above) ·
        ADRs ADR-FIN-002, ADR-FIN-003, ADR-FIN-004, ADR-FIN-005, ADR-FIN-006, ADR-FIN-007,
        ADR-FIN-008 (all ACCEPTED, all non-breaking; raised in Part B's binding to the
        published api-docs and recorded here for completeness)
```
══════════════════════════════════════════════════════════════════
