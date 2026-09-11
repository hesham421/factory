<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-005 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-012, AC-SEC-013, AC-SEC-014, AC-SEC-015, AC-SEC-020, AC-SEC-030, API-SEC-012, API-SEC-013, API-SEC-014, API-SEC-015, API-SEC-016, API-SEC-017, REQ-SEC-012, REQ-SEC-013, REQ-SEC-014, REQ-SEC-015, REQ-SEC-020, REQ-SEC-030, SCR-SEC-005 -->
<!-- SUB:F3-SCR-SEC-005:START traces=REQ-SEC-012,REQ-SEC-013,REQ-SEC-014,REQ-SEC-015,REQ-SEC-020,REQ-SEC-030,AC-SEC-012,AC-SEC-013,AC-SEC-014,AC-SEC-015,AC-SEC-020,AC-SEC-030,API-SEC-012,API-SEC-013,API-SEC-014,API-SEC-015,API-SEC-016,API-SEC-017,SCR-SEC-005 -->
### F3 · SCR-SEC-005 — الأدوار والصلاحيات / Roles & permissions

Validation timing for this form: **on blur for the role code, on submit for the rest**.
### F3-FIELD — SCR-SEC-005 (create role)
code          · REQUIRED · LENGTH (maxLength 50) · UNIQUE_CHECK · when blur
nameAr        · REQUIRED · LENGTH (maxLength 150) · when submit
nameEn        · REQUIRED · LENGTH (maxLength 150) · when submit
descriptionAr · optional · LENGTH (maxLength 500) · when submit
descriptionEn · optional · LENGTH (maxLength 500) · when submit
UNIQUE_CHECK  : async, on blur, via `API-SEC-012` with an EQUALS filter on `code`; no edit mode
                exists on this screen, so there is no current record to exclude. The authority
                remains the server's `SEC-409-ROLE-DUP`, routed inline to `code`.
The role code is displayed read-only everywhere after creation — it is the stable machine
reference (SRS ENT-SEC-002) and is never an input a second time.
### F3-VALIDATION — RULE-SEC-001      traces=REQ-SEC-013,AC-SEC-013
Statement : The system shall prevent a screen grant for a role that does not hold the screen's
            module grant.
Message   : from the catalog code `SEC-409-NO-MODULE-GRANT` —
            ar: "لا يمكن منح شاشة دون منح الوحدة أولًا" ·
            en: "Cannot grant a screen without first granting its module"
Scope     : CREATE (a screen grant, API-SEC-016)
Field     : the screen node of the grant tree · kind BUSINESS_RULE · when submit
Validation shape : the tree's own reachability expresses the rule — a screen node is offered
            only beneath a module the role already holds, so the refusal is rare by
            construction. It is never relied on as the enforcement: the server's catalog code
            is routed to a user message beside the node and the tree is re-read, never patched.
### F3-VALIDATION — RULE-SEC-002      traces=REQ-SEC-014,AC-SEC-014
Statement : The system shall prevent an action grant for a role that does not hold the action's
            screen grant.
Message   : from the catalog code `SEC-409-NO-SCREEN-GRANT` —
            ar: "لا يمكن منح إجراء دون منح الشاشة أولًا" ·
            en: "Cannot grant an action without first granting its screen"
Scope     : CREATE (an action grant, API-SEC-017)
Field     : the action node of the grant tree · kind BUSINESS_RULE · when submit
Validation shape : as RULE-SEC-001, one level down — an action node is offered only beneath a
            granted screen; the server's code is the authority.
### F3-VALIDATION — RULE-SEC-007      traces=REQ-SEC-030,AC-SEC-030
Statement : The system shall require a role to hold the VIEW action grant on a screen before
            any other action grant on that screen takes effect for it.
Message   : from the catalog code `SEC-409-NO-VIEW-GRANT` —
            ar: "يلزم منح إجراء العرض (VIEW) أولًا على هذه الشاشة" ·
            en: "The VIEW action must be granted on this screen first"
Scope     : CREATE (an action grant other than VIEW, API-SEC-017)
Field     : the action node · kind BUSINESS_RULE · when submit
Validation shape : the tree presents VIEW as the first action of every screen and marks the
            others unreachable until it is held; the server's code is the authority.
### F3-VALIDATION — RULE-SEC-003      traces=REQ-SEC-015,AC-SEC-015
Statement : The system shall delete every screen grant and action grant that module covered for
            that role when its module grant is revoked.
Message   : ar: "سيتم سحب كل منح الشاشات والإجراءات ضمن هذه الوحدة لهذا الدور" ·
            en: "Every screen and action grant under this module for this role will be revoked"
            (SRS A5 — this is a confirmation, not a rejection: the rule always succeeds)
Scope     : ALL (the module-revoke step, API-SEC-015)
Field     : the module node · kind BUSINESS_RULE · when submit
Validation shape : a blocking confirmation before the call, carrying the message above; after
            the call the returned `revokedScreenGrants` / `revokedActionGrants` counts are
            shown as the outcome and the tree is re-read from the server.
### F3-VALIDATION — RULE-SEC-005      traces=REQ-SEC-020,AC-SEC-020
Statement : The system shall prevent assigning a user, by any combination of roles, both
            actions of a module-declared conflicting pair.
Message   : from the catalog code `SEC-409-SOD-CONFLICT` — ar / en as on SCR-SEC-004
Scope     : CREATE (an action grant, API-SEC-017)
Field     : the action node · kind BUSINESS_RULE · when submit
Validation shape : server-side only — the conflicting pairs are the owning module's
            declaration and no endpoint publishes them (as on SCR-SEC-004).
LOOKUP_VALID : none — every selectable value on this screen is a registry node the server
            returned, so there is no static list to validate against.
Locale       : session → browser → `ar`.
Permission-driven behaviour: a caller without UPDATE receives `ACCESS_DENIED` on a grant and
the tree shows the localized forbidden message, unchanged (ADR-SEC-005).

<!-- SUB:F3-SCR-SEC-005:END -->
