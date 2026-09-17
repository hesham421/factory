#!/usr/bin/env bash
# claude_delegate.sh — the GOV_RUNNER=cmd adapter between gov.py and the
# claude-delegate relay (delegate-skills/skills/claude-delegate/scripts/relay.mjs).
#
#   claude_delegate.sh {brief} {lane} {model} {read_only_flag} {out}
#
# gov.py fills the placeholders per round (dispatch.run_round). {read_only_flag}
# is "--read-only" for a read-only lane and EMPTY otherwise — and an empty
# word vanishes from a shell command line, so the positional arguments shift.
# The adapter therefore reads {out} as the LAST argument and detects
# --read-only anywhere, rather than trusting positions 4 and 5.
#
# What it does: runs the relay with a temporary --out-dir, and on success
# copies the implementer's final response text (final.txt) to {out} — the
# file dispatch.run_round expects. Any failure (relay usage error, claude
# unavailable, timeout, error result, no final text) exits non-zero and
# leaves {out} absent, so the orchestrator never reads a half response.
#
# {model} is mandatory: a dialogue lane alternates implementers, and a
# lane-name-only mapping would collapse the debate to one model. Explicit
# relay flags win over the lane's dials (relay.mjs --help), so --model here
# beats the model the delegate-setup lane names, while effort, timeout and
# read-only still come from the lane of the same name.
#
# Locating the relay: $GOV_DELEGATE_RELAY when set; else the first of
#   <factory>/delegate-skills/skills/claude-delegate/scripts/relay.mjs
#   <any parent of the factory>/.agents/skills/claude-delegate/scripts/relay.mjs
#   ~/.agents/skills/claude-delegate/scripts/relay.mjs
set -euo pipefail

usage() { echo "usage: $0 {brief} {lane} {model} [--read-only] {out}" >&2; exit 2; }

[ "$#" -ge 4 ] || usage
brief="$1"; lane="$2"; model="$3"
out="${!#}"                                   # the last argument, whatever position it landed in
read_only=""
for a in "$@"; do [ "$a" = "--read-only" ] && read_only="--read-only"; done
[ -f "$brief" ] || { echo "claude_delegate: brief not found: $brief" >&2; exit 2; }
[ -n "$lane" ] && [ -n "$model" ] || usage
case "$out" in --read-only|"$brief"|"$lane"|"$model") usage ;; esac

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
factory="$(cd "$here/../.." && pwd)"

find_relay() {
  if [ -n "${GOV_DELEGATE_RELAY:-}" ]; then echo "$GOV_DELEGATE_RELAY"; return; fi
  local rel="skills/claude-delegate/scripts/relay.mjs"
  if [ -f "$factory/delegate-skills/$rel" ]; then echo "$factory/delegate-skills/$rel"; return; fi
  local d="$factory"
  while :; do
    if [ -f "$d/.agents/$rel" ]; then echo "$d/.agents/$rel"; return; fi
    [ "$d" = "/" ] && break
    d="$(dirname "$d")"
  done
  if [ -f "$HOME/.agents/$rel" ]; then echo "$HOME/.agents/$rel"; return; fi
  return 1
}

relay="$(find_relay)" || { echo "claude_delegate: relay.mjs not found — set GOV_DELEGATE_RELAY or install the claude-delegate skill" >&2; exit 127; }
command -v node >/dev/null 2>&1 || { echo "claude_delegate: node is not on PATH" >&2; exit 127; }

tmp="$(mktemp -d "${TMPDIR:-/tmp}/gov-delegate.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

# The relay's exit code mirrors claude's; a non-zero code, a missing result.json
# or a status other than "completed" is a failed round.
set +e
node "$relay" --brief "$brief" --lane "$lane" --model "$model" --cd "$factory" --out-dir "$tmp" $read_only
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  echo "claude_delegate: relay exited $rc for lane '$lane' (model $model)" >&2
  [ -f "$tmp/stderr.txt" ] && tail -n 20 "$tmp/stderr.txt" >&2
  exit "$rc"
fi
[ -f "$tmp/result.json" ] || { echo "claude_delegate: relay wrote no result.json" >&2; exit 1; }
status="$(sed -n 's/.*"status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$tmp/result.json" | head -n 1)"
[ "$status" = "completed" ] || { echo "claude_delegate: relay status '$status' (not completed)" >&2; exit 1; }
if grep -q '"readOnlyViolation"[[:space:]]*:[[:space:]]*true' "$tmp/result.json"; then
  echo "claude_delegate: read-only lane '$lane' changed the working tree — refusing the response" >&2
  exit 1
fi
[ -s "$tmp/final.txt" ] || { echo "claude_delegate: relay returned no final response text" >&2; exit 1; }

mkdir -p "$(dirname "$out")"
cp "$tmp/final.txt" "$out"
echo "claude_delegate: lane '$lane' model $model → $(wc -c < "$out" | tr -d ' ') bytes → $out"
