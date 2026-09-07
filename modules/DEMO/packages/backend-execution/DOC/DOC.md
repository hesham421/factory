<!-- Source: PHASE:DOC -->

## PHASE DOC — Contract Stabilization

### DOC-1: API Contract Summary
─────────────────────────────────────────────────────────────────
API-ID       │ Endpoint                     │ Method │ Request DTO        │ Response DTO  │ Stability
─────────────┼───────────────────────────────┼────────┼─────────────────────┼───────────────┼──────────
API-DEMO-001 │ /api/v1/demo/notes            │ POST   │ CreateNoteRequest   │ NoteResponse  │ STABLE
API-DEMO-002 │ /api/v1/demo/notes            │ GET    │ page, size, sortBy, sortDir │ Page<NoteResponse> │ STABLE
API-DEMO-003 │ /api/v1/demo/notes/{id}       │ GET    │ — (path param only) │ NoteResponse  │ STABLE
API-DEMO-004 │ /api/v1/demo/notes/{id}       │ PUT    │ UpdateNoteRequest   │ NoteResponse  │ STABLE
API-DEMO-005 │ /api/v1/demo/notes/{id}       │ DELETE │ — (path param only) │ NoteResponse  │ STABLE
─────────────────────────────────────────────────────────────────
Unstable APIs: None.
Frontend-governed contracts: None.

### DOC-2: DTO Typing Rules (constraints — DTOs fully defined in PHASE SVC+API)
LOV field typing (statusId): String (stores the fixed code ACTIVE/DELETED
  directly — never an ENUM, per project standard).
Business Code: N/A on this entity — never appears in any DTO.

### DOC-3: Pagination & Filter Standards (project-standard — see PHASE CORE)
Backend strategy : JPA Page<T> — used directly, no custom wrapper.
Request contract : NoteSearchRequest extends BaseSearchContractRequest →
                    page (0-based), size, sortBy, sortDir.
                    ALLOWED_SORT_FIELDS = { updatedAt, createdAt, title }.
Empty result rule : HTTP 200 with empty content — NEVER HTTP 404.
Filter types      : None client-supplied for this module (owner + ACTIVE
                    status are server-fixed, not filters — see API-DEMO-002).

**DOC GATE CHECK (auto-evaluated):**
[ ✓ ] All API-IDs from SVC+API appear in API Contract Summary
[ ✓ ] Error Catalog complete with Arabic + English messages
[ ✓ ] All APIs marked STABLE
[ ✓ ] Pagination standard declared
DOC Gate: PASSED ✓

**v2.0 STATUS NOTE (CONTRACT-12):** DOC-1 above is an internal,
backend-only self-consistency artifact. It does NOT gate P3.2 — that
gate is GATE: BACKEND MODULE COMPLETE (real, post-implementation API
Docs + human-approved P2.5 outputs), evaluated independently and out of
scope for this factory pass.
