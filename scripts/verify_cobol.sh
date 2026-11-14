#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v cobc >/dev/null 2>&1; then
  echo 'ERROR: GnuCOBOL (cobc) is required. No tests were executed.' >&2
  exit 127
fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/cobol"
mkdir -p "$TMP/data"
cp -R "$ROOT/cobol/programs" "$ROOT/cobol/copybooks" "$TMP/cobol/"
cd "$TMP/cobol/programs"
# The suites intentionally reset account and journal test data; only disposable copies are used.
bash run-tx01-tests.sh
bash run-tx02-tests.sh
printf '\nCOBOL regression scripts completed successfully in an isolated temporary directory.\n'
