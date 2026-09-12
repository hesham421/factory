<!-- source: PHASE:F3 / SUB:F3-SCR-MDL-002 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-MDL-011, AC-MDL-012, AC-MDL-013, API-MDL-010, API-MDL-011, REQ-MDL-011, REQ-MDL-012, REQ-MDL-013, SCR-MDL-002, UXD-MDL-001 -->
<!-- SUB:F3-SCR-MDL-002:START traces=REQ-MDL-011,REQ-MDL-012,REQ-MDL-013,AC-MDL-011,AC-MDL-012,AC-MDL-013,API-MDL-010,API-MDL-011,UXD-MDL-001,SCR-MDL-002 -->
### F3 · SCR-MDL-002 — سجل أنواع اللوكب حسب المالك / Lookup-type registry by owner

This screen has **no form**: SRS SCR-REQ-MDL-002 §B3 reads "read-only browse; no create/update
here", and every field of `OwnerGroupResponse` is read-only.
### F3-FIELD — SCR-MDL-002 (filters, not a form)
ownerModuleCode · optional · the select is the UXD-MDL-001 hook's list, so it offers only
                  registered module codes
key             · optional · LENGTH (maxLength 80) · a LIKE filter
Validation shape : filter validation only, written with `zod` over the route's search params so
                  that an address someone shared is validated the same way a typed filter is.
                  No business rule is enforced here, because nothing is written.
No RULE-* is enforced on this screen. RULE-MDL-004's effect is visible — a deactivated type
leaves this registry's active set — but the rule fires on the consumer read, not here.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without VIEW never reaches this screen — the navigation
guard of SEC-FE stops the route.
<!-- SUB:F3-SCR-MDL-002:END -->
