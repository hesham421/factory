<!-- P2 stage output — governed by factory.yaml stages[P2]; see shared/REGISTRY-SCHEMA.md -->
## REGISTRY — P2 — FIN v1

Tables :
| Table | ENT id | Kind | DBF range |
|---|---|---|---|
| fin_account | ENT-FIN-001 | master | DBF-FIN-001 … DBF-FIN-014 |
| fin_dimension | ENT-FIN-002 | config | DBF-FIN-015 … DBF-FIN-020 |
| fin_dimension_value | ENT-FIN-002 | config | DBF-FIN-021 … DBF-FIN-027 |
| fin_lookup_type | ENT-FIN-003 | lookup | DBF-FIN-028 … DBF-FIN-032 |
| fin_lookup_value | ENT-FIN-003 | lookup | DBF-FIN-033 … DBF-FIN-039 |
| fin_event_rule | ENT-FIN-004 | config | DBF-FIN-040 … DBF-FIN-048 |
| fin_rule_line | ENT-FIN-005 | config | DBF-FIN-049 … DBF-FIN-061 |
| fin_rule_line_mapping | ENT-FIN-005 | config | DBF-FIN-062 … DBF-FIN-066 |
| fin_journal_entry | ENT-FIN-006 | transactional | DBF-FIN-067 … DBF-FIN-082 |
| fin_journal_entry_line | ENT-FIN-007 | transactional | DBF-FIN-083 … DBF-FIN-090 |
| fin_journal_entry_line_dim | ENT-FIN-007 | transactional | DBF-FIN-091 … DBF-FIN-093 |
| fin_recurring_template | ENT-FIN-008 | config | DBF-FIN-094 … DBF-FIN-104 |
| fin_recurring_template_line | ENT-FIN-008 | config | DBF-FIN-105 … DBF-FIN-111 |
| fin_recurring_template_line_dim | ENT-FIN-008 | config | DBF-FIN-112 … DBF-FIN-114 |
| fin_allocation_rule | ENT-FIN-009 | config | DBF-FIN-115 … DBF-FIN-123 |
| fin_allocation_rule_dim | ENT-FIN-009 | config | DBF-FIN-124 … DBF-FIN-126 |
| fin_allocation_rule_line | ENT-FIN-009 | config | DBF-FIN-127 … DBF-FIN-132 |
| fin_allocation_rule_line_dim | ENT-FIN-009 | config | DBF-FIN-133 … DBF-FIN-135 |
| fin_fiscal_year | ENT-FIN-010 | master | DBF-FIN-136 … DBF-FIN-147 |
| fin_fiscal_period | ENT-FIN-011 | master | DBF-FIN-148 … DBF-FIN-163 |
| fin_user | ENT-FIN-012 | security | DBF-FIN-164 … DBF-FIN-174 |
| fin_role | ENT-FIN-013 | security | DBF-FIN-175 … DBF-FIN-183 |
| fin_role_permission | ENT-FIN-013 | security | DBF-FIN-184 … DBF-FIN-187 |
| fin_user_role | ENT-FIN-013 | security | DBF-FIN-188 … DBF-FIN-190 |

DBF ids : DBF-FIN-001, DBF-FIN-002, DBF-FIN-003, DBF-FIN-004, DBF-FIN-005, DBF-FIN-006, DBF-FIN-007, DBF-FIN-008, DBF-FIN-009, DBF-FIN-010, DBF-FIN-011, DBF-FIN-012, DBF-FIN-013, DBF-FIN-014, DBF-FIN-015, DBF-FIN-016, DBF-FIN-017, DBF-FIN-018, DBF-FIN-019, DBF-FIN-020, DBF-FIN-021, DBF-FIN-022, DBF-FIN-023, DBF-FIN-024, DBF-FIN-025, DBF-FIN-026, DBF-FIN-027, DBF-FIN-028, DBF-FIN-029, DBF-FIN-030, DBF-FIN-031, DBF-FIN-032, DBF-FIN-033, DBF-FIN-034, DBF-FIN-035, DBF-FIN-036, DBF-FIN-037, DBF-FIN-038, DBF-FIN-039, DBF-FIN-040, DBF-FIN-041, DBF-FIN-042, DBF-FIN-043, DBF-FIN-044, DBF-FIN-045, DBF-FIN-046, DBF-FIN-047, DBF-FIN-048, DBF-FIN-049, DBF-FIN-050, DBF-FIN-051, DBF-FIN-052, DBF-FIN-053, DBF-FIN-054, DBF-FIN-055, DBF-FIN-056, DBF-FIN-057, DBF-FIN-058, DBF-FIN-059, DBF-FIN-060, DBF-FIN-061, DBF-FIN-062, DBF-FIN-063, DBF-FIN-064, DBF-FIN-065, DBF-FIN-066, DBF-FIN-067, DBF-FIN-068, DBF-FIN-069, DBF-FIN-070, DBF-FIN-071, DBF-FIN-072, DBF-FIN-073, DBF-FIN-074, DBF-FIN-075, DBF-FIN-076, DBF-FIN-077, DBF-FIN-078, DBF-FIN-079, DBF-FIN-080, DBF-FIN-081, DBF-FIN-082, DBF-FIN-083, DBF-FIN-084, DBF-FIN-085, DBF-FIN-086, DBF-FIN-087, DBF-FIN-088, DBF-FIN-089, DBF-FIN-090, DBF-FIN-091, DBF-FIN-092, DBF-FIN-093, DBF-FIN-094, DBF-FIN-095, DBF-FIN-096, DBF-FIN-097, DBF-FIN-098, DBF-FIN-099, DBF-FIN-100, DBF-FIN-101, DBF-FIN-102, DBF-FIN-103, DBF-FIN-104, DBF-FIN-105, DBF-FIN-106, DBF-FIN-107, DBF-FIN-108, DBF-FIN-109, DBF-FIN-110, DBF-FIN-111, DBF-FIN-112, DBF-FIN-113, DBF-FIN-114, DBF-FIN-115, DBF-FIN-116, DBF-FIN-117, DBF-FIN-118, DBF-FIN-119, DBF-FIN-120, DBF-FIN-121, DBF-FIN-122, DBF-FIN-123, DBF-FIN-124, DBF-FIN-125, DBF-FIN-126, DBF-FIN-127, DBF-FIN-128, DBF-FIN-129, DBF-FIN-130, DBF-FIN-131, DBF-FIN-132, DBF-FIN-133, DBF-FIN-134, DBF-FIN-135, DBF-FIN-136, DBF-FIN-137, DBF-FIN-138, DBF-FIN-139, DBF-FIN-140, DBF-FIN-141, DBF-FIN-142, DBF-FIN-143, DBF-FIN-144, DBF-FIN-145, DBF-FIN-146, DBF-FIN-147, DBF-FIN-148, DBF-FIN-149, DBF-FIN-150, DBF-FIN-151, DBF-FIN-152, DBF-FIN-153, DBF-FIN-154, DBF-FIN-155, DBF-FIN-156, DBF-FIN-157, DBF-FIN-158, DBF-FIN-159, DBF-FIN-160, DBF-FIN-161, DBF-FIN-162, DBF-FIN-163, DBF-FIN-164, DBF-FIN-165, DBF-FIN-166, DBF-FIN-167, DBF-FIN-168, DBF-FIN-169, DBF-FIN-170, DBF-FIN-171, DBF-FIN-172, DBF-FIN-173, DBF-FIN-174, DBF-FIN-175, DBF-FIN-176, DBF-FIN-177, DBF-FIN-178, DBF-FIN-179, DBF-FIN-180, DBF-FIN-181, DBF-FIN-182, DBF-FIN-183, DBF-FIN-184, DBF-FIN-185, DBF-FIN-186, DBF-FIN-187, DBF-FIN-188, DBF-FIN-189, DBF-FIN-190

XM index : none — FIN declares zero cross-module dependencies (fully isolated, `DEPENDENCIES: NONE`, `ROOT: YES`; SRS A8; module-registry-fin.md).

Lookups : payment-methods (0 seeded values) · accounting-event-types (0 seeded values) · account-types (5 seeded values) · period-states (3 seeded values) · journal-types (5 seeded values) — owner: FIN (own tables, not MDL)

Sequences : last DBF: DBF-FIN-190 · last XM: none

Decisions : ADR-FIN-001, ADR-FIN-002, ADR-FIN-003 (carried from P1) · ADR-FIN-004, ADR-FIN-005 (new, this stage) — all ACCEPTED — none BLOCKED

Event : "P2 completed: FIN v1 — 24 tables, 190 DBF, 0 XM"

Cascade : no registry XM row anywhere in `project-registry.md` targets FIN with
status DEFERRED (FIN has never been a dependency target — it is a ROOT module
with no consumers registered yet); no cascade action required.
