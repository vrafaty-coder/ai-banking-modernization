#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/classes" "$TMP/run"
# Compile the canonical runnable sources, not historical generation snapshots.
mapfile -d '' SOURCES < <(find "$ROOT/java/src/main/java" "$ROOT/java/src/test/java" -name '*.java' -print0)
javac -d "$TMP/classes" "${SOURCES[@]}"
(
 cd "$TMP/run"
 java -cp "$TMP/classes" banking.tx01.Tx01ValidationGateV3 > "$TMP/tx01.txt"
 java -cp "$TMP/classes" banking.tx02.Tx02ValidationGateV2 > "$TMP/tx02.txt"
)
for dim in RESPONSE ACCOUNT JOURNAL BUSINESS_RULE; do
 grep -q "$dim: PASS=15 FAIL=0 NOT_EVALUABLE=1" "$TMP/tx01.txt"
done
grep -q 'Scenarios=16' "$TMP/tx01.txt"
PYTHON_BIN="${PYTHON:-python}"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "Python not found" >&2; exit 127; }
"$PYTHON_BIN" - "$TMP/tx02.txt" <<'PYCHECK'
import sys,re
s=open(sys.argv[1],encoding='utf-8').read()
rows=re.findall(r'^S\d{2}\s*\|\s*(RESPONSE|ACCOUNT|JOURNAL|BUSINESS_RULE)\s*\|\s*(PASS|FAIL)\s*\|',s,re.M)
assert len(rows)==64, f'TX02 expected 64 checks, got {len(rows)}'
assert all(status=='PASS' for _,status in rows), 'TX02 contains FAIL records'
assert len(set(re.findall(r'^S\d{2}',s,re.M)))==16, 'TX02 scenario count differs'
print('TX02: 16 scenarios x 4 dimensions = 64 PASS')
PYCHECK
printf 'TX01: 60 PASS, 0 FAIL, 4 NOT_EVALUABLE\n'
printf 'Both Java gates verified.\n'
