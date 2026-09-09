# ADR-DEMO-001 — Maximum content length for the Note entity

Status  : ACCEPTED (non-breaking)
Module  : DEMO   Version : v1
Traces  : ENT-DEMO-001, REQ-DEMO-001, REQ-DEMO-004, RULE-DEMO-002

## Context
No input (PRD, business policies, domain-profile, knowledge base) states a
maximum length for a note's free-text `content` field. `[KB:erp-domain-standards §6]`
gives defaults for money, dates, paging and search, but not for free-text
field length. A database-level text column still needs a stated bound to be
verifiable (SRS quality attribute: every RULE with a message; every field
constraint testable) and to become a concrete `CHECK` constraint at P2.

## Decision
Set the maximum length of `content` to 4000 characters, enforced by
`RULE-DEMO-002`. This follows the pattern of the archived `DEMO v1` pipeline
run, which added the same kind of DB-level content-length `CHECK` constraint
for its equivalent `DEMO_NOTE` table, and is a generous bound for a personal
note ("just CRUD") that still keeps storage and payload sizes bounded.

## Consequences
- `RULE-DEMO-002` (SRS, P1) states the constraint and its bilingual message.
- P2 (Database) implements it as a DB-level `CHECK` constraint on the
  `content` column, mirroring the precedent above.
- Non-breaking: raising or lowering this bound later is a new version's
  MODIFIED rule, not a contradiction of any approved story or policy.
