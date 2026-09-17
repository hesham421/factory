# ADR-NOTE-002 — حدّا طول العنوان والنص / Title and body length limits

| Item | Value |
|---|---|
| Module | NOTE |
| Stage | P1 (SRS) |
| Status | ACCEPTED — non-breaking; the pass continued |
| Date | 2026-09-17 |

## Context
US-NOTE-001 تصف "ملاحظة قصيرة"، ولا يُسمّي أي مدخل (رؤية، سياسة، سجل، قاعدة معرفة) رقمًا.
وترك الحقلين بلا حدّ يجعل القيد الوحيد قيدَ قاعدة بيانات، وخطأ قاعدة البيانات لا يصل
المستخدم أبدًا (engine §5) — فيصير للمستخدم رفضٌ بلا رسالة.
No input states a number, yet an unbounded free-text field leaves the only limit in the
database, where its failure has no business message.

## Decision
العنوان 200 حرفًا كحدًّا أقصى، والنص 4000 حرف، مُعلَنَين في RULE-NOTE-003 برسالة ثنائية اللغة.
الرقمان مقياسان لـ"ملاحظة قصيرة" تُقرأ في سطر واحد ونصّ يُقرأ في شاشة واحدة، لا أكثر.

## Consequences
- P2 يشتقّ الأنواع الفيزيائية من هذين الحدّين، وP3.1 يشتقّ منهما تحقّق المُدخلات.
- تغيير أيٍّ من الرقمين بطلب العميل لا يمسّ أي متطلَّب ولا أي معيار قبول عدا نصّ الرسالة.

## Traces
RULE-NOTE-003 · REQ-NOTE-004 · ENT-NOTE-001 · US-NOTE-001
