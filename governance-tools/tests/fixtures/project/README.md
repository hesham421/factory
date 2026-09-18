# the tests' own project repo

A fixture: every test builds a temporary copy of this directory (git-initialised) and points
`GOV_PROJECT_CHECKOUT` at it, so no test depends on a committed project. The profile is an
ERP-shaped sample under a made-up identity; the tool itself carries no project.
