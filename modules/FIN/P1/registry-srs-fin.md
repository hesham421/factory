<!-- P1 stage output — governed by factory.yaml stages[P1]; see shared/REGISTRY-SCHEMA.md -->
## REGISTRY — P1 — FIN v1

Entities      :
| ENT id | Name | Kind | PRIVATE / SHARED(owner) | Status |
|---|---|---|---|---|
| ENT-FIN-001 | شجرة الحسابات / Chart of Account | master | PRIVATE | REGISTERED |
| ENT-FIN-002 | بُعد الحساب / Account Dimension (definition + values) | config | PRIVATE | REGISTERED |
| ENT-FIN-003 | البيانات المرجعية المحاسبية / Accounting Reference List (lookup type + values) | lookup | PRIVATE | REGISTERED |
| ENT-FIN-004 | قاعدة نوع الحدث / Event-Type Rule | config | PRIVATE | REGISTERED |
| ENT-FIN-005 | سطر القاعدة / Rule Line | config | PRIVATE | REGISTERED |
| ENT-FIN-006 | القيد المحاسبي / Journal Entry | transactional | PRIVATE | REGISTERED |
| ENT-FIN-007 | سطر القيد / Journal Entry Line | transactional | PRIVATE | REGISTERED |
| ENT-FIN-008 | قالب القيد المتكرر / العكسي / Recurring-Reversing Entry Template | config | PRIVATE | REGISTERED |
| ENT-FIN-009 | قاعدة التوزيع / Allocation Rule | config | PRIVATE | REGISTERED |
| ENT-FIN-010 | السنة المالية / Fiscal Year | master | PRIVATE | REGISTERED |
| ENT-FIN-011 | الفترة المالية / Fiscal Period | master | PRIVATE | REGISTERED |
| ENT-FIN-012 | مستخدم المحاسبة / Accounting User | security | PRIVATE | REGISTERED |
| ENT-FIN-013 | الدور والصلاحية / Role & Permission | security | PRIVATE | REGISTERED |

Consumed      : none — FIN is fully isolated (`DEPENDENCIES: NONE`, `ROOT: YES`); no HARD-FK / SOFT-READ record added to the dependency index.

Lookups owned : payment-methods (0 values seeded) · accounting-event-types (0 values seeded) · account-types (5 values) · period-states (3 values) · journal-types (5 values)
Lookups consumed : none

Screens       :
| SCR-REQ id | Name | Page code |
|---|---|---|
| SCR-REQ-FIN-001 | Chart of Accounts | FIN_COA |
| SCR-REQ-FIN-002 | Dimensions | FIN_DIM |
| SCR-REQ-FIN-003 | Lookups | FIN_LKP |
| SCR-REQ-FIN-004 | Engine Rules | FIN_RULE |
| SCR-REQ-FIN-005 | Recurring Templates | FIN_TMPL |
| SCR-REQ-FIN-006 | Allocation Rules | FIN_ALLOC |
| SCR-REQ-FIN-007 | Journal Entries | FIN_JE |
| SCR-REQ-FIN-008 | Fiscal Periods & Years | FIN_PERIOD |
| SCR-REQ-FIN-009 | Account Ledger | FIN_LEDGER |
| SCR-REQ-FIN-010 | Trial Balance | FIN_TB |
| SCR-REQ-FIN-011 | Balance Sheet | FIN_BS |
| SCR-REQ-FIN-012 | Income Statement | FIN_IS |
| SCR-REQ-FIN-013 | Dimension Reports | FIN_DIMRPT |
| SCR-REQ-FIN-014 | Login | FIN_LOGIN |
| SCR-REQ-FIN-015 | Users | FIN_USER |
| SCR-REQ-FIN-016 | Roles & Permissions | FIN_ROLE |

Requirements  : REQ count: 34 · AC count: 41 · RULE count: 14 · SCR-REQ count: 16
                last sequence per atom (REQ: 34, AC: 37, ENT: 13, RULE: 14, SCR-REQ: 16)
                (AC ids are numbered independently of REQ ids in `srs-fin.md`; highest AC id emitted is AC-FIN-037.)

Decisions     : ADR-FIN-001, ADR-FIN-002, ADR-FIN-003 (all ACCEPTED — none BLOCKED)

Event         : "P1 completed: FIN v1 — 13 entities, 34 requirements, 41 acceptance criteria, 14 business rules, 16 screen requirements, 3 ADRs, 0 open questions"
