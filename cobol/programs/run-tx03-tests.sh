#!/usr/bin/env bash
set -euo pipefail

echo '================================'
echo 'TX03 REGRESSION TEST SUITE'
echo '================================'

cobc -x -free -I ../copybooks -o init-data.exe INIT-DATA.cbl
cobc -x -free -I ../copybooks -o prepare-tx03-test-data.exe PREPARE-TX03-TEST-DATA.cbl
cobc -x -free -I ../copybooks -o test-tx03-regression.exe TEST-TX03-REGRESSION.cbl TX03.cbl

for scenario in T01 T02 T03 T04 T05 T06 T07 T08 T09 T10 T11; do
    echo '================================'
    echo "Running $scenario"
    ./init-data.exe
    case "$scenario" in
        T09|T10|T11) ./prepare-tx03-test-data.exe "$scenario" ;;
    esac
    ./test-tx03-regression.exe "$scenario"
done

echo '================================'
echo 'TX03 REGRESSION: T01-T11 ALL PASS'
echo '================================'
