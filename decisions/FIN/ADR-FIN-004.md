# ADR-FIN-004 — Header debit=credit balance enforced by a deferred constraint trigger
Status      : ACCEPTED
Stage       : P2        Module: FIN        Version: v1
Context     : RULE-FIN-002 (srs-fin.md A5) requires that a journal entry's debit lines sum to the same total as its credit lines. A postgresql16 `CHECK` constraint cannot aggregate sibling rows across a table (it evaluates one row at a time), so the SRS-level rule has no direct DDL equivalent.
Decision    : Enforce RULE-FIN-002 with a `CONSTRAINT TRIGGER ... DEFERRABLE INITIALLY DEFERRED` on `fin_journal_entry_line` (function `fin_fn_check_entry_balance`) that sums debit/credit amounts for the parent entry and raises when they disagree, but only once the parent's `status_code` is `POSTED` — so a multi-line DRAFT build (added line by line) is never falsely rejected mid-transaction.
Consequences: The backend must insert/update all lines of an entry within one transaction before the header transitions to POSTED, so the deferred trigger fires once at COMMIT with the full line set present; P3.1's execution plan must sequence the "build lines, then post" API calls inside a single transaction boundary.
traces      : ENT-FIN-006, ENT-FIN-007, RULE-FIN-002, REQ-FIN-018, REQ-FIN-019
