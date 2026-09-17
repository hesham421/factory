# ADR-NOTE-004 — استراتيجية فهرسة مُرشِّح البحث النصي / Index strategy for the text filter

| Item | Value |
|---|---|
| Module | NOTE |
| Stage | P2 (Database) |
| Status | ACCEPTED — non-breaking; the pass continued |
| Date | 2026-09-17 |

## Context
يوجب المحرك (§4.3) فهرسًا على كل عمود يُستعمل في مُرشِّحات البحث والقوائم (PART B §B2).
مُرشِّح النص في B2 يقع على `noteTitle` و`noteBody` بدلالة "يحتوي" (REQ-NOTE-011)، وفهرس
B-tree لا يخدم نمط `%text%` إطلاقًا: يبقى المُخطِّط على مسح كامل ويُكلّف الفهرس كتابةً بلا
قراءة. والبديل — فهرس GIN بامتداد `pg_trgm` — يفرض امتدادًا على قاعدة البيانات لا يذكره
أي مُدخل، ولا يُسمّي أي متطلَّب حجمًا ولا زمن استجابة.
The SRS settles neither an index type nor a volume; a btree on a substring filter is
dead weight, and a trigram index would impose an extension no input requires.

## Decision
لا فهرس على `note_title` ولا على `note_body` في النسخة 1. مُرشِّح النص يُخدَم بمسح ضمن
نطاق المالك وحده، وهو نطاق مضمون الضيق: البحث محصور بملاحظات الطالب دائمًا (REQ-NOTE-009)
ومُقسَّم على الخادم بحجم صفحة 20 و200 حدًّا أقصى (REQ-NOTE-012). الفهرس المركَّب
`IDX_NOTE_NOTE_OWN_ACT (owner_user_ref, is_active_fl)` هو الذي يحصر هذا النطاق، ويغطي
بسابقته عمود المالك وحده. الترتيب الافتراضي بالأحدث يخدمه `IDX_NOTE_NOTE_OWN_UPD`.

## Consequences
- عمودا العنوان والنص بلا فهرس — انحراف مُعلَن عن حرفية §4.3، مُبرَّر بأن الفهرس المطلوب
  لا يخدم نمط المُرشِّح.
- إن ظهر لاحقًا متطلَّب أداء أو حجم، يُضاف فهرس `GIN` بـ `pg_trgm` في نسخة دلتا: إضافة
  فهرس لا تمسّ أي عمود ولا أي متطلَّب، فالقرار غير كاسر.
- P3.1 يبني استعلام البحث على المالك أولاً ثم الحالة ثم النص.

## Traces
REQ-NOTE-009 · REQ-NOTE-010 · REQ-NOTE-011 · REQ-NOTE-012 · SCR-REQ-NOTE-001 §B2 ·
DBF-NOTE-002 · DBF-NOTE-003 · DBF-NOTE-004 · DBF-NOTE-005
