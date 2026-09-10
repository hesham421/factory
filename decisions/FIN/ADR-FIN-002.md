# ADR-FIN-002 — Mapping-set account derivation embedded in Rule Line, not a separate entity
Status      : ACCEPTED
Stage       : P1        Module: FIN        Version: v1
Context     : plan §3.2(a) describes a "mapping set: a combination of event attributes → a segment value via lookup" as one of three account-derivation methods on a rule line, but does not name it as a standalone concept. `modules/FIN/P0/module-registry-fin.md` (ARCH-4, reuse-before-create) already fixed the module's entity list at 13 entities — "سطر القاعدة / Rule Line" is registered, but no separate "mapping entry" entity is.
Decision    : Model the mapping set as a repeating `mappingEntries` field group embedded within `ENT-FIN-005` (Rule Line) — (eventAttributeName, eventAttributeValue, resultingDimensionValue) per entry — rather than introducing a fourteenth top-level entity that was not registered at P0.
Consequences: P2 may still normalize `mappingEntries` into its own physical table (a config detail table keyed by the rule line), but it remains logically part of ENT-FIN-005, not a new ENT id; P3.1/P3.2 present it as a nested repeating group on the Rule Line's own screen (SCR-REQ-FIN-004), not a separate screen.
traces      : ENT-FIN-005, REQ-FIN-010
