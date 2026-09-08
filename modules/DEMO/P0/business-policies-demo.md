## BUSINESS POLICIES — Daily Notes / Demo (DEMO)
══════════════════════════════════════════════════════════════════
Module   : DEMO     Source of truth : user vision text + dialogue resolutions
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)
لا توجد سياسات خاصة بالعميل — تُطبَّق قواعد النطاق القياسية. طلب المستخدم
("simple daily notes with just CRUD" / "ملاحظات يومية بسيطة بعمليات CRUD
فقط") لا يذكر أي قيد خاص يتجاوز عمليات الإنشاء/القراءة/التعديل/الحذف
القياسية؛ لذلك لا يُكتب أي سجل `POL` لهذه الوحدة.
None — standard domain rules apply; no `POL` record is created for this module.

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
لا توجد قيم مخصّصة — تُطبَّق القيم القياسية. / None — standard values apply.

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| المشاركة / دفاتر ملاحظات متعددة المستخدمين (Sharing / multi-user notebooks) | "just CRUD" — لا مشاركة ولا صلاحيات لكل ملاحظة ولا تعاون بين مستخدمين | طلب مستقبلي صريح بدعم ملاحظات متعددة المستخدمين | domain-profile §7.1 (مصطلح Daily Notes — "do not say" notebook system) |
| الموافقات / سير العمل على الملاحظات (Approval / workflow on notes) | لا تُطبَّق اتفاقيات سير عمل الموافقات في ERP على DEMO | لا شيء مخطَّط — DEMO أداة اختبار للخط الحوكمي وليست وحدة أعمال حقيقية | domain-profile §5 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Does "just CRUD" imply any client-specific business policy beyond standard create/read/update/delete? | No — treat "just CRUD" literally; write no POL record rather than inventing one. | Confirmed (no objection; matches the user's literal framing). | domain-profile §2, §3 |
══════════════════════════════════════════════════════════════════
