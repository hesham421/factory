## REGISTRY — P1 — FIN v1
══════════════════════════════════════════════════════════════════

Entities
| ENT id | Name (ar/en) | Kind | PRIVATE/SHARED | Status |
|---|---|---|---|---|
| ENT-FIN-001 | الحساب / Account | master | PRIVATE | REGISTERED |
| ENT-FIN-002 | البُعد / Dimension | config | PRIVATE | REGISTERED |
| ENT-FIN-003 | قيمة البُعد / DimensionValue | lookup | PRIVATE | REGISTERED |
| ENT-FIN-004 | رأس قيد اليومية / JournalEntry | transactional | PRIVATE | REGISTERED |
| ENT-FIN-005 | سطر قيد اليومية / JournalLine | transactional | PRIVATE | REGISTERED |
| ENT-FIN-006 | بُعد سطر القيد / JournalLineDimension | transactional | PRIVATE | REGISTERED |
| ENT-FIN-007 | السنة المالية / FiscalYear | master | PRIVATE | REGISTERED |
| ENT-FIN-008 | الفترة المحاسبية / FiscalPeriod | master | PRIVATE | REGISTERED |
| ENT-FIN-009 | قاعدة نوع الحدث / EventTypeRule | config | PRIVATE | REGISTERED |
| ENT-FIN-010 | سطر القاعدة / RuleLine | config | PRIVATE | REGISTERED |
| ENT-FIN-011 | قالب متكرر/عكسي / RecurringTemplate | config | PRIVATE | REGISTERED |
| ENT-FIN-012 | سطر القالب المتكرر / RecurringTemplateLine | config | PRIVATE | REGISTERED |
| ENT-FIN-013 | قاعدة توزيع / AllocationRule | config | PRIVATE | REGISTERED |
| ENT-FIN-014 | هدف التوزيع / AllocationTarget | config | PRIVATE | REGISTERED |

Consumed
| Consumed entity | Owner ENT id | Owner module | HARD-FK / SOFT-READ |
|---|---|---|---|
| User | ENT-SEC-001 | SEC | HARD-FK (principal string) |
| ModuleRegistry | ENT-SEC-004 | SEC | HARD-FK |
| ScreenRegistry | ENT-SEC-005 | SEC | HARD-FK |
| ActionRegistry | ENT-SEC-006 | SEC | HARD-FK |
| LookupType | ENT-MDL-001 | MDL | HARD-FK |
| LookupValue | ENT-MDL-002 | MDL | HARD-FK |

Lookups owned
| Key | ENT | Values count |
|---|---|---|
| ACCOUNT_TYPE | ENT-FIN-001 | 5 |
| DEBIT_CREDIT | ENT-FIN-001, ENT-FIN-005, ENT-FIN-010, ENT-FIN-012 | 2 |
| PERIOD_STATE | ENT-FIN-008 | 4 |
| FISCAL_YEAR_STATUS | ENT-FIN-007 | 2 |
| JOURNAL_TYPE | ENT-FIN-004 | 5 |
| JOURNAL_STATUS | ENT-FIN-004 | 3 |
| ACCOUNTING_EVENT_TYPE | ENT-FIN-009 | 0 (host-defined) |
| PAYMENT_METHOD | (registered, no dedicated column this v1) | 0 (host-defined) |
| ACCOUNT_DERIVATION_TYPE | ENT-FIN-010 | 3 |
| AMOUNT_SOURCE_TYPE | ENT-FIN-010 | 3 |
| DISTRIBUTION_TYPE | ENT-FIN-010, ENT-FIN-014 | 3 |
| RECURRING_SCHEDULE_TYPE | ENT-FIN-011 | 2 |
| RECURRING_FREQUENCY | ENT-FIN-011 | 4 |

Lookups consumed
none.

Screens
| SCR-REQ id | Name (ar/en) | Page code |
|---|---|---|
| SCR-REQ-FIN-001 | شجرة الحسابات / Chart of accounts | FIN_ACCOUNTS |
| SCR-REQ-FIN-002 | تعريف الأبعاد وقيمها / Dimension definition & values | FIN_DIMENSIONS |
| SCR-REQ-FIN-003 | قواعد المحرك / Engine rules | FIN_RULES |
| SCR-REQ-FIN-004 | قوالب متكررة/عكسية / Recurring/reversing templates | FIN_RECURRING_TEMPLATES |
| SCR-REQ-FIN-005 | قواعد التوزيع / Allocation rules | FIN_ALLOCATION_RULES |
| SCR-REQ-FIN-006 | قيود اليومية / Journal entries | FIN_JOURNAL_ENTRIES |
| SCR-REQ-FIN-007 | الفترات والسنوات المالية / Fiscal periods & years | FIN_PERIODS |
| SCR-REQ-FIN-008 | دفتر الحساب / Account ledger | FIN_ACCOUNT_LEDGER |
| SCR-REQ-FIN-009 | ميزان المراجعة / Trial balance | FIN_TRIAL_BALANCE |
| SCR-REQ-FIN-010 | الميزانية العمومية / Balance sheet | FIN_BALANCE_SHEET |
| SCR-REQ-FIN-011 | قائمة الدخل / Income statement | FIN_INCOME_STATEMENT |
| SCR-REQ-FIN-012 | تقارير الأبعاد / Dimension reports | FIN_DIMENSION_REPORTS |

Requirements
REQ count: 46 · AC count: 46 · RULE count: 17 · ENT count: 14 · SCR-REQ count: 12
Last sequence per atom: REQ: 046 · AC: 046 · ENT: 014 · RULE: 017 · SCR-REQ: 012

REQ ids (full text in srs-fin.md → A4): REQ-FIN-001, REQ-FIN-002, REQ-FIN-003, REQ-FIN-004,
REQ-FIN-005, REQ-FIN-006, REQ-FIN-007, REQ-FIN-008, REQ-FIN-009, REQ-FIN-010, REQ-FIN-011,
REQ-FIN-012, REQ-FIN-013, REQ-FIN-014, REQ-FIN-015, REQ-FIN-016, REQ-FIN-017, REQ-FIN-018,
REQ-FIN-019, REQ-FIN-020, REQ-FIN-021, REQ-FIN-022, REQ-FIN-023, REQ-FIN-024, REQ-FIN-025,
REQ-FIN-026, REQ-FIN-027, REQ-FIN-028, REQ-FIN-029, REQ-FIN-030, REQ-FIN-031, REQ-FIN-032,
REQ-FIN-033, REQ-FIN-034, REQ-FIN-035, REQ-FIN-036, REQ-FIN-037, REQ-FIN-038, REQ-FIN-039,
REQ-FIN-040, REQ-FIN-041, REQ-FIN-042, REQ-FIN-043, REQ-FIN-044, REQ-FIN-045, REQ-FIN-046

AC ids (full text in srs-fin.md → A4, one per REQ above): AC-FIN-001, AC-FIN-002, AC-FIN-003,
AC-FIN-004, AC-FIN-005, AC-FIN-006, AC-FIN-007, AC-FIN-008, AC-FIN-009, AC-FIN-010,
AC-FIN-011, AC-FIN-012, AC-FIN-013, AC-FIN-014, AC-FIN-015, AC-FIN-016, AC-FIN-017,
AC-FIN-018, AC-FIN-019, AC-FIN-020, AC-FIN-021, AC-FIN-022, AC-FIN-023, AC-FIN-024,
AC-FIN-025, AC-FIN-026, AC-FIN-027, AC-FIN-028, AC-FIN-029, AC-FIN-030, AC-FIN-031,
AC-FIN-032, AC-FIN-033, AC-FIN-034, AC-FIN-035, AC-FIN-036, AC-FIN-037, AC-FIN-038,
AC-FIN-039, AC-FIN-040, AC-FIN-041, AC-FIN-042, AC-FIN-043, AC-FIN-044, AC-FIN-045,
AC-FIN-046

RULE ids (full text in srs-fin.md → A5): RULE-FIN-001, RULE-FIN-002, RULE-FIN-003,
RULE-FIN-004, RULE-FIN-005, RULE-FIN-006, RULE-FIN-007, RULE-FIN-008, RULE-FIN-009,
RULE-FIN-010, RULE-FIN-011, RULE-FIN-012, RULE-FIN-013, RULE-FIN-014, RULE-FIN-015,
RULE-FIN-016, RULE-FIN-017

Decisions
ADR ids: none.

Event
"P1 completed: FIN v1 — 14 entities, 46 requirements, 46 acceptance criteria, 16 rules, 12 screen requirements, 0 ADRs"
(RULE-FIN-017 — fiscal-year/period/docDate coherence — was added later, during SVC-API, and
carried back into srs-fin.md §A5; the counts above are the current 17, while this event line
records what P1 itself emitted.)
══════════════════════════════════════════════════════════════════
