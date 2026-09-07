# ERP GOVERNANCE — XM RESOLUTION EVENT PROTOCOL
## Inter-Module Dependency Orchestration

```
File ID        : XM-RESOLUTION-EVENT-PROTOCOL
Status         : MANDATORY — governs XM dependency lifecycle events
                 (Backend-only concern — v2.0: XM-IDs never exist in
                 the Frontend pass, see CORE-2 note)
Authority      : Database Governance Engine (Project 2) initiates;
                 Execution Plan Governance Engine, Backend Pass
                 (Project 3.1) responds;
                 Governance Audit Engine, Backend Gate (Project 4.1)
                 confirms closure
Embedded in    : Project 2, Project 3.1 (Backend), Project 4.1 (Backend)
                 — NOT embedded in Project 3.2, Project 4.2, or any
                 other engine, since XM-IDs are exclusively a Backend
                 concern (CORE-5 RULE-6)
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 1 — PURPOSE
═══════════════════════════════════════════════════════════════════

The XM Resolution Event (RXE) is the governed mechanism by which a
change in one module's pipeline state is communicated to modules that
hold XM dependencies on it. It replaces informal inter-team communication
for dependency resolution with a traceable, auditable governance event.

An RXE is triggered when the conditions that would allow a DEFERRED
or CONDITIONAL XM dependency to advance toward READY or CLOSED are met.

**RXE does NOT replace:**
- The XM Register (structural facts in db-script.md)
- The INT Summary (execution-level XM status in backend-execution-plan.md,
  owned by Project 3.1)
- The Global XM Dependency Index (ecosystem-level tracking in master-registry.md)

**RXE IS:**
- The event that signals a dependent module to re-evaluate its XM status
- The trigger for registry cascade updates (Section 12, MASTER-REGISTRY-SCHEMA.md)
- The audit trail for inter-module dependency resolution

---

═══════════════════════════════════════════════════════════════════
# SECTION 2 — RXE-ID FORMAT
═══════════════════════════════════════════════════════════════════

```
RXE-[TARGET-MODULE-PREFIX]-[3-digit-seq]

Examples:
  RXE-FIN-001   : First resolution event targeting Finance GL
  RXE-PRC-002   : Second resolution event targeting Procurement

Sequence: per target module, independent across target modules.

Note: RXE-ID belongs to the target module's ID space —
because it is a governance action RECEIVED by that module.
The initiating module records the RXE-ID in the Global XM Index
as a reference. The target module tracks it in its XM Register
amendment and INT Summary.
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 3 — TRIGGER CONDITIONS
═══════════════════════════════════════════════════════════════════

An RXE is created when ANY of the following events occurs:

**TRIGGER-1: Target Module DB Script Gated (DEFERRED → READY candidate)**

When Module X completes its DB Script generation (Project 2 — "MODE
1.5" in the legacy mode-numbering scheme) and its db-script.md receives a
DBS-ID (gate passed), the Registry Maintainer:

1. Scans Global XM Dependency Index for all rows where:
   - To Module = Module X
   - Status = DEFERRED
2. For each such row, evaluates:
   - Is the target table in Module X's now-gated DB Script? → READY candidate
   - Is Module X in GOVERNANCE REDUCED state? → CONDITIONAL (not READY)
3. Creates one RXE per dependent module (not per XM-ID — one event covers
   all XM-IDs from a given dependent module to the newly gated target module)

**TRIGGER-2: Shared Entity Amended by Owner**

When Module X amends a SHARED entity (new DBF-IDs, deprecated columns,
constraint changes) and the amended db-script.md receives an updated DBS-ID:

1. Scan Global XM Dependency Index for all rows where:
   - To Module = Module X
   - Type = HARD-FK or SOFT-READ
   - Status = READY or CLOSED
2. Create RXE for each dependent module — signaling that the SHARED
   entity has changed and impact assessment is required.

**TRIGGER-3: GOVERNANCE RECOVERY Completed**

When Module X completes GOVERNANCE RECOVERY (transitions from
GOVERNANCE REDUCED to FULL governance with a validated DBS-ID):
Same process as TRIGGER-1.

**TRIGGER-4: XM READY → CLOSED Confirmed**

When Module Y's Project 4.1 (Backend Audit Gate) confirms that
XM-[Y]-[N] FK constraint has been physically applied to the database:
Status transitions to CLOSED.
No RXE is generated for closure — it is logged in the Registry Event Log.
(NOTE: this previously referenced "MODE 4B" — corrected here; MODE 4B
was already abolished ecosystem-wide before v2.0 and this reference
was simply never updated.)

---

═══════════════════════════════════════════════════════════════════
# SECTION 4 — RXE RECORD FORMAT
═══════════════════════════════════════════════════════════════════

Each RXE is a formal governance record. It is stored in:
1. The Global XM Dependency Index (RXE-ID column)
2. The Registry Event Log (master-registry.md Section 11)
3. The target module's XM Register amendment record

```
## XM RESOLUTION EVENT — RXE-[TARGET-MODULE]-[SEQ]
══════════════════════════════════════════════════════════════════
RXE-ID           : RXE-[TARGET-MODULE-PREFIX]-[SEQ]
Date Created     : [date]
Trigger          : [TRIGGER-1 / TRIGGER-2 / TRIGGER-3]
Initiating Module: [module that had the pipeline change]
Target Module    : [module that holds the XM dependencies]
Affected XM-IDs  : [XM-[TARGET-MOD]-[N], XM-[TARGET-MOD]-[M], ...]
──────────────────────────────────────────────────────────────────
Change Summary   : [brief description of what changed in the initiating module]
                   Example: "DBS-FIN-01 gated. Tables FIN_GL_ACCOUNT,
                   FIN_JOURNAL_ENTRY now available."
──────────────────────────────────────────────────────────────────
Required Action  : [what the target module must do]
                   Examples:
                   "Re-evaluate XM-PRC-001 DEFERRED→READY. Update INT Summary.
                    Run XM Register amendment. Update Global XM Index."
──────────────────────────────────────────────────────────────────
Status           : OPEN | ACKNOWLEDGED | RESOLVED | WAIVED
Acknowledged By  : [governance engine that processed this event]
Resolved Date    : [date — when XM-ID status updated in INT Summary]
══════════════════════════════════════════════════════════════════
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 5 — TARGET MODULE RESPONSE PROTOCOL
═══════════════════════════════════════════════════════════════════

When a target module's governance session encounters an OPEN RXE
in the Global XM Dependency Index (visible at any entry gate), the
following protocol is mandatory before proceeding:

```
XM RESOLUTION RESPONSE PROTOCOL

STEP 1 — ACKNOWLEDGE
  Target module governance engine reads the RXE record.
  Confirms: which XM-IDs are affected (from Global XM Index).
  Updates RXE Status: OPEN → ACKNOWLEDGED.

STEP 2 — EVALUATE
  For each affected XM-ID:
    If TRIGGER-1 or TRIGGER-3 (new DBS-ID available):
      Can the DEFERRED FK now be implemented?
      Is the target table available in the new DB Script?
      → Yes: classify as READY candidate
      → No: document why DEFERRED persists; update unblock condition
    If TRIGGER-2 (SHARED entity amended):
      Does the amendment affect this module's implementation?
      → Yes: raise OQ-ID in OQ Log; assess impact on B2/F1/TC
      → No: document as no-impact; close with justification

STEP 3 — UPDATE XM REGISTER
  For each XM-ID transitioning DEFERRED → READY:
    Emit XM Register Amendment record (format: Section 5.1 below)
    Update INT Summary: Status column updated
    Add DRV-ID entry: "XM-[ID] transitioned DEFERRED→READY per RXE-[ID]"

STEP 4 — UPDATE GLOBAL XM INDEX
  Registry Maintainer applies:
    XM-ID Status: DEFERRED → READY (or CONDITIONAL if target is REDUCED)
    RXE-ID column: cleared (event resolved)

STEP 5 — MARK RXE RESOLVED
  Update RXE Status: ACKNOWLEDGED → RESOLVED
  Resolved Date: current date
  Log in Registry Event Log.
```

## 5.1 XM Register Amendment Record Format

When an XM-ID transitions status, emit this amendment record in the
module's db-script.md XM Register section:

```
## XM REGISTER AMENDMENT — [Module] — [Date]
──────────────────────────────────────────────────────────────────
XM-ID           : XM-[MODULE]-[SEQ]
Previous Status : DEFERRED
New Status      : READY
Trigger         : RXE-[TARGET-MODULE]-[SEQ]
DBS-ID Available: [DBS-ID of the now-available target module DB Script]
Amendment Note  : [brief note confirming the FK can now be applied]
──────────────────────────────────────────────────────────────────
```

---

═══════════════════════════════════════════════════════════════════
# SECTION 6 — GOVERNANCE AUDIT — RXE COVERAGE
═══════════════════════════════════════════════════════════════════

The Governance Audit Engine, Backend Gate (Project 4.1) includes RXE
coverage in CHECK-5 (Cross-Module Dependencies) — see
PROJECT-4-BACKEND-AUDIT.md.

(NOTE: this section previously referenced "MODE 4B Check 5.1" — MODE
4B was already abolished ecosystem-wide before v2.0 and this section
was simply never updated. It is corrected here to reference Project
4.1's CHECK-5, which is where this coverage actually lives — CHECK-5
already exists in PROJECT-4-BACKEND-AUDIT.md and already includes the
sub-checks below verbatim; this section restates them here only for
RXE-protocol completeness, not as a second authority.)

```
PROJECT 4.1 CHECK-5 — Cross-Module Dependencies — RXE-relevant items:

CHECK-5.4:
  All OPEN RXEs targeting this module at P4.1 entry are RESOLVED
  or formally WAIVED before Backend implementation is cleared to begin.
  An OPEN RXE at P4.1 represents an unacknowledged inter-module
  governance event — this is a MAJOR finding.

CHECK-5.5:
  All XM-IDs that transitioned DEFERRED→READY per an RXE have
  corresponding DRV-ID entries documenting the transition
  rationale in the Derivation Log.
```

Note: RXE coverage is exclusively a Project 4.1 (Backend Gate) concern.
Project 4.2 (Frontend Gate) never checks RXE status — XM-IDs do not
exist in the Frontend pass (CORE-5 RULE-6).

---

═══════════════════════════════════════════════════════════════════
# SECTION 7 — RXE WAIVER PROTOCOL
═══════════════════════════════════════════════════════════════════

An RXE may be WAIVED when:
- The affected XM dependency is no longer valid (architectural change)
- The target module's development is formally cancelled or deferred
- A formal architectural decision supersedes the dependency

Waiver requires:
- Named approver (human — architecture authority)
- Documented reason in the RXE record
- Update to Global XM Dependency Index: XM Status → WAIVED
- Registry Event Log entry

A WAIVED XM-ID is never re-activated. If the dependency reappears,
a new XM-ID is assigned.

---

═══════════════════════════════════════════════════════════════════
# SECTION 8 — GOVERNANCE REDUCED → RECOVERY INTERACTION
═══════════════════════════════════════════════════════════════════

When Module Y is in GOVERNANCE REDUCED state and other modules hold
DEFERRED XM-IDs targeting Module Y:

- Other modules' XM-IDs remain DEFERRED (not CONDITIONAL)
  because Module Y has no confirmed DBS-ID yet
- When Module Y completes GOVERNANCE RECOVERY and receives a valid
  DBS-ID: TRIGGER-1 fires → RXE created for all dependent modules
- CONDITIONAL status is used ONLY when Module Y has a DBS-ID but
  its pipeline is in GOVERNANCE REDUCED state (rare scenario where
  DB Script exists but is not yet fully governed)

This ensures that GOVERNANCE RECOVERY automatically propagates
its resolution benefit to all waiting dependent modules.

---

*End of XM-RESOLUTION-EVENT-PROTOCOL.md*
*RXE-ID owned by: target module's governance space*
*Initiated by: Database Governance Engine (Project 2) / Registry Maintainer*
*Responded to by: target module's Execution Plan Governance Engine,*
*Backend Pass (Project 3.1) — never Project 3.2 (Frontend)*
*Confirmed closed by: Governance Audit Engine, Backend Gate (Project 4.1)*
*at CHECK-5 — never Project 4.2 (Frontend)*
