# /micro-feature — extension on a built module: same flow, new version

```
/micro-feature [MODULE] "<free text — the whole feature, any language>"
```
One free-text input. The command splits it internally into a backend part and
a frontend part (either may be empty), then runs the SAME factory flow as a
new version — nothing lighter, nothing outside governance:

1. `gov.py version -m MOD --new` → vN (v[N-1] frozen + tagged). CS-ID = CS-MOD-SEQ.
2. `/analyze-pass1 MOD --version N` (delegate `--lane analysis`) in DELTA mode: engines read v[N-1] as
   baseline and emit only NEW/MODIFIED elements with a Change Manifest; IDs
   continue sequences; dependencies (XM/UXD/ALIGN) preserved; a breaking
   change STOPS. Review gates as usual. Split + deliver backend.
3. When the repos publish the updated api-docs / ui-shell →
   `/analyze-pass2 MOD --version N` (frontend delta) → gates → split → deliver
   frontend → tag `[mod]-vN`.
4. If a part is empty, that track is simply skipped (backend-only or frontend-
   only extension).

Never a shortcut around a gate: an extension is a full, reviewed, versioned
analysis — just scoped to the delta.
