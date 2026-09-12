<!-- source: PHASE:F2 / SUB:F2-SCR-FIN-012 -->
<!-- context: F2-HEADER.md — phase-level preamble -->
<!-- traces: AC-FIN-043, AC-FIN-045, API-FIN-032, REQ-FIN-043, REQ-FIN-045, SCR-FIN-012, UXD-FIN-002 -->
<!-- SUB:F2-SCR-FIN-012:START traces=REQ-FIN-043,AC-FIN-043,API-FIN-032,UXD-FIN-002,SCR-FIN-012,REQ-FIN-045,AC-FIN-045 -->
### F2 · SCR-FIN-012 — تقارير الأبعاد / Dimension reports

### F2-QUERY — API-FIN-032            traces=API-FIN-032,REQ-FIN-043
GET `/api/v1/fin/reports/dimension` · query params `dimensionId` (**required**),
`dimensionValueId` (optional), `periodId` (optional) · response `DimensionReportResponse`
with its `rows[]` · kind **read query**
Cache key    : `[reports, dimension, filters]` — all three params
Enabled      : only once a dimension is chosen — the required parameter gates the call, and
               the screen shows its choose-a-dimension state until then
Errors       : `FIN-404-DIMENSION` (404) → user message (the required keying id) ·
               `FIN-404-PERIOD` (404) → user message when a supplied period does not resolve ·
               validation (400) → inline · `FIN-403-FORBIDDEN` (403) → forbidden message
Loading      : LOCAL
Cache policy : defaults, inside the `[reports, *]` family every posting mutation invalidates
Invalidation : n/a (a read)
### F2-LOOKUP — DEBIT_CREDIT
Key `DEBIT_CREDIT` (UXD-FIN-002) — the shared hook, for the row's nature. The dimension and
dimension-value selects are NOT lookups: they read FIN's own API-FIN-005 and API-FIN-008
through the SCR-FIN-002 keys, and the row's dimension-value names come from the report itself.
### F2-SCREEN-INIT — SCR-FIN-012
Permission read : `FIN_DIMENSION_REPORTS` present in the caller's effective menu → VIEW
                  (ADR-FIN-005). No other action exists on this screen.
Lookups used    : DEBIT_CREDIT (row nature)
Entity by id    : none
Dimension select: served by the SCR-FIN-002 dimension and dimension-value searches through
                  their shared keys; no call is duplicated here
### F2-FACADE — SCR-FIN-012
Composes     : API-FIN-032 · the dimension and dimension-value searches for its selects · the
               DEBIT_CREDIT hook
State it owns: the filter object (dimension, dimension value, period) mirrored from the
               route's search params, and a derived loading flag. No aggregation is performed
               here — the account × dimension-value rows arrive as they are
Operations   : none — this screen writes nothing

<!-- SUB:F2-SCR-FIN-012:END -->
