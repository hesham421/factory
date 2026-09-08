## BUSINESS POLICIES — Daily Notes / Demo (DEMO)
══════════════════════════════════════════════════════════════════
Module   : DEMO     Source of truth : user vision text + dialogue resolutions
Read by  : P0.5 (every user story cites the policies it serves)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES   (only from user text or confirmed dialogue answers)
None — standard domain rules apply. The user's brief ("simple daily notes
with just CRUD") states no client-specific constraint beyond plain CRUD;
no POL record is created for this module.

CUSTOM LOOKUP VALUES   (values the user named that the standard lists lack)
None — standard values apply.

SCOPE EXCEPTIONS   (explicit exclusions or non-standard scope)
| Excluded / Deferred | Statement | Activation trigger | Source |
|---|---|---|---|
| Sharing / multi-user notebooks | "just CRUD" — no sharing, permissions-per-note, or collaboration implied | a future version explicitly requesting multi-user notes | domain-profile §7.1 (Daily Notes term — "do not say" notebook system) |
| Approval / workflow on notes | ERP approval-workflow conventions are not applied to DEMO | none planned — DEMO is a pipeline-test harness, not a real workflow-bearing module | domain-profile §5 |

RESOLVED DECISIONS (dialogue, this module)
| # | Question | Recommended answer | Confirmed by user | Sources |
|---|---|---|---|---|
| 1 | Does "just CRUD" imply any client-specific business policy beyond standard create/read/update/delete? | No — treat "just CRUD" literally; write no POL record rather than inventing one. | Confirmed (no objection; matches the user's literal framing). | domain-profile §2, §3 |
══════════════════════════════════════════════════════════════════
