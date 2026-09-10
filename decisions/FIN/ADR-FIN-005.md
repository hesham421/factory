# ADR-FIN-005 — Posted-entry immutability enforced at the database layer
Status      : ACCEPTED
Stage       : P2        Module: FIN        Version: v1
Context     : RULE-FIN-006 (srs-fin.md A5) requires that a POSTED journal entry can never be edited or deleted. The SRS states this as a business rule enforced "at post"; it does not specify whether the guarantee must hold at the database layer or only through the application/API.
Decision    : Add a `BEFORE UPDATE OR DELETE` trigger (`fin_fn_block_posted_entry_edit`) on `fin_journal_entry` that raises whenever `OLD.status_code = 'POSTED'`, so the guarantee holds even against a direct database write, not only through the governed API — consistent with plan §5.3/§6.1's framing of this as an integrity guarantee ("prevents any suspicion of tampering"), which is weaker if only application-enforced.
Consequences: Reversal (REQ-FIN-023) must always be modeled as a new row, never an update to the original; any future migration or data-fix script touching a POSTED entry must go through an explicit, audited exception path outside normal DML, since this trigger has no bypass flag.
traces      : ENT-FIN-006, RULE-FIN-006, REQ-FIN-018, REQ-FIN-023
