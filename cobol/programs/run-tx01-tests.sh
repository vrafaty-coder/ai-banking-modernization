
#!/usr/bin/env bash
set -euo pipefail

echo "================================"
echo "TX01 REGRESSION TEST SUITE"
echo "================================"

echo "Compiling programs..."

cobc -x -free -I ../copybooks \
    -o init-data.exe INIT-DATA.cbl

cobc -x -free -I ../copybooks \
    -o test-tx01-deposit.exe \
    TEST-TX01-DEPOSIT.cbl TX01.cbl

cobc -x -free -I ../copybooks \
    -o verify-tx01-persistence.exe \
    VERIFY-TX01-PERSISTENCE.cbl

echo "Resetting test data..."
./init-data.exe

echo "Running T01: Successful Deposit..."
./test-tx01-deposit.exe

echo "Verifying stored Account and Journal..."
./verify-tx01-persistence.exe


echo "Compiling regression tests..."

cobc -x -free -I ../copybooks \
    -o test-tx01-regression.exe \
    TEST-TX01-REGRESSION.cbl TX01.cbl

cobc -x -free -I ../copybooks \
    -o prepare-tx01-test-data.exe \
    PREPARE-TX01-TEST-DATA.cbl

for scenario in T02 T03 T04 T05 T06 T07
do
    echo "================================"
    echo "Running $scenario"
    ./init-data.exe
    if [[ "$scenario" == "T06" || "$scenario" == "T07" ]]; then
        ./prepare-tx01-test-data.exe "$scenario"
    fi
    ./test-tx01-regression.exe "$scenario"
done

echo "================================"
echo "TX01 REGRESSION: T01-T07 ALL PASS"
echo "================================"
