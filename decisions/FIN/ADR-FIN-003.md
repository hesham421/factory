# ADR-FIN-003 — Year-end close requires every period of the year Hard Closed first
Status      : ACCEPTED
Stage       : P1        Module: FIN        Version: v1
Context     : plan §7.4 states balance-sheet balances carry forward and result accounts close to Retained Earnings "at year-end close," but does not state the precondition for triggering it — specifically, whether open or soft-closed periods within the year may coexist with a year-end close.
Decision    : Require every fiscal period belonging to the year to be Hard Closed before year-end close is permitted (RULE-FIN-010), following standard accounting practice that a year cannot be finalized while any of its periods remains open to posting. §2 resolution order step 6 (domain best practice) applies since no policy, story, registry fact or steering rule settles the exact gating condition.
Consequences: SCR-REQ-FIN-008's "year-end-close" action is disabled/rejected until all periods of the target year show Hard Close; REQ-FIN-030/031 assume this precondition already holds when they run.
traces      : ENT-FIN-010, ENT-FIN-011, REQ-FIN-030, RULE-FIN-010
