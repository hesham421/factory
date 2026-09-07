# /micro-feature — one free-text launcher; splits the work backend↔frontend itself

ONE prompt, ONE free-text input in any language ("add roles bulk-deactivate with
a confirm dialog in SEC", "أضف حقل ملاحظات لجدول الفروع وشاشة تعديله في org").
This prompt UNDERSTANDS which parts of the request are backend and which are
frontend, splits them itself, and drives BOTH governed fast-paths in order —
each archiving in its own established structure (GOVERNANCE-CONFIG §1G). The
person never has to say "backend" or "frontend"; the split is internal.

## Input
```
/micro-feature  <free text — the whole feature, any phrasing/language>
```

## STEP A — Understand & SPLIT the request (internal, automatic)
From the one free-text request, derive the MODULE, then decompose the feature
into a BACKEND part and a FRONTEND part — do not ask the person to separate them:
- **Backend part** = anything touching data/logic: endpoint/API, table/column,
  validation rule, service, calculation, permission check. → this becomes the
  input to `/micro-feature-backend`.
- **Frontend part** = anything touching the UI: screen/page, button, a field on
  a screen, form, layout, route, component, confirm dialog. → input to
  `/micro-feature-frontend`.
- A part may be EMPTY (a pure API change has no frontend part; a pure styling
  change has no backend part) — then only that track runs.
- MODULE: infer from the text; ask ONLY if it is missing/ambiguous. Nothing
  else is asked.

Write the split explicitly so it is auditable:
```
MODULE   : [MOD]                     new version: v[N]
BACKEND  : "[backend one-liner]"     | (none)
FRONTEND : "[frontend one-liner]"    | (none)
```

## STEP B — Confirm in ONE line, then go
```
MFF [MOD] v[N] — backend: "[…|none]" · frontend: "[…|none]"  — Run? (yes / edit)
```
Proceed on "yes" (or an explicit "go/just do it" already in the request).
"edit" → adjust either one-liner, re-confirm.

## STEP C — Drive BOTH governed commands, in order, each in its own structure
The two are RELATED but archived with a clean separation — same tools, each on
its own track's set:

1. If BACKEND part is non-empty → run `/micro-feature-backend [MOD] "[backend one-liner]"`.
   It archives the FULL backend analysis set (srs / db-script / backend-
   execution-plan + registries) with the clear phase separation inside
   `backend-execution-plan-[mod].md`, agent3 splits it, uploads to governed
   Drive folders (§1E) + ledger, implements. Backend goes FIRST — its new API
   is the frontend's input.

2. If FRONTEND part is non-empty → then run `/micro-feature-frontend [MOD] "[frontend one-liner]"`.
   It archives chiefly `frontend-execution-plan-[mod].md` (+ its registry; flow/
   ui-ux deltas only if a screen changed), agent3 splits it, uploads + ledger,
   implements. It consumes the backend's new API via the §1F api-docs reference.

Both runs use the SAME new version v[N] and the SAME CS-ID (one change set), and
the frontend run writes END for the version (or backend END if frontend part is
empty). Each command does its own §1G steps (local-first baseline read, Claude
Code generates the delta honoring dependencies, agent1/2/3, governed upload).
Relay each command's prompts/output; don't pre-answer beyond the single Run?.

## STEP D — Report
MODULE + v[N] + CS-ID; the backend/frontend split that was applied; for each
track that ran: Change Manifest (NEW/MODIFIED IDs), governed Drive paths the
analysis landed in, ledger START…END, what was implemented in code.

## Constraints
- ONE free-text input; the backend/frontend split is INTERNAL — never make the
  person pre-classify.
- ROUTER only — hand the two parts to `/micro-feature-backend` /
  `/micro-feature-frontend`; never do analysis/split/archive yourself.
- Backend BEFORE frontend whenever both parts are non-empty.
- Each track archives in ITS OWN structure (backend = full set with phase
  separation; frontend = execution plan) — never mix a track's files into the
  other's folders.
- NEVER guess the MODULE; ask if it can't be inferred.
- No prior built version for the module → full project route (§1G scope), not MFF.
