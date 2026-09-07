# /audit — optional governance audit of a module version → FIX-PROMPTS

```
/audit backend  [MODULE] --version N      (engines/optional/P4.1)
/audit frontend [MODULE] --version N      (engines/optional/P4.2)
```
Audits the ANALYSIS artifacts (not code) and writes paste-ready fix-prompts
grouped by owning engine (§1D.7) into `modules/[MOD][/vN]/P4-Audit/`. Run via
delegate `--lane review-holistic --read-only` (it is a review — it never edits).
Apply fixes through the owning engine + merge lane, then re-run the affected
per-engine gate. Never a gate for the core path.
