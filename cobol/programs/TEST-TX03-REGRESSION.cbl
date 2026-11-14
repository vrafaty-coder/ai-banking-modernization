       >>SOURCE FORMAT FREE
identification division.
program-id. TEST-TX03-REGRESSION.
environment division.
input-output section.
file-control.
    select ACCOUNT-FILE assign to "../../data/accounts.dat"
        organization is indexed access mode is dynamic
        record key is ACC-NUMBER file status is WS-ACC-STATUS.
    select JOURNAL-FILE assign to "../../data/journal.dat"
        organization is indexed access mode is dynamic
        record key is JRN-STAMP file status is WS-JRN-STATUS.
data division.
file section.
fd ACCOUNT-FILE.
copy "ACCOUNT-RECORD.cpy".
fd JOURNAL-FILE.
copy "JOURNAL-RECORD.cpy".
working-storage section.
01 WS-SCENARIO pic x(3).
01 WS-FAILED pic 9 value 0.
01 WS-EXPECTED-ALERT pic 9(4).
01 WS-EXPECTED-STATUS pic 9(2).
01 WS-EXPECTED-DB pic 9(15).
01 WS-EXPECTED-CR pic 9(15).
01 WS-EXPECTED-STAMP pic x(22).
01 WS-ACC-STATUS pic xx.
01 WS-JRN-STATUS pic xx.
01 WS-CHECK-NUMBER pic x(13).
01 WS-CHECK-BALANCE pic 9(15).
01 WS-CHECK-CURRENCY pic x(3).
01 WS-ACCOUNT-COUNT binary-long.
01 WS-JOURNAL-COUNT binary-long.
01 WS-SEEN-FIRST pic 9.
01 WS-SEEN-SECOND pic 9.
01 WS-RECEIVE.
    copy "COMMON-RECEIVE.cpy".
    copy "TX03-RECEIVE.cpy".
01 WS-RESPONSE.
    copy "COMMON-RESPONSE.cpy".
    copy "TX03-RESPONSE.cpy".
procedure division.
MAIN.
    move 0 to return-code WS-FAILED
    initialize WS-RECEIVE WS-RESPONSE
    accept WS-SCENARIO from command-line
    move "TX03" to RCV-TRAN-CODE
    move 20261107 to RCV-TRAN-DATE
    move 121500 to RCV-TRAN-TIME
    move "T001" to RCV-TRAN-TELLER-TERMINAL
    move 1 to RCV-TRAN-SEQUENCE
    move "0100000000001" to RCV-DB-ACCOUNT
    move "0100000000002" to RCV-CR-ACCOUNT
    move 50000 to RCV-AMOUNT
    move 1 to WS-EXPECTED-STATUS
    move 0 to WS-EXPECTED-DB WS-EXPECTED-CR
    move spaces to WS-EXPECTED-STAMP
    evaluate WS-SCENARIO
        when "T01" when "T11"
            move 0 to WS-EXPECTED-STATUS WS-EXPECTED-ALERT
            move 950000 to WS-EXPECTED-DB
            move 2550000 to WS-EXPECTED-CR
            if WS-SCENARIO = "T01"
                move "20261107121500T0010001"
                    to WS-EXPECTED-STAMP
            else
                move "20261107121500T0010002"
                    to WS-EXPECTED-STAMP
            end-if
        when "T02"
            move 1500000 to RCV-AMOUNT
            move 1007 to WS-EXPECTED-ALERT
        when "T03"
            move "9999999999999" to RCV-DB-ACCOUNT
            move 1001 to WS-EXPECTED-ALERT
        when "T04"
            move "9999999999999" to RCV-CR-ACCOUNT
            move 1001 to WS-EXPECTED-ALERT
        when "T05"
            move "0200000000001" to RCV-DB-ACCOUNT
            move 1002 to WS-EXPECTED-ALERT
        when "T06"
            move "0300000000001" to RCV-CR-ACCOUNT
            move 1003 to WS-EXPECTED-ALERT
        when "T07"
            move 0 to RCV-AMOUNT
            move 1004 to WS-EXPECTED-ALERT
        when "T08"
            move "0100000000001" to RCV-CR-ACCOUNT
            move 1008 to WS-EXPECTED-ALERT
        when "T09"
            move 1009 to WS-EXPECTED-ALERT
        when "T10"
            move 1005 to WS-EXPECTED-ALERT
        when other
            display "Unsupported scenario: " WS-SCENARIO
            move 1 to return-code
            goback
    end-evaluate
    call "TX03" using WS-RECEIVE WS-RESPONSE
    display "SCENARIO: " WS-SCENARIO
    display "Status  : " RSP-STATUS-CODE
    display "Alert   : " RSP-ALERT-CODE
    display "Message : [" RSP-ALERT-MESSAGE "]"
    display "DB Bal  : " RSP-DB-ACCOUNT-BALANCE
    display "CR Bal  : " RSP-CR-ACCOUNT-BALANCE
    display "Stamp   : [" RSP-JOURNAL-STAMP "]"
    if RSP-TRAN-CODE not = "TX03"
        or RSP-STATUS-CODE not = WS-EXPECTED-STATUS
        or RSP-ALERT-CODE not = WS-EXPECTED-ALERT
        or RSP-DB-ACCOUNT-BALANCE not = WS-EXPECTED-DB
        or RSP-CR-ACCOUNT-BALANCE not = WS-EXPECTED-CR
        or RSP-JOURNAL-STAMP not = WS-EXPECTED-STAMP
        move 1 to WS-FAILED
        display "RESPONSE CHECK: FAIL"
    end-if
    if WS-EXPECTED-STATUS = 0
        if RSP-ALERT-MESSAGE not = spaces
            move 1 to WS-FAILED
        end-if
    end-if
    perform CHECK-ACCOUNTS
    perform CHECK-JOURNAL
    if WS-FAILED = 0
        display WS-SCENARIO " RESULT: PASS"
        move 0 to return-code
    else
        display WS-SCENARIO " RESULT: FAIL"
        move 1 to return-code
    end-if
    goback.
CHECK-ACCOUNTS.
    open input ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        display "ACCOUNT OPEN: FAIL"
        move 1 to WS-FAILED
        exit paragraph
    end-if
    move "0100000000001" to WS-CHECK-NUMBER
    move 1000000 to WS-CHECK-BALANCE
    if WS-EXPECTED-STATUS = 0
        move 950000 to WS-CHECK-BALANCE
    end-if
    move "IRR" to WS-CHECK-CURRENCY
    perform CHECK-ONE-ACCOUNT
    move "0100000000002" to WS-CHECK-NUMBER
    move 2500000 to WS-CHECK-BALANCE
    if WS-EXPECTED-STATUS = 0
        move 2550000 to WS-CHECK-BALANCE
    end-if
    if WS-SCENARIO = "T10"
        move 999999999990000 to WS-CHECK-BALANCE
    end-if
    move "IRR" to WS-CHECK-CURRENCY
    if WS-SCENARIO = "T09"
        move "USD" to WS-CHECK-CURRENCY
    end-if
    perform CHECK-ONE-ACCOUNT
    move "0200000000001" to WS-CHECK-NUMBER
    move 500000 to WS-CHECK-BALANCE
    move "IRR" to WS-CHECK-CURRENCY
    perform CHECK-ONE-ACCOUNT
    move "0300000000001" to WS-CHECK-NUMBER
    move 750000 to WS-CHECK-BALANCE
    move "IRR" to WS-CHECK-CURRENCY
    perform CHECK-ONE-ACCOUNT
    move 0 to WS-ACCOUNT-COUNT
    move low-values to ACC-NUMBER
    start ACCOUNT-FILE key is greater than ACC-NUMBER
    evaluate WS-ACC-STATUS
        when "00"
            perform until WS-ACC-STATUS not = "00"
                read ACCOUNT-FILE next record
                evaluate WS-ACC-STATUS
                    when "00" add 1 to WS-ACCOUNT-COUNT
                    when "10" continue
                    when other move 1 to WS-FAILED
                end-evaluate
            end-perform
        when other
            move 1 to WS-FAILED
    end-evaluate
    if WS-ACCOUNT-COUNT not = 4
        move 1 to WS-FAILED
    end-if
    close ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        move 1 to WS-FAILED
    end-if.
CHECK-ONE-ACCOUNT.
    move WS-CHECK-NUMBER to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER
    if WS-ACC-STATUS not = "00"
        display "ACCOUNT READ FAILED: " WS-CHECK-NUMBER
        move 1 to WS-FAILED
    else
        if ACC-BALANCE not = WS-CHECK-BALANCE
            or ACC-CURRENCY not = WS-CHECK-CURRENCY
            display "ACCOUNT MISMATCH: " WS-CHECK-NUMBER
            move 1 to WS-FAILED
        end-if
    end-if.
CHECK-JOURNAL.
    move 0 to WS-JOURNAL-COUNT WS-SEEN-FIRST WS-SEEN-SECOND
    open input JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        display "JOURNAL OPEN: FAIL"
        move 1 to WS-FAILED
        exit paragraph
    end-if
    move low-values to JRN-STAMP
    start JOURNAL-FILE key is greater than JRN-STAMP
    evaluate WS-JRN-STATUS
        when "00"
            perform until WS-JRN-STATUS not = "00"
                read JOURNAL-FILE next record
                evaluate WS-JRN-STATUS
                    when "00"
                        add 1 to WS-JOURNAL-COUNT
                        perform CHECK-JOURNAL-ROW
                    when "10" continue
                    when other move 1 to WS-FAILED
                end-evaluate
            end-perform
        when "23" continue
        when other move 1 to WS-FAILED
    end-evaluate
    evaluate WS-SCENARIO
        when "T01"
            if WS-JOURNAL-COUNT not = 1
                or WS-SEEN-FIRST not = 1
                move 1 to WS-FAILED
            end-if
        when "T11"
            if WS-JOURNAL-COUNT not = 2
                or WS-SEEN-FIRST not = 1
                or WS-SEEN-SECOND not = 1
                move 1 to WS-FAILED
            end-if
        when other
            if WS-JOURNAL-COUNT not = 0
                move 1 to WS-FAILED
            end-if
    end-evaluate
    close JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        move 1 to WS-FAILED
    end-if.
CHECK-JOURNAL-ROW.
    if JRN-TRAN-CODE not = "TX03"
        or JRN-DB-ACCOUNT not = "0100000000001"
        or JRN-CR-ACCOUNT not = "0100000000002"
        move 1 to WS-FAILED
    end-if
    evaluate JRN-STAMP
        when "20261107121500T0010001"
            if WS-SCENARIO = "T11"
                if JRN-AMOUNT not = 1000
                    move 1 to WS-FAILED
                end-if
            else
                if JRN-AMOUNT not = 50000
                    move 1 to WS-FAILED
                end-if
            end-if
            move 1 to WS-SEEN-FIRST
        when "20261107121500T0010002"
            if WS-SCENARIO not = "T11"
                or JRN-AMOUNT not = 50000
                move 1 to WS-FAILED
            end-if
            move 1 to WS-SEEN-SECOND
        when other
            move 1 to WS-FAILED
    end-evaluate.
