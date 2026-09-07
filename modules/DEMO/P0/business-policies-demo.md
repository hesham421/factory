## BUSINESS POLICIES — DEMO (Personal Notes)
══════════════════════════════════════════════════════════════════
Module      : Personal Notes
P0 Date     : 2026-09-07
Domain KB Pattern : N/A — GENERAL domain, no Knowledge Base pattern
                     library in use (see module-registry-demo.md)
P1 reads    : CLIENT-SPECIFIC entries → RULE-IDs marked "Source: Client"
              Standard rules → applied by P1 directly (owner-based
              access + audit fields, per platform-standards.md)
══════════════════════════════════════════════════════════════════

CLIENT-SPECIFIC POLICIES
──────────────────────────────────────────────────────────────────
None beyond the brief itself — standard platform rules apply. The
brief ("عنوان + محتوى + CRUD كامل" — title + content, full CRUD) states
the entire functional scope; there is no additional client-specific
policy language to extract. Standard owner-based access and audit-field
conventions (domain/domain-profile.md, platform-standards.md) apply
without a POLICY-CLI entry, since they are already the platform default,
not a DEMO-specific exception.

──────────────────────────────────────────────────────────────────
CUSTOM LOV VALUES
──────────────────────────────────────────────────────────────────
None — NOTE_STATUS (ACTIVE, DELETED) as declared in
module-registry-demo.md is the complete value set; no additional
client-requested values.

──────────────────────────────────────────────────────────────────
SCOPE EXCEPTIONS
──────────────────────────────────────────────────────────────────
The brief itself is the scope boundary — explicitly "simple" personal
notes. The following are noted here (not as formal exclusions the user
stated, but as boundary calls the analyst made from the brief's plain
reading, for P1/reviewers to confirm rather than silently assume):
  - No sharing/collaboration between users.
  - No tags, folders, categories, or search-by-content beyond a basic
    list/search screen.
  - No attachments or rich text — content is a plain text field.
  - No note revision history / versioning of content.
Any of the above becoming in-scope is a new module version (IFA), not
a v1 change.
══════════════════════════════════════════════════════════════════
