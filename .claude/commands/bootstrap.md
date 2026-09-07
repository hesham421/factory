# /bootstrap — create the platform registry ONCE (engine P-1)

Run once per platform, before the first module. `engines/P-1` (Master Registry
Builder) produces `platform/project-registry.md` + `platform-standards.md` (+
indexes) from `domain/domain-profile.md` (build it first via
`engines/domain-profile` if absent). Delegate lane: `analysis`. Commit:
`"P-1: platform bootstrap"`. After this, per-module registry maintenance is
INLINE in every engine (§1D.4 step 2) — never re-run P-1 per module.
