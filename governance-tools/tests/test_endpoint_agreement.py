"""
Two ways a plan could disagree with the surface that was actually published and
still be reported clean.

Both shipped in SEC v1 and both were found by a human reading the table, not by a
check:

  · `forward-refs` resolved its DTO columns with `value in source` — a SUBSTRING
    test. `RoleAssignmentRequest` "resolved" against an api-docs defining only
    `UserRoleAssignmentRequest`: a different type, one the implementer cannot
    import. Four of twenty-seven rows were wrong and the column reported clean.
  · nothing compared the VERB and PATH beside those columns with the published
    ones at all, so five rows read `GET /users` with a `UserSearchRequest` body
    against a surface publishing `POST /users/search` — self-contradictory on
    their face, invisible to every clause.

Nothing here spells a module code, ID prefix or path: the ids come from
factory.yaml's own grammar via the fixtures.
"""
from __future__ import annotations

import analyze as an


# ── the substring enabler ───────────────────────────────────────────────────

def test_identifier_must_match_on_a_token_boundary():
    """A name that is merely a SUFFIX of a defined one does not resolve."""
    source = "Schema: `UserRoleAssignmentRequest` (application/json)"
    assert an._names_in("UserRoleAssignmentRequest", source)
    assert not an._names_in("RoleAssignmentRequest", source), \
        "a suffix of a defined type is a different type — the implementer cannot import it"


def test_identifier_must_match_on_a_left_boundary_too():
    """A name that is merely a PREFIX of a defined one does not resolve either."""
    source = "Shape: `UserResponseEnvelope`"
    assert not an._names_in("UserResponse", source)


def test_prose_cells_keep_substring_semantics():
    """A cell that is not identifier-shaped has no token to anchor, so it stays
    a substring test — a false negative there would be worse than the false
    positive it prevents."""
    source = "Shape: `paginated list of UserResponse (see Pagination Envelope in index.md)`"
    assert an._names_in("paginated list of UserResponse", source)


def test_empty_cell_resolves():
    """An empty cell states nothing, so it disagrees with nothing."""
    assert an._names_in("", "anything")


# ── the unguarded verb and path ─────────────────────────────────────────────

DOCS = """
## POST /api/v1/sec/users/search

**Search users**

## POST /api/v1/sec/users

**Create user**

## DELETE /api/v1/sec/users/{id}

**Deactivate user**
"""


def test_published_endpoints_are_read_from_the_docs_own_headings():
    assert an._published_endpoints(DOCS) == {
        ("POST", "/api/v1/sec/users/search"),
        ("POST", "/api/v1/sec/users"),
        ("DELETE", "/api/v1/sec/users/{id}"),
    }


def test_a_verb_the_surface_does_not_serve_is_a_finding(endpoint_ctx):
    ctx = endpoint_ctx("| API-SEC-005 | search users | GET | /api/v1/sec/users |", DOCS)
    out = an._c_endpoint_agrees(ctx, {"artifact": "plan", "source": "docs", "kind": "API"}, "MAJOR")
    assert len(out) == 1
    assert "GET /api/v1/sec/users" in out[0].message
    assert "POST /api/v1/sec/users" in out[0].message, "the finding names what IS served"


def test_a_bodyless_verb_carrying_a_request_type_says_so(endpoint_ctx):
    ctx = endpoint_ctx("| API-SEC-005 | /users | GET | UserSearchRequest | Page |", DOCS)
    out = an._c_endpoint_agrees(ctx, {"artifact": "plan", "source": "docs", "kind": "API"}, "MAJOR")
    assert len(out) == 1
    assert "self-contradictory" in out[0].message


def test_a_relative_path_matches_its_absolute_publication(endpoint_ctx):
    """A plan writes paths relative to the module base; the api-docs write them
    absolute. Suffix matching is what lets both be right."""
    ctx = endpoint_ctx("| API-SEC-006 | /users | POST | UserCreateRequest | UserResponse |", DOCS)
    assert an._c_endpoint_agrees(ctx, {"artifact": "plan", "source": "docs", "kind": "API"}, "MAJOR") == []


def test_an_agreeing_row_is_silent(endpoint_ctx):
    ctx = endpoint_ctx("| API-SEC-005 | search users | POST | /api/v1/sec/users/search |", DOCS)
    assert an._c_endpoint_agrees(ctx, {"artifact": "plan", "source": "docs", "kind": "API"}, "MAJOR") == []


def test_another_modules_endpoint_is_not_judged_here(endpoint_ctx):
    """A cited endpoint of ANOTHER module is that module's to publish; these
    api-docs are this module's, and `xref-surface` resolves the foreign one."""
    ctx = endpoint_ctx("| API-MDL-011 | lookups | GET | /api/v1/mdl/lookups |", DOCS)
    assert an._c_endpoint_agrees(ctx, {"artifact": "plan", "source": "docs", "kind": "API"}, "MAJOR") == []


def test_no_published_surface_yet_is_forward_refs_business(endpoint_ctx):
    """Before the api-docs exist this check says nothing — stating a verb for an
    unbuilt endpoint is exactly what `forward-refs` already owns."""
    ctx = endpoint_ctx("| API-SEC-005 | search users | GET | /api/v1/sec/users |", None)
    assert an._c_endpoint_agrees(ctx, {"artifact": "plan", "source": "docs", "kind": "API"}, "MAJOR") == []


def test_a_line_citing_several_ids_states_no_single_endpoint(endpoint_ctx):
    ctx = endpoint_ctx("see API-SEC-005 and API-SEC-006 — GET /api/v1/sec/users", DOCS)
    assert an._c_endpoint_agrees(ctx, {"artifact": "plan", "source": "docs", "kind": "API"}, "MAJOR") == []
