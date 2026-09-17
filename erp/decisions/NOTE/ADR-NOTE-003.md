# ADR-NOTE-003 — ردّ «غير موجودة» لطلب غير المالك / A non-owner's request is answered "not found"

| Item | Value |
|---|---|
| Module | NOTE |
| Stage | P1 (SRS) |
| Status | ACCEPTED — non-breaking; the pass continued |
| Date | 2026-09-17 |

## Context
POL-NOTE-001 تحصر القراءة بالمالك وPOL-NOTE-002 تحصر التعديل والتعطيل به، لكن أيًّا منهما
لا يقول بماذا يُردّ على غير المالك. الردّ بـ«ممنوع» يُقرّ ضمنًا بوجود ملاحظة بذلك المعرّف
ويكشف عددها وتسلسلها لمن يجرّب المعرّفات، وهو تسريبٌ للحدّ الذي تقوم عليه الوحدة كلها.
Neither policy states which answer a non-owner receives; "forbidden" confirms the note exists.

## Decision
كل طلب على ملاحظة لا يملكها الطالب — قراءةً أو تعديلًا أو تعطيلًا — يُردّ بالرسالة نفسها
التي يُردّ بها معرّفٌ غير موجود: ar «الملاحظة غير موجودة.» · en "The note was not found."
لا يُميَّز بين الحالتين في الرسالة ولا في رمز الخطأ (RULE-NOTE-005).

## Consequences
- P3.1 يُسجّل رمز خطأ واحدًا لكلتا الحالتين، ولا يُنشئ رمزًا ثانيًا لـ"ممنوع" على مستوى الصفّ.
- التفويض على مستوى الشاشة والإجراء يبقى على حاله (REQ-NOTE-018): «ممنوع» تخصّ الإجراء لا الصفّ.
- لو طلب العميل تمييز الحالتين لاحقًا، فتغيير الرسالة وحده يكفي ولا يمسّ أي متطلَّب.

## Traces
RULE-NOTE-005 · REQ-NOTE-006 · AC-NOTE-009 · AC-NOTE-010 · POL-NOTE-001 · POL-NOTE-002
