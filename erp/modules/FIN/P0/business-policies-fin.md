## BUSINESS POLICIES — الحسابات العامة / Finance (General Ledger) (FIN)
══════════════════════════════════════════════════════════════════
Module   : FIN     Source of truth : new project/general-accounting-system-plan-en.md
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)

The first 14 policies below transcribe, one-for-one, general-accounting-system-plan-en.md
§12 "Accounting details the analysis agent MUST honor" — every point is carried forward
as its own POL record, per GENERATION-INSTRUCTIONS.md §4.5 ("apply every one; do not
simplify any away"), so every later stage (PRD, SRS, rules, API) must trace back to it.

POL-FIN-001 — ثبات تساوي المدين والدائن / Debit=Credit is an absolute invariant
  Statement (ar) : يجب على النظام ألا يُرحِّل أي قيد ما لم يتساوَ إجمالي المدين مع إجمالي الدائن حتى أصغر وحدة عملة.
  Statement (en) : The system shall post no journal entry unless its total debits equal its total credits to the smallest currency unit.
  Pattern   : ubiquitous
  Trigger   : Post
  Rationale : عدم التوازن يعني خللاً في سلامة الترحيل، لا خطأ عرض
  Source    : general-accounting-system-plan-en.md §12.1
  Status    : CONFIRMED

POL-FIN-002 — إشارة الرصيد الطبيعي حسب نوع الحساب / Normal balance sign per account type
  Statement (ar) : يجب على النظام عرض إشارة رصيد كل حساب وفق طبيعته المدينة (أصول/مصروفات) أو الدائنة (خصوم/حقوق ملكية/إيرادات).
  Statement (en) : The system shall present each account's balance sign according to its account type's normal balance (debit-natured for assets/expenses, credit-natured for liabilities/equity/revenue).
  Pattern   : ubiquitous
  Trigger   : Any balance/report presentation
  Rationale : الإشارة تتبع طبيعة الحساب لا الحساب الحسابي الخام فقط
  Source    : general-accounting-system-plan-en.md §12.2
  Status    : CONFIRMED

POL-FIN-003 — الترحيل للأوراق النشطة القابلة للترحيل المباشر فقط / Posting only to leaf, active, direct-postable accounts
  Statement (ar) : إذا استهدف سطر قيد حسابًا ليس ورقة، أو غير نشط، أو لا يقبل ترحيلاً مباشرًا، فيجب على النظام رفض القيد.
  Statement (en) : If a journal line targets an account that is not a leaf, not active, or not direct-postable, then the system shall reject the entry.
  Pattern   : unwanted
  Trigger   : Build / post
  Rationale : الحسابات التجميعية للعرض فقط
  Source    : general-accounting-system-plan-en.md §12.3
  Status    : CONFIRMED

POL-FIN-004 — بوابة الفترة عند لحظة الترحيل / Period gate checked at post time
  Statement (ar) : عند ترحيل قيد اليومية، يجب على النظام التحقق من أن الفترة المستهدفة مفتوحة في تلك اللحظة، بصرف النظر عن حالتها وقت بناء القيد.
  Statement (en) : When a journal entry is posted, the system shall verify the target period is Open at that moment, independent of its state when the entry was built.
  Pattern   : event
  Trigger   : Post
  Rationale : الفترة قد تتغير حالتها بين البناء والترحيل
  Source    : general-accounting-system-plan-en.md §12.4
  Status    : CONFIRMED

POL-FIN-005 — المبالغ موجبة دائمًا والاتجاه يحمل الإشارة / Positive amounts; direction carries the sign
  Statement (ar) : يجب على النظام تخزين كل مبلغ سطر قيد موجبًا، مع حمل الاتجاه (مدين/دائن) كخاصية منفصلة.
  Statement (en) : The system shall store every journal line amount as positive, with the direction (debit/credit) carried as a separate attribute.
  Pattern   : ubiquitous
  Trigger   : Any journal line
  Rationale : التخفيض هو عكس الاتجاه، لا رقمًا سالبًا
  Source    : general-accounting-system-plan-en.md §12.5
  Status    : CONFIRMED

POL-FIN-006 — سطر الباقي ضامن التوازن / The remainder line is the balancing guarantor
  Statement (ar) : يجب على النظام تعيين سطر واحد بالضبط، في أي توزيع مركّب أو نسبي، سطرَ باقٍ يمتص فرق التقريب، ولا يُحسَب أبدًا كنسبة مئوية.
  Statement (en) : The system shall designate, in any compound or percentage distribution, exactly one line as the remainder line absorbing the rounding difference, never itself computed as a percentage.
  Pattern   : ubiquitous
  Trigger   : Distribution calculation (rule engine or allocation)
  Rationale : ضمان التوازن التام رغم التقريب
  Source    : general-accounting-system-plan-en.md §12.6
  Status    : CONFIRMED

POL-FIN-007 — العكس تام ومرتبط / Reversal is exact and linked
  Statement (ar) : يجب على النظام إنشاء قيد عكسي يطابق الأصل سطرًا بسطر بعكس الاتجاه وبنفس المبالغ، ومرتبط به ثنائي الاتجاه.
  Statement (en) : The system shall generate a reversing entry that mirrors its original line-for-line with opposite directions and equal amounts, linked bidirectionally to it.
  Pattern   : ubiquitous
  Trigger   : Reverse action
  Rationale : تصحيح دون فقدان الأثر التدقيقي
  Source    : general-accounting-system-plan-en.md §12.7
  Status    : CONFIRMED

POL-FIN-008 — ميزان المراجعة متوازن دائمًا / Trial balance always balances
  Statement (ar) : يجب على النظام ضمان تساوي إجمالي أرصدة المدين مع إجمالي أرصدة الدائن في ميزان المراجعة في أي لحظة.
  Statement (en) : The system shall ensure the trial balance's total debit balances equal its total credit balances at any point in time.
  Pattern   : ubiquitous
  Trigger   : Trial balance generation
  Rationale : عدم التوازن هنا عرَض لخلل ترحيلي، لا خطأ عرض
  Source    : general-accounting-system-plan-en.md §12.8
  Status    : CONFIRMED

POL-FIN-009 — الأرصدة تُشتق دائمًا، لا تُخزَّن / Balances are recomputed, never stored-and-trusted
  Statement (ar) : يجب على النظام حساب كل رصيد وتقرير من سطور القيود المُرحَّلة مباشرة، لا من عمود رصيد مُخزَّن.
  Statement (en) : The system shall compute every balance and report from POSTED journal lines directly, never from a stored balance column.
  Pattern   : ubiquitous
  Trigger   : Any balance/report query
  Rationale : تجنّب عطب الأنظمة القديمة القائم على أعمدة رصيد غير متزامنة
  Source    : general-accounting-system-plan-en.md §12.9
  Status    : CONFIRMED

POL-FIN-010 — استمرارية الأرصدة الافتتاحية / Opening balances continuity
  Statement (ar) : يجب على النظام ترحيل أرصدة إقفال السنة المالية كأرصدة افتتاحية للسنة التالية لحسابات الميزانية، وفتح حسابات النتيجة بصفر بعد إقفالها إلى الأرباح المحتجزة.
  Statement (en) : The system shall carry a fiscal year's closing balances forward as the next year's opening balances for balance-sheet accounts, and open result accounts at zero after closing to Retained Earnings.
  Pattern   : ubiquitous
  Trigger   : Year-end close
  Rationale : استمرارية مالية صحيحة عبر السنوات
  Source    : general-accounting-system-plan-en.md §12.10
  Status    : CONFIRMED

POL-FIN-011 — الأبعاد جزء من هوية الترحيل / Dimensions are part of the posting identity
  Statement (ar) : يجب على النظام معاملة تركيبة الحساب وأبعاده معًا كهوية الترحيل في كل رصيد وتقرير.
  Statement (en) : The system shall treat an account and its dimension combination together as the posting identity for every balance and report.
  Pattern   : ubiquitous
  Trigger   : Any balance/report aggregation
  Rationale : لا تجميع بالحساب الأساسي وحده عندما يكون هناك بُعد فاعل
  Source    : general-accounting-system-plan-en.md §12.11
  Status    : CONFIRMED

POL-FIN-012 — التزام الإدراج الفريد عند الحدود / Idempotency at the boundary is assumed, not re-implemented
  Statement (ar) : إذا كان مرجع حدث قياسي قد أنتج قيدًا مُرحَّلاً بالفعل، فيجب على النظام رفض إنشاء قيد ثانٍ لنفس المرجع.
  Statement (en) : If a canonical event's reference has already produced a posted entry, then the system shall reject a second entry for the same reference.
  Pattern   : unwanted
  Trigger   : Event-generated entry build
  Rationale : الحدث المكرر عيب يُرفض، لا يُرحَّل مرتين
  Source    : general-accounting-system-plan-en.md §12.12
  Status    : CONFIRMED

POL-FIN-013 — أثر تدقيقي غير قابل للتعديل وكامل / Immutable and complete audit trail
  Statement (ar) : يجب على النظام الاحتفاظ بسجل إنشاء كل قيد مُرحَّل دون حذف فعلي أبدًا، بحيث يبقى كل رقم مُقرَّر قابلاً للتتبع حتى قيده ومرجع حدثه المصدر.
  Statement (en) : The system shall retain every posted entry's creation record and never hard-delete it, keeping every reported figure traceable to its source entry and event reference.
  Pattern   : ubiquitous
  Trigger   : Any posted entry
  Rationale : الأثر التدقيقي متطلب لا رفاهية
  Source    : general-accounting-system-plan-en.md §12.13
  Status    : CONFIRMED

POL-FIN-014 — لا معنى تجاري داخل المحاسبة / No business meaning inside accounting
  Statement (ar) : يجب على النظام اشتقاق كل سلوك ترحيل من بيانات الحساب والبُعد والقاعدة والحدث فقط، لا من أي منطق عمل خاص بالمضيف.
  Statement (en) : The system shall derive all posting behavior only from account, dimension, rule and event data, never from host-specific business logic.
  Pattern   : ubiquitous
  Trigger   : Any rule evaluation
  Rationale : القابلية للتوصيل بأي نظام مضيف
  Source    : general-accounting-system-plan-en.md §12.14
  Status    : CONFIRMED

The remaining policies transcribe the plan's other platform-level constraints (security
consumption, lookup consumption, posting/approval model, pluggability boundary).

POL-FIN-015 — لا أمان خاص بـ FIN / No security of its own
  Statement (ar) : يجب على النظام ألا يملك أي مصادقة أو تفويض خاص به، معتمدًا كليًا على وحدة الأمان للهوية والصلاحيات.
  Statement (en) : The system shall own no authentication and no authorization of its own, relying entirely on the Security module for identity and permissions.
  Pattern   : ubiquitous
  Trigger   : Any request
  Rationale : المصدر الوحيد للحقيقة الأمنية
  Source    : general-accounting-system-plan-en.md §2.1
  Status    : CONFIRMED

POL-FIN-016 — فصل المهام: منشئ القيد ≠ معتمد الإغلاق / SoD: entry-creator ≠ period-close approver
  Statement (ar) : يجب على النظام اشتراط أن تُسنَد صلاحية إنشاء القيد وصلاحية اعتماد إغلاق الفترة لدورين أو مستخدمين متمايزين، منفَّذًا عبر وحدة الأمان المشتركة.
  Statement (en) : The system shall require the entry-creator permission and the period-close-approver permission be held by distinct roles or users, enforced through the shared Security module.
  Pattern   : ubiquitous
  Trigger   : Period close approval
  Rationale : نقطة التحكم البشري الوحيدة يجب ألا يتحكم بها طرف واحد
  Source    : general-accounting-system-plan-en.md §2.2, §8.2, §10.3
  Status    : CONFIRMED

POL-FIN-017 — لا جداول lookup خاصة بـ FIN / No lookup table of its own
  Statement (ar) : يجب على النظام ألا يملك أي جدول قيم مرجعية خاصًا به، مسجِّلاً وقارئًا كل قائمة قيم مُرمَّزة عبر وحدة البيانات المرجعية.
  Statement (en) : The system shall own no lookup table of its own, registering and reading every coded value list through the Lookup module.
  Pattern   : ubiquitous
  Trigger   : Any coded value need
  Rationale : مركزية القيم المرجعية
  Source    : general-accounting-system-plan-en.md §5.1
  Status    : CONFIRMED

POL-FIN-018 — ترحيل مباشر دون اعتماد لكل قيد / Direct posting, no per-entry approval
  Statement (ar) : يجب على النظام ترحيل كل قيد مباشرة بعد التحقق الآلي، دون أي خطوة اعتماد بشري على مستوى القيد الفردي.
  Statement (en) : The system shall post every entry directly after automatic validation, with no per-entry human approval step.
  Pattern   : ubiquitous
  Trigger   : Any entry build (any source)
  Rationale : السرعة التشغيلية مع نقل نقطة التحكم إلى إغلاق الفترة
  Source    : general-accounting-system-plan-en.md §8.1
  Status    : CONFIRMED

POL-FIN-019 — إغلاق الفترة هو بوابة الاعتماد الوحيدة / Period close is the sole approval gate
  Statement (ar) : يجب على النظام اشتراط الاعتماد البشري فقط عند إغلاق الفترة، لا على مستوى القيد الفردي أبدًا.
  Statement (en) : The system shall require human approval only at period close, never at the level of an individual entry.
  Pattern   : ubiquitous
  Trigger   : Period close
  Rationale : نقطة تحكم بشرية واحدة مقصودة
  Source    : general-accounting-system-plan-en.md §10.3
  Status    : CONFIRMED

POL-FIN-020 — لا قراءة أو كتابة لجداول المضيف / No read/write to any host system table
  Statement (ar) : يجب على النظام ألا يقرأ من أو يكتب إلى أي جدول لأي نظام أعمال مضيف، متفاعلاً معه فقط عبر الحدث المحاسبي القياسي.
  Statement (en) : The system shall read from and write to no table of any host business system, interacting with it only through the canonical accounting event.
  Pattern   : ubiquitous
  Trigger   : Any integration point
  Rationale : القابلية للتوصيل والفصل التام
  Source    : general-accounting-system-plan-en.md §3, §15
  Status    : CONFIRMED

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
See module-registry-fin.md → LOOKUPS OWNED for the full 13-key list and every named
initial value; not repeated here to avoid duplication.

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| Multi-currency | Not built this version | explicit future request | general-accounting-system-plan-en.md §15 |
| Multi-ledger / multi-entity, intercompany entries | Not built this version | explicit future request | general-accounting-system-plan-en.md §15 |
| Statistical accounts | Not built this version | explicit future request | general-accounting-system-plan-en.md §15 |
| Multi-pattern fiscal calendar | Not built this version | explicit future request | general-accounting-system-plan-en.md §15 |
| Attachments on journal entries | Not built this version | explicit future request | general-accounting-system-plan-en.md §15 |
| Account numbers in event payloads | Never — a permanent boundary rule, not a deferred feature | never | general-accounting-system-plan-en.md §15 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
None — no open question was raised for FIN; the plan is fully prescriptive for this
stage's scope.
══════════════════════════════════════════════════════════════════
