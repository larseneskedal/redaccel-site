#!/bin/sh
# Runs the site checks (ruff static check + pytest) on a directory, default the repo.
# The pre-push hook calls this on the exact commit being pushed; GitHub Actions runs the
# same pytest command. Usage: tools/ci/check.sh [dir-with-tests]
set -eu
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET="${1:-$REPO}"
VENV="$REPO/.venv"

if [ ! -x "$VENV/bin/python" ]; then
  for p in python3.13 python3.12 python3.11 python3; do
    if command -v "$p" >/dev/null 2>&1; then "$p" -m venv "$VENV"; break; fi
  done
fi
# Reinstall when the requirements change, so a new dependency is tested before it ships.
want="$(cat "$REPO/requirements.txt" "$REPO/requirements-dev.txt" | shasum | cut -c1-40)"
have="$(cat "$VENV/.req-hash" 2>/dev/null || true)"
if [ "$want" != "$have" ]; then
  "$VENV/bin/python" -m pip install -q --disable-pip-version-check -r "$REPO/requirements-dev.txt"
  echo "$want" > "$VENV/.req-hash"
fi
cd "$TARGET"
exec "$VENV/bin/python" -m pytest -q -p no:cacheprovider tests
