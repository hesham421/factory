## REGISTRY — P1 — NOTE v1
══════════════════════════════════════════════════════════════════
Module : NOTE (الملاحظات / Notes)   Version : v1   Profile : erp
Source : erp/modules/NOTE/P1/srs-note.md
══════════════════════════════════════════════════════════════════

### Entities
| ENT id | Name (ar / en) | Kind | PRIVATE / SHARED | Status |
|---|---|---|---|---|
| ENT-NOTE-001 | الملاحظة / Note | master | PRIVATE | REGISTERED |

### Consumed (shared entities of other modules)
| Owner ENT id | Owner module | HARD-FK / SOFT-READ | Consumes |
|---|---|---|---|
| ENT-SEC-001 | SEC | SOFT-READ (no FK) | الهوية كسلسلة أصل — `ownerUserRef` + حقول التدقيق / identity as a principal string |
| ENT-SEC-004 | SEC | SOFT-READ | تسجيل الوحدة / module registration row |
| ENT-SEC-005 | SEC | SOFT-READ | تسجيل الشاشة / screen registration row |
| ENT-SEC-006 | SEC | SOFT-READ | تسجيل الإجراءات الأربعة / the four action rows |
لا صف XM ولا مفتاح أجنبي — سابقة ADR-FIN-001 (project-registry DECISION INDEX #9).
No XM row and no foreign key; INT-C and INT-R stay empty but present in the execution plan.

### Lookups owned
| Key | ENT | Values count |
|---|---|---|
| — | — | 0 — لا قائمة قيم مُرمَّزة تملكها الوحدة / the module owns no coded value list |

### Lookups consumed
| Key | Owner |
|---|---|
| — | — | لا قيمة مُرمَّزة تُقرأ من MDL ولا من غيرها / none read from MDL or anywhere else |

### Screens
| SCR-REQ id | Name (ar / en) | Page code |
|---|---|---|
| SCR-REQ-NOTE-001 | شاشة الملاحظات / Notes | NOTE_NOTES |

### Requirements
| Atom | Count | Last sequence |
|---|---|---|
| REQ | 18 | REQ: 18 |
| AC | 24 | AC: 24 |
| ENT | 1 | ENT: 1 |
| RULE | 7 | RULE: 7 |
| SCR-REQ | 1 | SCR-REQ: 1 |

Requirements registered (REQ-NOTE-001 … REQ-NOTE-018):
REQ-NOTE-001, REQ-NOTE-002, REQ-NOTE-003, REQ-NOTE-004, REQ-NOTE-005, REQ-NOTE-006,
REQ-NOTE-007, REQ-NOTE-008, REQ-NOTE-009, REQ-NOTE-010, REQ-NOTE-011, REQ-NOTE-012,
REQ-NOTE-013, REQ-NOTE-014, REQ-NOTE-015, REQ-NOTE-016, REQ-NOTE-017, REQ-NOTE-018

Acceptance criteria registered (AC-NOTE-001 … AC-NOTE-024):
AC-NOTE-001, AC-NOTE-002, AC-NOTE-003, AC-NOTE-004, AC-NOTE-005, AC-NOTE-006,
AC-NOTE-007, AC-NOTE-008, AC-NOTE-009, AC-NOTE-010, AC-NOTE-011, AC-NOTE-012,
AC-NOTE-013, AC-NOTE-014, AC-NOTE-015, AC-NOTE-016, AC-NOTE-017, AC-NOTE-018,
AC-NOTE-019, AC-NOTE-020, AC-NOTE-021, AC-NOTE-022, AC-NOTE-023, AC-NOTE-024

Business rules registered (RULE-NOTE-001 … RULE-NOTE-007):
RULE-NOTE-001, RULE-NOTE-002, RULE-NOTE-003, RULE-NOTE-004, RULE-NOTE-005,
RULE-NOTE-006, RULE-NOTE-007

### Decisions
| ADR id | Subject | Status |
|---|---|---|
| ADR-NOTE-001 | حقول `master` القياسية مُضيَّقة: لا `nameAr`/`nameEn`/`code` | ACCEPTED (non-breaking) |
| ADR-NOTE-002 | حدّا الطول 200 / 4000 حرف | ACCEPTED (non-breaking) |
| ADR-NOTE-003 | ردّ «غير موجودة» لطلب غير المالك | ACCEPTED (non-breaking) |
لا قرار بحالة BLOCKED / no BLOCKED ADR — the pass completed.

### Event
"P1 completed: NOTE v1 — 1 entity, 18 requirements, 24 AC, 7 rules, 1 screen requirement, 3 ADR"
══════════════════════════════════════════════════════════════════
