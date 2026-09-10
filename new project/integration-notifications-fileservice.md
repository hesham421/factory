# Integration Guide: Notifications & File Service

Extracted from the actual backend code as of this writing. Everything below cites the file
(and line, where useful) it was read from. Anything not present in the code is marked
**"not found in code."**

Base URL: `server.port=7272` (`src/main/resources/application.properties:14`), no
`server.servlet.context-path` configured, so paths below are relative to
`http://<host>:7272`.

All JSON endpoints are wrapped in the shared envelope
(`src/main/java/com/erp/common/web/ApiResponse.java`):

```json
{ "success": true, "data": { ... }, "error": null, "timestamp": "2026-09-10T12:00:00Z" }
```

On failure, `success:false` and `error` is populated (`ApiError`: `code`, `message`,
`fieldErrors[]`) — see the shared Errors section at the bottom of each module.

---

## 1. Notifications Module (NOTIF)

### 1.1 How it is called

Two integration styles exist, both landing on the same code path
(`DispatchService.doDispatch`, `src/main/java/com/erp/notif/service/DispatchService.java`):

| Style | Entry point | When to use |
|---|---|---|
| REST | `POST /api/v1/notifications/dispatch` (`src/main/java/com/erp/notif/controller/DispatchController.java:35-40`) | Caller is a separate process/service (e.g. a new Spring app calling over HTTP). |
| In-process cross-module bean | `com.erp.notif.crossmodule.NotificationDispatchApi.dispatch(DispatchCommand)` (`src/main/java/com/erp/notif/crossmodule/NotificationDispatchApi.java:13-21`, impl at `NotificationDispatchApiImpl.java`) | Caller is Java code running inside the **same** Spring context/JVM as NOTIF (only applies if the new module is merged into this same deployable — not applicable to a genuinely separate service). |

There is no message queue/topic integration in the code — dispatch is synchronous
request/response only.

No message queue or async broker is used; dispatch is synchronous (see the
`REQUIRES_NEW`/`AFTER_COMMIT` handling below, which is about the DB transaction, not messaging).

### 1.2 Request / input

Real DTO: `com.erp.notif.dto.DispatchRequest`
(`src/main/java/com/erp/notif/dto/DispatchRequest.java`). Same fields carried by the
in-process `DispatchCommand` record (`src/main/java/com/erp/notif/crossmodule/DispatchCommand.java`).

| Field | Type | Required | Notes |
|---|---|---|---|
| `recipientId` | Long | yes | Recipient `UserAccount` id (SEC module). |
| `templateCode` | String (max 80) | yes | Template code to resolve; unknown code → 404. |
| `channelHint` | List\<String\> (each max 20) | yes, non-empty | Requested channels (LOV-NOTIF-001 codes). One `NOTIF_LOG` row is created per requested channel. |
| `moduleCode` | String (max 50) | yes | Code of the sending module, e.g. `"SEC"`. |
| `referenceId` | Long | no | Source entity reference id. |
| `referenceType` | String (max 100) | no | Source entity reference type. |
| `variables` | Map\<String,String\> | no | Template placeholder substitution values. |

Known `channelHint` codes seeded in `MDM_LOOKUP_VALUE` under `NOTIF_CHANNEL`
(`src/main/resources/db/migration/V4__mdm_schema_and_seed.sql:106-110`): `EMAIL`, `SMS`,
`WHATSAPP`, `PUSH`, `INTERNAL`. **Only `EMAIL` has an actual enabled channel config row**
(`src/main/resources/db/migration/V11__notif_email_channel_seed.sql:6-7`) — requesting any
other channel currently resolves to `CHANNEL_DISABLED` (no channel config found), per
`DispatchService.java:120-123`.

Minimal real example (mirrors the shape built in
`src/main/java/com/erp/notif/crossmodule/SecurityAuthEventListener.java:69-84`):

```json
{
  "recipientId": 42,
  "templateCode": "USER_WELCOME",
  "channelHint": ["EMAIL"],
  "moduleCode": "SEC",
  "referenceId": 42,
  "referenceType": "USER_ACCOUNT",
  "variables": { "email": "user@example.com" }
}
```

### 1.3 Response / output

Real DTO: `com.erp.notif.dto.DispatchResponse`
(`src/main/java/com/erp/notif/dto/DispatchResponse.java`):

```json
{ "logIds": [1001, 1002] }
```

`logIds` are the created `NOTIF_LOG` row ids, one per requested channel. If the recipient is
inactive, dispatch is skipped and `logIds` is an **empty list** — no error, no logs created
(`DispatchService.java:109-114`, RULE-NOTIF-007). Dispatch is synchronous/fire-and-return: by
the time the response comes back, each channel has already been attempted (with retries) and
its `NOTIF_LOG` row is in a final state (`SENT`, `FAILED`, or `CHANNEL_DISABLED`) — the caller
does not need to poll, but the response body itself doesn't carry per-channel status, only ids
(caller would need to separately read `NOTIF_LOG` to see status, e.g. via
`NotificationLogController` — **not found in code as a public cross-module read API**, only an
admin-facing controller).

Documented HTTP status is 200 (not 202 as originally planned) — see the controller javadoc,
`DispatchController.java:18-25`.

### 1.4 Authentication / authorization

- REST endpoint: standard platform JWT — `Authorization: Bearer <token>` header, parsed by
  `com.erp.security.jwt.JwtAuthenticationFilter` (`src/main/java/com/erp/security/jwt/JwtAuthenticationFilter.java:26-27`).
- Gate on the service method: `@PreAuthorize("isAuthenticated()")` — **any authenticated
  principal**, no specific permission/role required (`DispatchService.java:63-70`, RULE-NOTIF-005:
  dispatch has no page permission to attach to since it isn't a management screen).
- The in-process `dispatchSystem(...)` entry point (`DispatchService.java:87-90`) has **no**
  `@PreAuthorize` gate and is meant for principal-less internal callers (e.g. an
  `@TransactionalEventListener` running on an unauthenticated forgot-password flow) — it is
  **not exposed via any controller**, callable only from Java code in the same JVM.

### 1.5 Errors

From `com.erp.notif.exception.NotifErrorCodes` (`src/main/java/com/erp/notif/exception/NotifErrorCodes.java`)
and `DispatchService.java`, mapped to HTTP status via `Status`
(`src/main/java/com/erp/common/domain/status/Status.java`):

| Code | HTTP status | When |
|---|---|---|
| `NOTIF_TEMPLATE_NOT_FOUND` | 404 | Unknown `templateCode` (`DispatchService.java:97-99`). |
| `NOTIF_TEMPLATE_INACTIVE` | (via `assertDispatchable()`, domain-thrown) | Template deactivated — dispatch rejected (`DispatchService.java:104`). |
| — (validation) | 400, code `VALIDATION_ERROR` | Missing/blank required fields (`@NotNull`/`@NotBlank`/`@NotEmpty` on `DispatchRequest`), handled generically by `GlobalExceptionHandler.handleValidation` (`src/main/java/com/erp/common/web/GlobalExceptionHandler.java:41-52`). |
| — (auth) | 401/403 | No/invalid token, or not authenticated — `GlobalExceptionHandler.handleAccessDenied` / Spring Security default for `isAuthenticated()` failure. |
| — (unexpected) | 500, code `INTERNAL_ERROR` | Any uncaught exception (`GlobalExceptionHandler.handleUnexpected`). |

A "disabled" or unconfigured channel is **not** an error — it silently produces a `NOTIF_LOG`
row with status `CHANNEL_DISABLED` and the caller still gets a 200 with that log id
(`DispatchService.java:120-128`). Same for a genuinely failed send after retries: the response
is still 200, with the log row status `FAILED` — the caller must inspect logs to know delivery
actually happened, since the dispatch call itself does not surface send failure as an HTTP
error.

### 1.6 Minimal "how to call it" snippet

REST (curl), matching the controller path/method:

```bash
curl -X POST http://localhost:7272/api/v1/notifications/dispatch \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipientId": 42,
    "templateCode": "USER_WELCOME",
    "channelHint": ["EMAIL"],
    "moduleCode": "SEC",
    "referenceId": 42,
    "referenceType": "USER_ACCOUNT",
    "variables": { "email": "user@example.com" }
  }'
```

In-process (real caller pattern, copied from
`src/main/java/com/erp/notif/crossmodule/SecurityAuthEventListener.java:69-84` — note: this
existing caller injects `DispatchService` directly and calls `dispatchSystem(...)`, not the
`NotificationDispatchApi` bean; no current caller of `NotificationDispatchApi` was found in
the codebase, though it is the interface intended for other modules per its own javadoc):

```java
dispatchService.dispatchSystem(DispatchRequest.builder()
    .recipientId(userAccountId)
    .templateCode("ACCOUNT_ACTIVATION")
    .channelHint(List.of("EMAIL"))
    .moduleCode("SEC")
    .referenceId(userAccountId)
    .referenceType("USER_ACCOUNT")
    .variables(Map.of("email", email, "token", rawToken))
    .build());
```

---

## 2. File Service Module (FILE)

### 2.1 How it is called

REST only — no queue, no documented in-process cross-module Java API (`file` module has no
`crossmodule` package, unlike `notif`; confirmed by directory listing). Controller:
`com.erp.file.controller.FileController` (`src/main/java/com/erp/file/controller/FileController.java`),
mounted at `/api/v1/files`.

| Operation | Endpoint | Method |
|---|---|---|
| Upload | `/api/v1/files` (multipart) | `POST` |
| Issue download token | `/api/v1/files/{id}/access-token` | `POST` |
| Download | `/api/v1/files/download?token=...` | `GET` |
| Get metadata | `/api/v1/files/{id}` | `GET` |
| List by owner | `/api/v1/files?ownerId=&ownerType=&moduleCode=...` | `GET` |
| Archive / soft-delete | `/api/v1/files/{id}?action=ARCHIVE\|DELETE` | `DELETE` |

(All from `FileController.java:44-100`.)

### 2.2 Request / input

**Upload** — `multipart/form-data`: a `file` part plus form fields bound to
`com.erp.file.dto.UploadRequest` (`src/main/java/com/erp/file/dto/UploadRequest.java`):

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | multipart file part (`@RequestParam("file")`) | yes | The binary content. |
| `ownerId` | Long | yes | Polymorphic owner id. |
| `ownerType` | String (max 100) | yes | Polymorphic owner type, e.g. `"PURCHASE_ORDER"`. |
| `moduleCode` | String (max 50) | yes | Owning module code, e.g. `"PROC"`. |
| `fileCategoryFk` | Long | no | Optional category id — drives per-category size/type limits. |

Server-detected fields (`fileName`, `contentType`, `fileSize`, `fileTypeId`, `fileStatusId`)
are never client-supplied (`UploadRequest.java:13-17`).

Size limits (`src/main/java/com/erp/file/domain/FileValidationDomainService.java:17-21`):
default per-file cap **5 MB** (overridable per category), whole-request cap **10 MB** (fixed).
Content-type is validated by server-side magic-byte sniffing, not the client filename or
declared MIME, and only enforced if the chosen category has an `allowedContentTypes`
allow-list (`FileValidationDomainService.java:52-70`).

**Issue access token**: path variable `id` (file id) only, no body
(`FileController.java:52-56`).

**Download**: query param `token` (opaque string) only (`FileController.java:58-71`).

**List by owner**: query params `ownerId` (Long, required), `ownerType` (String, required),
`moduleCode` (String, required), `fileTypeId`/`fileStatusId` (optional filters), `page`
(default 0), `size` (default 20), `sort` (one of `fileName`, `createdAt`, `fileSize`; default
`createdAt` — `FileController.java:79-92`, `FileService.java:65,202`).

### 2.3 Response / output

**Upload / metadata / list / archive-delete** return
`com.erp.file.dto.FileMetadataResponse` (`src/main/java/com/erp/file/dto/FileMetadataResponse.java`) —
never the file bytes (`DRV-003`):

```json
{
  "id": 5001,
  "ownerId": 1001,
  "ownerType": "PURCHASE_ORDER",
  "moduleCode": "PROC",
  "fileName": "contract.pdf",
  "contentType": "application/pdf",
  "fileSize": 204800,
  "fileTypeId": "DOCUMENT",
  "fileStatusId": "ACTIVE",
  "fileCategoryId": 3,
  "createdAt": "2026-09-10T12:00:00.000Z",
  "createdBy": "jdoe",
  "updatedAt": null,
  "updatedBy": null
}
```

Upload returns HTTP 201 (`FileService.java:113`); archive/delete returns HTTP 200
(`FileService.java:242`, `Status.UPDATED`).

**Issue access token** returns `com.erp.file.dto.AccessTokenResponse`
(`src/main/java/com/erp/file/dto/AccessTokenResponse.java`):

```json
{ "accessToken": "q1w2e3...", "expiresAt": "2026-09-10T12:10:00.000Z" }
```

Token is a **single-use**, ~10-minute TTL, AES/GCM-encrypted opaque string, bound to the
issuing user (`FileService.java:116-141`, `FileAccessTokenDomainService`).

**Download** returns the **raw binary body** (not the `ApiResponse` envelope) with
`Content-Type` set to the stored MIME and `Content-Disposition: attachment` carrying the
original filename (`FileController.java:58-71`).

**List by owner** returns `Page<FileMetadataResponse>` — a Spring `Page` wrapper (`content`,
`totalElements`, `totalPages`, etc.) inside `ApiResponse.data`.

### 2.4 Authentication / authorization

Same JWT bearer scheme as NOTIF (`JwtAuthenticationFilter`). Beyond authentication, each
operation requires a specific permission authority
(`com.erp.security.permission.PermissionConstants`,
`src/main/java/com/erp/security/permission/PermissionConstants.java:90-96`), page code
`FILE_BROWSER`:

| Operation | Required authority |
|---|---|
| Upload | `PERM_FILE_BROWSER_CREATE` |
| Issue access token | `PERM_FILE_BROWSER_VIEW` |
| Download (by token) | none of the above — gated only by `isAuthenticated()` plus the token itself being valid and bound to the caller's username (`FileService.java:144-157`) |
| Get metadata | `PERM_FILE_BROWSER_VIEW` |
| List by owner | `PERM_FILE_BROWSER_VIEW` |
| Archive (`action=ARCHIVE`) | `PERM_FILE_BROWSER_UPDATE` |
| Soft-delete (`action=DELETE`) | `PERM_FILE_BROWSER_DELETE` |

(All `@PreAuthorize` annotations in `FileService.java:76,118,145,181,195,224-225`.)

The download token is single-use and identity-bound: a token issued to user A returns
`FILE_ACCESS_TOKEN_INVALID` (401) if replayed by user B, or if it's already been consumed
(`FileService.java:143-176`).

### 2.5 Errors

From `com.erp.file.exception.FileErrorCodes` (`src/main/java/com/erp/file/exception/FileErrorCodes.java`):

| Code | HTTP status | When |
|---|---|---|
| `FILE_DOCUMENT_SIZE_EXCEEDED` | 413 (`PAYLOAD_TOO_LARGE`) | Content or whole-request size over the limit. |
| `FILE_DOCUMENT_TYPE_NOT_ALLOWED` | 415 (`UNSUPPORTED_MEDIA_TYPE`) | Server-sniffed MIME not in the category's allow-list (or unverifiable when a restriction applies). |
| `FILE_ACCESS_TOKEN_INVALID` | 401 (`UNAUTHORIZED`) | Token invalid/tampered/expired, wrong owner, or already consumed. |
| `FILE_DOCUMENT_OWNERSHIP_REQUIRED` | 400 (`VALIDATION_ERROR`) | `ownerId`/`ownerType`/`moduleCode` missing on upload. |
| `FILE_CATEGORY_CODE_DUPLICATE` | 409 (`ALREADY_EXISTS`/`CONFLICT` family) | Category admin endpoints only, not upload. |
| `FILE_CATEGORY_INACTIVE` | 422 (`BUSINESS_RULE_VIOLATION`) | Upload references a deactivated `fileCategoryFk`. |
| `FILE_DOCUMENT_INVALID_TRANSITION` | 400 (`VALIDATION_ERROR`) | `action` other than `ARCHIVE`/`DELETE`, or illegal lifecycle transition. |
| `FILE_DOCUMENT_NOT_FOUND` / `FILE_CATEGORY_NOT_FOUND` | 404 | Unknown file/category id. |

Plus the shared generic handlers (validation, access-denied, internal error) as in the NOTIF
section above (`GlobalExceptionHandler.java`).

### 2.6 Minimal "how to call it" snippet

No existing in-code caller of `FileController`/`FileService` from another module was found
(`grep` for `FileService` usage outside `com.erp.file` returned no matches) — the snippets
below are built directly from the controller/DTO signatures, not copied from an existing
caller.

Upload:

```bash
curl -X POST http://localhost:7272/api/v1/files \
  -H "Authorization: Bearer <token>" \
  -F "file=@contract.pdf" \
  -F "ownerId=1001" \
  -F "ownerType=PURCHASE_ORDER" \
  -F "moduleCode=PROC"
```

Issue a download token, then download:

```bash
curl -X POST http://localhost:7272/api/v1/files/5001/access-token \
  -H "Authorization: Bearer <token>"
# -> { "data": { "accessToken": "...", "expiresAt": "..." } }

curl -X GET "http://localhost:7272/api/v1/files/download?token=<accessToken>" \
  -H "Authorization: Bearer <token>" \
  -o contract.pdf
```
