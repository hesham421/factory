<!-- source: PHASE:F3 / SUB:F3-SCR-SEC-010 -->
<!-- context: F3-HEADER.md — phase-level preamble -->
<!-- traces: AC-SEC-021, AC-SEC-032, AC-SEC-033, API-SEC-027, REQ-SEC-021, REQ-SEC-032, REQ-SEC-033, SCR-SEC-010 -->
<!-- SUB:F3-SCR-SEC-010:START traces=REQ-SEC-021,REQ-SEC-032,REQ-SEC-033,AC-SEC-021,AC-SEC-032,AC-SEC-033,API-SEC-027,SCR-SEC-010 -->
### F3 · SCR-SEC-010 — القائمة الديناميكية ثنائية المستوى / Dynamic two-tier menu

This component has **no form and no input** (SRS B3: "read-only, derived"), so it
declares no validation timing and carries no field block.
No `RULE-*` is enforced here, and none could be: the menu asserts nothing — it renders what the
caller's effective grants already are (REQ-SEC-021) and omits what they are not (REQ-SEC-032).
The one rule that matters at this boundary, REQ-SEC-033, is explicitly **not** a client-side
validation: the server verifies the module grant on every request regardless of what the menu
shows, and this component's absence of an entry is a usability consequence, never the
enforcement (ADR-SEC-005).
Nothing is composed locally: no static route table is merged into the response, no entry is
sorted into existence, and no module the response omitted is added back from a cached earlier
menu. A menu that fails to load renders no entry rather than a remembered one.
Locale       : session → browser → `ar`; `nameAr` / `nameEn` are rendered by the active locale
               at both tiers.
Permission-driven behaviour: the whole component **is** the permission-driven behaviour of this
module's frontend — it is the single source every route guard reads (F4, RF5).

<!-- SUB:F3-SCR-SEC-010:END -->
