Read `GENERATION-INSTRUCTIONS.md` in this folder and execute it exactly.

Analyze the three module plans in the order it specifies (Security first, then Lookup,
then Accounting), honoring every dependency rule, boundary, and the Accounting
"details the analysis agent MUST honor" section. Treat the plans as the source of truth,
use `integration-notifications-fileservice.md` only where a plan calls for it, and target
PostgreSQL. Do not begin a consumer module's analysis before its dependencies are done.