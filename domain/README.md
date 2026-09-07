# domain/
`domain-profile.md` — ONE profile for the whole platform, built once by
`engines/domain-profile` (recommended: not per module). Each module gets a
short inherit section (`## Module: <MOD>`) appended when it enters pass 1.
Maintained by commit, like every artifact. Run `/analyze-pass1` on a module
with no profile present and the factory builds it first.
