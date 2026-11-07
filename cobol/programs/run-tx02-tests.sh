#!/usr/bin/env bash
set -euo pipefail

echo '================================'
echo 'TX02 REGRESSION TEST SUITE'
echo '================================'

cobc -x -free -I ../copybooks -o init-data.exe INIT-DATA.cbl
cobc -x -free -I ../copybooks -o prepare-tx01-test-data.exe PREPARE-TX01-TEST-DATA.cbl
cobc -x -free -I ../copybooks -o test-tx02-withdrawal.exe TEST-TX02-WITHDRAWAL.cbl TX02.cbl
cobc -x -free -I ../copybooks -o test-tx02-regression.exe TEST-TX02-REGRESSION.cbl TX02.cbl

echo 'Running T01: Successful Withdrawal'
./init-data.exe
./test-tx02-withdrawal.exe

# T01 persistence: check with the existing reader programs separately.
for scenario in T02 T03 T04 T05 T06 T07; do
    echo '================================'
    echo "Running $scenario"
    ./init-data.exe
    if [[ "$scenario" == 'T07' ]]; then
        ./prepare-tx01-test-data.exe T07
    fi
    ./test-tx02-regression.exe "$scenario"
done

echo '================================'
echo 'TX02 REGRESSION: T01-T07 ALL PASS'
echo '================================'
