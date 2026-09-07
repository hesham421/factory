# FLOW DIAGRAM — الملاحظات الشخصية (Personal Notes) — DEMO
══════════════════════════════════════════════════════════════════
Module   : DEMO
Mode     : RECONCILE MODE — srs-demo.md is attached; Reconciliation
           Gate run against prd-demo.md (see below)
Date     : 2026-09-07
Status   : RECONCILED
══════════════════════════════════════════════════════════════════

## RECONCILIATION GATE — prd-demo.md ↔ srs-demo.md

| US-ID | SCR-ID (SRS) | Traceable? | Notes |
|---|---|---|---|
| US-DEMO-001 (Create) | SCR-DEMO-001 | YES | API-DEMO-001 |
| US-DEMO-002 (List) | SCR-DEMO-001 | YES | API-DEMO-002 |
| US-DEMO-003 (Read one) | SCR-DEMO-001 | YES | API-DEMO-003 |
| US-DEMO-004 (Update) | SCR-DEMO-001 | YES | API-DEMO-004 |
| US-DEMO-005 (Delete) | SCR-DEMO-001 | YES | API-DEMO-005 |

Every US-ID reconciles cleanly to SCR-DEMO-001 — no US-ID is
BLOCKED-BY-OQ. No field/permission drift: srs-demo.md B1-B4 defines
exactly title + content (matching prd-demo.md's traced sources), owner-
only access, no additional fields or permissions introduced or dropped.
No RECONCILE-DEMO OQ raised.

---

## flow-diagram-demo.md — DEMO — canonical format
──────────────────────────────────────────────────────────────────
FLOW-DEMO-001
  Screens involved : SCR-DEMO-001 (single unified screen — list +
                      Side Drawer for create/edit, per PATTERN-2)
  Sequence         : [Module entry] → SCR-DEMO-001 (My Notes list,
                      ACTIVE notes only) →
                        [New] → Side Drawer (empty form) → Save →
                          back to list (new note visible)
                        [select existing note] → Side Drawer
                          (pre-filled) → Save → back to list (updated)
                        [select existing note] → Side Drawer →
                          Delete → back to list (note removed from
                          the ACTIVE view)
                      → [Exit] (navigate away from module)
  Trigger          : User opens the Personal Notes module.
  Source US-ID(s)  : US-DEMO-001, US-DEMO-002, US-DEMO-003,
                      US-DEMO-004, US-DEMO-005
  Source SCR-ID(s) : SCR-DEMO-001
  Priority         : — (not stated in prd-demo.md)
  Status           : RECONCILED
──────────────────────────────────────────────────────────────────

Only one FLOW block — the module has exactly one screen (PATTERN-2
composite; SRS explicitly declares "لا شاشات إضافية" / no additional
screens, B1).

## UXD-ID — UI Cross-Dependency Governance

None. SCR-DEMO-001 displays no data owned by another module's API —
this platform currently has no other module. No UXD-[MOD]-[SEQ]
assigned.

══════════════════════════════════════════════════════════════════
*End of flow-diagram-demo.md*
*Next: ui-ux-spec-demo.md (same session, STAGE B)*
══════════════════════════════════════════════════════════════════
