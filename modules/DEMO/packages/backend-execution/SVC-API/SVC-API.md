<!-- source: PHASE:SVC-API -->
<!-- traces: DBF-DEMO-001, DBF-DEMO-002, DBF-DEMO-003, DBF-DEMO-004, DBF-DEMO-008, REQ-DEMO-001, REQ-DEMO-002, REQ-DEMO-003, REQ-DEMO-004, REQ-DEMO-005 -->
<!-- PHASE:SVC-API:START traces=REQ-DEMO-001,REQ-DEMO-002,REQ-DEMO-003,REQ-DEMO-004,REQ-DEMO-005,DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003,DBF-DEMO-004,DBF-DEMO-008 -->
### PHASE: SVC-API — service + API

No SUB split (5 API atoms, under the 8-endpoint threshold).

<!-- API:API-DEMO-001:START traces=REQ-DEMO-001,DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003 -->
### API-DEMO-001 — create note
Endpoint     : /api/v1/demo/notes   verb: POST
Layers       : controller.createNote → service.createNote
Request      : body DTO `CreateNoteRequest {title: string, content: string}`; excluded system fields: id, activeFl, createdBy, createdAt, updatedBy, updatedAt
Response     : status 201; DTO `NoteResponse {id, title, content, activeFl, createdAt, updatedAt}`; paginated? no; envelope ApiResponse<NoteResponse>
Validations  : RULE-DEMO-001 (title required — ar: "عنوان الملاحظة مطلوب" / en: "Note title is required"); RULE-DEMO-002 (content ≤ 4000 chars — ar: "محتوى الملاحظة يتجاوز الحد الأقصى المسموح (4000 حرف)" / en: "Note content exceeds the maximum allowed length (4000 characters)")
Errors       : DEMO_NOTE_TITLE_REQUIRED (400, RULE-DEMO-001); DEMO_NOTE_CONTENT_TOO_LONG (400, RULE-DEMO-002)
Orchestration: load — (none, new record) → validate (RULE-DEMO-001, RULE-DEMO-002) → integrate — (none, no XM) → persist (QR-DEMO-001, demo_note, GENERATED ALWAYS AS IDENTITY)
Repository   : QR-DEMO-001 · SAVE · join NONE · transaction READ_WRITE
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_CREATE — enforced before processing
Localization : messages ar+en above; no name field beyond user-entered title (free text, not per-language)
<!-- API:API-DEMO-001:END -->

<!-- API:API-DEMO-002:START traces=REQ-DEMO-002,DBF-DEMO-002,DBF-DEMO-008 -->
### API-DEMO-002 — search notes
Endpoint     : /api/v1/demo/notes   verb: GET
Layers       : controller.searchNotes → service.searchNotes
Request      : query params `titleFilter?: string, page: number = 0, size: number = 20 (max 200)`
Response     : status 200; DTO `Page<NoteResponse>`; paginated? yes (Page<T>); envelope ApiResponse<Page<NoteResponse>>
Validations  : none (search has no RULE)
Errors       : none beyond platform-standard (malformed paging params — framework-level, not module-specific)
Orchestration: load (QR-DEMO-002, filtered by current user + activeFl=TRUE) → validate — (none) → integrate — (none) → persist — (none, read-only)
Repository   : QR-DEMO-002 · FIND_BY_CRITERIA · join NONE · transaction READ_ONLY
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_VIEW — enforced before processing
Localization : empty-state message ar: "لا توجد ملاحظات بعد" · en: "No notes yet" (AC-DEMO-005) — rendered by the caller on empty content, not a server error
<!-- API:API-DEMO-002:END -->

<!-- API:API-DEMO-003:START traces=REQ-DEMO-003,DBF-DEMO-001,DBF-DEMO-002,DBF-DEMO-003 -->
### API-DEMO-003 — read note
Endpoint     : /api/v1/demo/notes/{id}   verb: GET
Layers       : controller.getNote → service.getNote
Request      : path param `id: Long`
Response     : status 200; DTO `NoteResponse`; paginated? no; envelope ApiResponse<NoteResponse>
Validations  : none beyond existence (RULE = PLATFORM-STD, ADR-DEMO-002)
Errors       : DEMO_NOTE_NOT_FOUND (404, PLATFORM-STD, ADR-DEMO-002)
Orchestration: load (QR-DEMO-003) → validate (existence, ADR-DEMO-002) → integrate — (none) → persist — (none, read-only)
Repository   : QR-DEMO-003 · FIND_ONE · join NONE · transaction READ_ONLY
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_VIEW — enforced before processing
Localization : not-found message ar/en in the catalog row (§7)
<!-- API:API-DEMO-003:END -->

<!-- API:API-DEMO-004:START traces=REQ-DEMO-004,DBF-DEMO-002,DBF-DEMO-003,DBF-DEMO-008 -->
### API-DEMO-004 — update note
Endpoint     : /api/v1/demo/notes/{id}   verb: PUT
Layers       : controller.updateNote → service.updateNote
Request      : path param `id: Long`; body DTO `UpdateNoteRequest {title: string, content: string}`; excluded system fields: id, activeFl, createdBy, createdAt, updatedBy, updatedAt
Response     : status 200; DTO `NoteResponse`; paginated? no; envelope ApiResponse<NoteResponse>
Validations  : RULE-DEMO-001; RULE-DEMO-002; existence (RULE = PLATFORM-STD, ADR-DEMO-002)
Errors       : DEMO_NOTE_TITLE_REQUIRED (400, RULE-DEMO-001); DEMO_NOTE_CONTENT_TOO_LONG (400, RULE-DEMO-002); DEMO_NOTE_NOT_FOUND (404, PLATFORM-STD, ADR-DEMO-002)
Orchestration: load (QR-DEMO-003, verify ownership + active) → validate (RULE-DEMO-001, RULE-DEMO-002) → integrate — (none) → persist (QR-DEMO-004)
Repository   : QR-DEMO-004 · UPDATE · join NONE · transaction READ_WRITE
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_UPDATE — enforced before processing
Localization : messages ar+en above
<!-- API:API-DEMO-004:END -->

<!-- API:API-DEMO-005:START traces=REQ-DEMO-005,DBF-DEMO-004 -->
### API-DEMO-005 — deactivate note
Endpoint     : /api/v1/demo/notes/{id}   verb: DELETE
Layers       : controller.deactivateNote → service.deactivateNote
Request      : path param `id: Long`
Response     : status 200; confirmation body `{deactivated: true}`; paginated? no; envelope ApiResponse<Confirmation>
Validations  : existence (RULE = PLATFORM-STD, ADR-DEMO-002)
Errors       : DEMO_NOTE_NOT_FOUND (404, PLATFORM-STD, ADR-DEMO-002)
Orchestration: load (QR-DEMO-003, verify ownership + active) → validate (existence) → integrate — (none) → persist (QR-DEMO-005, flip is_active_fl)
Repository   : QR-DEMO-005 · UPDATE (flag flip) · join NONE · transaction READ_WRITE
Security     : screen SCR-REQ-DEMO-001 · permission PERM_PAGE_DEMO_NOTES_DELETE — enforced before processing
Localization : confirmation message ar: "تم حذف الملاحظة" · en: "Note deleted" (AC-DEMO-010)
<!-- API:API-DEMO-005:END -->
<!-- PHASE:SVC-API:END -->
