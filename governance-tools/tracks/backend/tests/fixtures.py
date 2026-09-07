"""
Fixture builders for the governance-tools test suite.

These produce SMALL but structurally faithful backend-execution-plan.md and
backend-test-plan.md bodies — enough to exercise the parser, the semantic
validator, and Agent 3's splitter without needing a real 8000-line module
artifact. Marker syntax matches PROJECT-3-REGISTRY.md Section 5.7 exactly.
"""


def valid_execution_plan() -> str:
    """A minimal but well-formed backend-execution-plan.md.

    - CORE: whole-phase (never splits)
    - SVC-API: above threshold → two phase-qualified SUBs (AMEND-P3-N),
      each holding one API atomic
    - INT-C: two phase-qualified SUBs to a shared target module name, proving
      the qualification keeps SUB:INT-C-FINANCE distinct from any INT-R twin
    - trailing, un-marked "Agent Handoff Summary" section (must be captured,
      not dropped — C4)
    """
    return (
        "<!-- PHASE:CORE:START -->\n"
        "## PHASE CORE — Architectural Policies\n"
        "Package structure declared.\n"
        "<!-- PHASE:CORE:END -->\n"
        "\n"
        "<!-- PHASE:SVC-API:START -->\n"
        "## PHASE SVC-API — Services & APIs\n"
        "Phase-level strategy table.\n"
        "  <!-- SUB:SVC-API-CRUD:START -->\n"
        "  ### CRUD group\n"
        "    <!-- API:API-ORG-001:START -->\n"
        "    POST /orgs — create\n"
        "    <!-- API:API-ORG-001:END -->\n"
        "  <!-- SUB:SVC-API-CRUD:END -->\n"
        "  <!-- SUB:SVC-API-SEARCH:START -->\n"
        "  ### SEARCH group\n"
        "    <!-- API:API-ORG-002:START -->\n"
        "    GET /orgs — search\n"
        "    <!-- API:API-ORG-002:END -->\n"
        "  <!-- SUB:SVC-API-SEARCH:END -->\n"
        "<!-- PHASE:SVC-API:END -->\n"
        "\n"
        "<!-- PHASE:INT-C:START -->\n"
        "## PHASE INT-C — Integration Consume\n"
        "  <!-- SUB:INT-C-FINANCE:START -->\n"
        "    <!-- XM:XM-ORG-001:START -->\n"
        "    Consume from Finance.\n"
        "    <!-- XM:XM-ORG-001:END -->\n"
        "  <!-- SUB:INT-C-FINANCE:END -->\n"
        "<!-- PHASE:INT-C:END -->\n"
        "\n"
        "<!-- PHASE:ALIGN-BE:START -->\n"
        "## PHASE ALIGN-BE — Self-consistency gate\n"
        "All good.\n"
        "<!-- PHASE:ALIGN-BE:END -->\n"
        "\n"
        "## Agent Handoff Summary\n"
        "This trailing section has no PHASE marker and must still be packaged.\n"
    )


def valid_test_plan() -> str:
    """A minimal well-formed backend-test-plan.md above the TC>12 threshold,
    split into the two exempt (un-prefixed) SUB labels."""
    rule_tcs = "".join(
        f"    <!-- TC:TC-BE-ORG-{i:03d}:START -->\n"
        f"    Given/When/Then {i}\n"
        f"    <!-- TC:TC-BE-ORG-{i:03d}:END -->\n"
        for i in range(1, 8)
    )
    api_tcs = "".join(
        f"    <!-- TC:TC-BE-ORG-{i:03d}:START -->\n"
        f"    Given/When/Then {i}\n"
        f"    <!-- TC:TC-BE-ORG-{i:03d}:END -->\n"
        for i in range(8, 15)
    )
    return (
        "<!-- PHASE:TEST-PLAN-BE:START -->\n"
        "## Backend Test Plan\n"
        "  <!-- SUB:RULE-SCENARIOS:START -->\n"
        f"{rule_tcs}"
        "  <!-- SUB:RULE-SCENARIOS:END -->\n"
        "  <!-- SUB:API-SCENARIOS:START -->\n"
        f"{api_tcs}"
        "  <!-- SUB:API-SCENARIOS:END -->\n"
        "<!-- PHASE:TEST-PLAN-BE:END -->\n"
    )


def valid_test_plan_below_threshold() -> str:
    """Below the TC>12 threshold → all TCs sit directly under the PHASE, no SUB
    (a valid no-SUB phase — must NOT trip the orphan-atomic check)."""
    tcs = "".join(
        f"  <!-- TC:TC-BE-ORG-{i:03d}:START -->\n"
        f"  Given/When/Then {i}\n"
        f"  <!-- TC:TC-BE-ORG-{i:03d}:END -->\n"
        for i in range(1, 4)
    )
    return (
        "<!-- PHASE:TEST-PLAN-BE:START -->\n"
        "## Backend Test Plan (small)\n"
        f"{tcs}"
        "<!-- PHASE:TEST-PLAN-BE:END -->\n"
    )


def svc_api_over_threshold_no_sub() -> str:
    """SVC-API with 8 API blocks and NO SUB — at the split threshold (≥8) but
    unsplit. Should raise a threshold advisory (non-blocking), or block under
    strict. No orphan issue: with no SUBs, atomics under PHASE are valid."""
    apis = "".join(
        f"  <!-- API:API-ORG-{i:03d}:START -->\n  POST /x{i}\n  <!-- API:API-ORG-{i:03d}:END -->\n"
        for i in range(1, 9)  # 8 APIs
    )
    return (
        "<!-- PHASE:SVC-API:START -->\n"
        "## PHASE SVC-API\n"
        f"{apis}"
        "<!-- PHASE:SVC-API:END -->\n"
    )


def core_with_sub() -> str:
    """CORE carries a SUB — but CORE never splits. Should raise an advisory."""
    return (
        "<!-- PHASE:CORE:START -->\n"
        "  <!-- SUB:CORE-A:START -->\n  x\n  <!-- SUB:CORE-A:END -->\n"
        "<!-- PHASE:CORE:END -->\n"
    )

