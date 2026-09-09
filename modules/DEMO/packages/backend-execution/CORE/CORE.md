<!-- source: PHASE:CORE -->
<!-- traces: REQ-DEMO-001, REQ-DEMO-002, REQ-DEMO-003, REQ-DEMO-004, REQ-DEMO-005 -->
<!-- PHASE:CORE:START traces=REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: CORE — architecture policies

**Layers.** controller → service → mapper → domain (entity) → repository.
- Controller: HTTP binding, DTO validation annotations, permission gateway check only — no business logic.
- Service: orchestrates load → validate (RULE-*) → integrate (none — no XM) → persist (QR-*); the only layer allowed to throw `LocalizedException`.
- Mapper: entity ↔ DTO conversion only; never applies a RULE.
- Domain (entity): `Note` carries no behaviour beyond getters/setters for this module (simple kind) — domain-behaviour placement: entity methods only where a RULE is a pure invariant (title non-empty, content length); everything else lives in the service.
- Repository: QR-* implementations only; no business logic.

**Error signalling.** `LocalizedException → {code, messageAr, messageEn}`; runtime code format: the exact string in the Error Catalog (§7), serialized as the `code` field of the framework's standard error envelope.

**Transaction defaults.** READ_ONLY for FIND_*; READ_WRITE for SAVE/UPDATE (per QRC, §5 above).

**Search contract.** Request shape: `{titleFilter?: string, page: number, size: number}`; allowed sort field: `updatedAt` (default, DESC); paging via `Page<T>`.

**Audit fields.** `createdBy, createdAt, updatedBy, updatedAt` are framework-filled on every write; never accepted in create/update request DTOs, never set by mappers or services.

**Type mapping (postgresql16 → framework types).**
| postgresql16 | Framework type |
|---|---|
| GENERATED ALWAYS AS IDENTITY | Long |
| VARCHAR(n) | String |
| TEXT | String |
| BOOLEAN | boolean |
| TIMESTAMPTZ | Instant |

**Lookup values.** Not applicable — DEMO owns no lookup.

**Numbering.** Not applicable — Note has no business/document number (§3.3 test, all "no").

**Workflow engine.** Forbidden (profile) — not used; DEMO has no status lifecycle beyond the `activeFl` flag.

**Languages.** Every user-facing message carries `ar` and `en` (Error Catalog, §7); `Note.title`/`Note.content` are free-text user content, not per-language reference data (domain-profile §5) — no `titleAr`/`titleEn` split.

**Cross-module contract placement.** Not applicable — DEMO exposes and consumes no cross-module interface in v1.
<!-- PHASE:CORE:END -->
