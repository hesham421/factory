<!-- source: PHASE:DOC -->
<!-- traces: REQ-DEMO-001, REQ-DEMO-002, REQ-DEMO-003, REQ-DEMO-004, REQ-DEMO-005 -->
<!-- PHASE:DOC:START traces=REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005 -->
### PHASE: DOC — contract documentation (internal, backend self-check only)

**API contract summary**
| API | Path | Verb | Request DTO | Response DTO | Stability |
|---|---|---|---|---|---|
| API-DEMO-001 | /api/v1/demo/notes | POST | CreateNoteRequest | NoteResponse | DRAFT — this summary is superseded by the published `api-docs-demo.md` after implementation |
| API-DEMO-002 | /api/v1/demo/notes | GET | (query params) | Page\<NoteResponse\> | DRAFT |
| API-DEMO-003 | /api/v1/demo/notes/{id} | GET | (path param) | NoteResponse | DRAFT |
| API-DEMO-004 | /api/v1/demo/notes/{id} | PUT | UpdateNoteRequest | NoteResponse | DRAFT |
| API-DEMO-005 | /api/v1/demo/notes/{id} | DELETE | (path param) | Confirmation | DRAFT |

**DTO typing constraints.** No lookup-backed fields in this module (none to constrain). Note has no business code, so none is ever present in create/update bodies (there is none to exclude/include).

**Pagination + filter standard.** Request shape `{titleFilter?, page, size}`; allowed sort field `updatedAt` (DESC default); an empty result is success with empty content, never "not found" (applies to API-DEMO-002 only).

This section is a backend self-check only; the frontend stage binds to the real `api-docs-demo.md` published after implementation (factory.passes.2.required_inputs), never to this summary.
<!-- PHASE:DOC:END -->
