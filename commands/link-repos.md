# /link-repos — connect backend / frontend consumer repos to the factory

Linking is a CONFIG edit, not a code change (governance-tools/config.py REPOS):
```
REPOS["backend"]["url"]      = "git@github.com:<org>/backend.git"
REPOS["backend"]["checkout"] = <local clone path>          # or env GOV_BACKEND_CHECKOUT
REPOS["frontend"]…                                           # same
```
Agreed paths the repos must honour (already in config):
- backend publishes  `governance/api-docs/api-docs-<mod>.md`       (after implementing a version)
- frontend publishes `governance/ui-shell/ui-shell-manifest-<mod>.md` (after implementing UI/UX)
- the factory delivers to `governance/modules/<MOD>[/vN]/` on branch `gov/<mod>-vN-<track>`
Verify with `python3 governance-tools/gov.py status -m <MOD>` and a dry
`fetch-inputs`. Until `url` is set, delivery commits locally and does not push.
