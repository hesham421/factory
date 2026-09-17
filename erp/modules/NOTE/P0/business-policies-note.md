## BUSINESS POLICIES — الملاحظات / Notes (NOTE)
══════════════════════════════════════════════════════════════════
Module   : NOTE     Source of truth : نص رؤية الوحدة + قرارات هذا الحوار / the module's vision text + this dialogue's resolutions
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)

POL-NOTE-001 — الملاحظة مرئية لمالكها فقط / A note is visible to its owner only
  Statement (ar) : يجب على النظام إتاحة قراءة الملاحظة لمستخدمها المالك دون سواه.
  Statement (en) : The system shall make a note readable only by the user who owns it.
  Pattern   : ubiquitous
  Trigger   : Search / Read
  Rationale : الرؤية تحصر القراءة في ملاحظات المستخدم نفسه — لا مشاركة ولا اطّلاع متبادل
  Source    : vision text — "A user writes a short note and reads their own notes back"; "search (own notes only)"
  Status    : CONFIRMED

POL-NOTE-002 — التعديل والتعطيل للمالك وحده / Owner-only update and deactivation
  Statement (ar) : إذا طلب مستخدم غير مالك الملاحظة تعديلها أو تعطيلها، فيجب على النظام رفض الطلب.
  Statement (en) : If a user who does not own a note requests its update or deactivation, then the system shall reject the request.
  Pattern   : unwanted
  Trigger   : Update / Deactivate
  Rationale : الملكية شرط كتابة كما هي شرط قراءة؛ بغير ذلك تُخترق حدود المالك من جهة الكتابة
  Source    : vision text — "four operations: create · update · deactivate · search (own notes only)"; resolved dialogue decision (module-registry-note.md #1 scope)
  Status    : CONFIRMED

POL-NOTE-003 — التقاعد بالتعطيل لا بالحذف / Retirement by deactivation, never by deletion
  Statement (ar) : يجب على النظام إخراج الملاحظة من الخدمة بالتعطيل وحده.
  Statement (en) : The system shall retire a note by deactivation alone.
  Pattern   : ubiquitous
  Trigger   : Deactivate
  Rationale : الحذف النهائي يُفقد أثر التدقيق؛ العملية الرابعة في الرؤية اسمها "تعطيل" لا "حذف"
  Source    : vision text — "four operations: … deactivate …"; [KB:erp-domain-standards §6 soft delete]
  Status    : CONFIRMED

POL-NOTE-004 — الملاحظة المعطَّلة خارج البحث الافتراضي / A deactivated note stays out of the default search
  Statement (ar) : أثناء كون الملاحظة معطَّلة، يجب على النظام استبعادها من البحث الافتراضي لمالكها.
  Statement (en) : While a note is deactivated, the system shall exclude it from its owner's default search.
  Pattern   : state
  Trigger   : Search
  Rationale : التعطيل يجب أن يُحدث أثرًا ملموسًا للمستخدم، وإلا صار علمًا بلا معنى
  Source    : vision text — "deactivate"; [KB:erp-domain-standards §6]
  Status    : CONFIRMED

POL-NOTE-005 — محتوى الملاحظة بلغة كاتبها / Note content is in its author's own language
  Statement (ar) : يجب على النظام حفظ عنوان الملاحظة ونصها كحقلين حرّين بلغة كاتبهما.
  Statement (en) : The system shall store a note's title and body as free-text fields in their author's own language.
  Pattern   : ubiquitous
  Trigger   : Create / Update
  Rationale : المحتوى الذي يكتبه المستخدم ليس بيانات مرجعية؛ فرض زوج ثنائي اللغة عليه يُلزم
              المستخدم بترجمة ملاحظته الشخصية. تبقى ثنائية اللغة سارية كاملةً على أسماء الوحدة
              والكيان والشاشة (domain-profile G11).
  Source    : resolved dialogue decision (platform-summary RESOLVED DECISIONS #5) — انحراف مُعلَن عن [KB:erp-domain-standards §2 rule 1]
  Status    : CONFIRMED

POL-NOTE-006 — مجموعة صلاحيات واحدة تحكم العمليات الأربع / One permission set governs all four operations
  Statement (ar) : يجب على النظام ضبط عمليات الملاحظة الأربع جميعها بمجموعة صلاحيات واحدة على شاشة الملاحظات الوحيدة.
  Statement (en) : The system shall govern all four note operations through a single permission set on the one Notes screen.
  Pattern   : ubiquitous
  Trigger   : Any authorization check
  Rationale : حجم الوحدة مقصود: شاشة واحدة، مجموعة صلاحيات واحدة — أي مجموعة ثانية تعني شاشة ثانية
  Source    : vision text — "one screen … one permission set on that screen"; [KB:erp-domain-standards §4]
  Status    : CONFIRMED

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
None — لا تملك الوحدة ولا تستهلك أي قائمة قيم مُرمَّزة / the module owns and consumes no coded value list.

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| مشاركة الملاحظة / note sharing | لا مسار لمشاركة ملاحظة مع مستخدم آخر ولا اطّلاع إداري شامل عليها في هذه النسخة / no sharing path and no administrative all-notes view in this version | طلب صريح من المستخدم لمشاركة أو لإشراف إداري | vision text — "reads their own notes back" |
| اعتماديات بيانات-مجال بين الوحدات / cross-module domain-data dependencies | لا صف XM ولا مفتاح أجنبي ولا قائمة قيم من MDL ولا كيان أجنبي / no XM row, no FK, no MDL lookup, no foreign entity. التسجيل الذاتي في سجلات SEC وبوابة الوحدة خارج هذا الاستثناء — invariant منصّي لا تملك أي وحدة الإعفاء منه (G2, G3) | قرار صريح لاحق يربط NOTE ببيانات وحدة أخرى | vision text — "zero cross-module dependencies"; domain-profile G2/G3; round-2 resolution #4 |
| توسيع النموذج / model growth | لا كيان ثانٍ ولا شاشة ثانية (وسوم، تصنيفات، مرفقات، تذكيرات) / no second entity or screen (tags, categories, attachments, reminders) | نسخة لاحقة تُعيد تحديد النطاق صراحة | vision text — "one entity … one screen" |
| ثنائية اللغة لمحتوى المستخدم / bilingual user content | العنوان والنص خارج اصطلاح nameAr/nameEn — انظر POL-NOTE-005 | طلب صريح بمحتوى ثنائي اللغة | [KB:erp-domain-standards §2 rule 1]; domain-profile G11 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | هل يرى مسؤول النظام كل الملاحظات؟ / Does an administrator see every note? | لا — لا استثناء لأي دور في هذه النسخة؛ الملكية هي الحدّ الوحيد (POL-NOTE-001) | موصى به — ينتظر تأكيد المستخدم | vision text — "own notes only"; [KB:erp-domain-standards §4] |
| 2 | ماذا يحدث للملاحظة المعطَّلة؟ / What becomes of a deactivated note? | تبقى محفوظة وتخرج من البحث الافتراضي لمالكها (POL-NOTE-003, POL-NOTE-004) | موصى به | [KB:erp-domain-standards §6] |
| 3 | هل يلزم أن يكون محتوى الملاحظة ثنائي اللغة؟ / Must note content be bilingual? | لا — حقل حر بلغة كاتبه (POL-NOTE-005)، مع بقاء ثنائية اللغة على الأسماء | موصى به | domain-profile G11; [KB:erp-domain-standards §2 rule 1] |
| 4 | هل تُسجَّل NOTE اعتمادية على SEC أو MDL؟ / Does NOTE record a SEC or MDL dependency? | **مُعدَّل في الجولة 2** — SEC: نعم، صف SOFT واحد (تسجيل ذاتي + بوابة الوحدة)، بلا صف XM وبلا مفتاح أجنبي؛ MDL: لا — لا قائمة قيم أصلًا | موصى به | project-registry SHARED ENTITY DECLARATIONS + DECISION INDEX #9; domain-profile §6, G2/G3; erp/modules/MDL/P0/module-registry-mdl.md |
══════════════════════════════════════════════════════════════════
