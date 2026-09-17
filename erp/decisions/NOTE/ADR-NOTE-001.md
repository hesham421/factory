# ADR-NOTE-001 — حقول الكيان `master` مُضيَّقة لمحتوى يكتبه المستخدم / Narrowed `master` defaults for user-written content

| Item | Value |
|---|---|
| Module | NOTE | 
| Stage | P1 (SRS) |
| Status | ACCEPTED — non-breaking; the pass continued |
| Date | 2026-09-17 |

## Context
الملف الشخصي يُلزم كل كيان من نوع `master` بحقول `nameAr, nameEn, code, isActiveFl` وحقول
التدقيق الأربعة، ويفحص ذلك `ERP-1` (MAJOR). لكن POL-NOTE-005 المُقرّة تنصّ على أن عنوان
الملاحظة ونصّها حقلان حرّان بلغة كاتبهما، وSCOPE EXCEPTIONS تستبعد ثنائية اللغة لمحتوى
المستخدم صراحةً؛ واسم الملاحظة المعروض هو عنوانها — أي محتوى مستخدم لا تسمية نظام. كذلك
`code` كود عملٍ لا تستوفي الملاحظة أيًّا من شروطه الثلاثة (§3.3 NUMBERING).
The profile's `master` defaults assume reference data with a bilingual display name and a
business code; a personal note is neither.

## Decision
يبقى ENT-NOTE-001 مصنَّفًا `master` (اختيار محسوم في P0: التعطيل الناعم اصطلاح `master`،
ولا فترة ولا حالة من lookup تجعله `transactional`)، ويحمل من حقول النوع القياسية
`isActiveFl` وحقول التدقيق الأربعة كاملةً، ولا يحمل `nameAr`/`nameEn`/`code`؛ يقوم مقام
التسمية حقلٌ واحد `noteTitle` أحادي اللغة. تبقى ثنائية اللغة (domain-profile G11) سارية
كاملةً على اسم الوحدة والكيان والحقول والشاشة والرسائل — وهي محمولة في تسميات A3 وB.

## Consequences
- انحراف مُعلَن يظهر أمام فحص `ERP-1`؛ مصدره سياسة مُقرّة لا اجتهاد مرحلة، وهذا السجل هو مستنده.
- P2 لا يُنشئ أعمدة `name_ar`/`name_en`/`code` لجدول الملاحظة ولا فهرس تفرّد عليها.
- لو طُلب لاحقًا محتوى ثنائي اللغة، فهو تغيير نطاق يبدأ من P0 بقصة جديدة، لا تعديل في مكانه.

## Traces
ENT-NOTE-001 · REQ-NOTE-001 · REQ-NOTE-005 · RULE-NOTE-001 · RULE-NOTE-002 · US-NOTE-001 · POL-NOTE-005
