       >>SOURCE FORMAT FREE
identification division.
program-id. TEST-TX02-REGRESSION.
environment division.
input-output section.
file-control.
    select ACCOUNT-FILE
        assign to "../../data/accounts.dat"
        organization is indexed
        access mode is dynamic
        record key is ACC-NUMBER
        file status is WS-ACC-STATUS.
    select JOURNAL-FILE
        assign to "../../data/journal.dat"
        organization is indexed
        access mode is dynamic
        record key is JRN-STAMP
        file status is WS-JRN-STATUS.
data division.
file section.
fd ACCOUNT-FILE.
copy "ACCOUNT-RECORD.cpy".
fd JOURNAL-FILE.
copy "JOURNAL-RECORD.cpy".
working-storage section.
01 WS-ACC-STATUS       pic xx.
01 WS-JRN-STATUS       pic xx.
01 WS-JOURNAL-COUNT    binary-long value 0.
01 WS-TEST-FAILED      pic 9 value 0.
01 WS-SCENARIO         pic x(3).
01 WS-EXPECTED-ALERT   pic 9(4).
01 WS-EXPECTED-BAL     pic 9(15).
01 WS-EXPECTED-ACCOUNT pic x(13).
01 WS-CHECK-ACCOUNT    pic x(13).
01 WS-CHECK-BALANCE    pic 9(15).
01 WS-EXPECTED-STAMP   pic x(22).
01 WS-RECEIVE.
    copy "COMMON-RECEIVE.cpy".
    copy "TX02-RECEIVE.cpy".
01 WS-RESPONSE.
    copy "COMMON-RESPONSE.cpy".
    copy "TX02-RESPONSE.cpy".
procedure division.
MAIN.
    initialize WS-RECEIVE WS-RESPONSE
    accept WS-SCENARIO from command-line
    move "0100000000001" to RCV-ACCOUNT-NUMBER
    move 1500000 to RCV-AMOUNT
    move 1000000 to WS-EXPECTED-BAL
    move "0100000000001" to WS-EXPECTED-ACCOUNT
    move 0 to WS-TEST-FAILED WS-JOURNAL-COUNT
    evaluate WS-SCENARIO
        when "T02"
            move 1007 to WS-EXPECTED-ALERT
        when "T03"
            move "9999999999999" to RCV-ACCOUNT-NUMBER
            move 1001 to WS-EXPECTED-ALERT
        when "T04"
            move "0200000000001" to RCV-ACCOUNT-NUMBER
            move "0200000000001" to WS-EXPECTED-ACCOUNT
            move 500000 to WS-EXPECTED-BAL
            move 1002 to WS-EXPECTED-ALERT
        when "T05"
            move "0300000000001" to RCV-ACCOUNT-NUMBER
            move "0300000000001" to WS-EXPECTED-ACCOUNT
            move 750000 to WS-EXPECTED-BAL
            move 1003 to WS-EXPECTED-ALERT
        when "T06"
            move 0 to RCV-AMOUNT
            move 1004 to WS-EXPECTED-ALERT
        when "T07"
            move 50000 to RCV-AMOUNT
            move 0 to WS-EXPECTED-ALERT
            move 950000 to WS-EXPECTED-BAL
        when other
            display "Unsupported scenario: " WS-SCENARIO
            move 1 to return-code
            goback
    end-evaluate
    move "TX02" to RCV-TRAN-CODE
    move 20261107 to RCV-TRAN-DATE
    move 121500 to RCV-TRAN-TIME
    move "T001" to RCV-TRAN-TELLER-TERMINAL
    move 1 to RCV-TRAN-SEQUENCE
    call "TX02" using WS-RECEIVE WS-RESPONSE
    display "SCENARIO: " WS-SCENARIO
    display "Status  : " RSP-STATUS-CODE
    display "Alert   : " RSP-ALERT-CODE
    display "Message : " RSP-ALERT-MESSAGE
    display "Balance : " RSP-ACCOUNT-BALANCE
    display "Stamp   : [" RSP-JOURNAL-STAMP "]"
    if RSP-TRAN-CODE not = "TX02"
        move 1 to WS-TEST-FAILED
    end-if
    if WS-SCENARIO = "T07"
        move "20261107121500T0010002"
            to WS-EXPECTED-STAMP
        if RSP-STATUS-CODE not = 0
            or RSP-ALERT-CODE not = 0
            or RSP-ALERT-MESSAGE not = spaces
            or RSP-ACCOUNT-BALANCE not = 950000
            or RSP-JOURNAL-STAMP not = WS-EXPECTED-STAMP
            move 1 to WS-TEST-FAILED
        end-if
    else
        if RSP-STATUS-CODE not = 1
            or RSP-ALERT-CODE not = WS-EXPECTED-ALERT
            or RSP-ACCOUNT-BALANCE not = 0
            or RSP-JOURNAL-STAMP not = spaces
            move 1 to WS-TEST-FAILED
        end-if
    end-if
    move WS-EXPECTED-ACCOUNT to WS-CHECK-ACCOUNT
    move WS-EXPECTED-BAL to WS-CHECK-BALANCE
    perform CHECK-ACCOUNT
    if WS-SCENARIO = "T03" or "T04" or "T05"
        move "0100000000001" to WS-CHECK-ACCOUNT
        move 1000000 to WS-CHECK-BALANCE
        perform CHECK-ACCOUNT
    end-if
    if WS-SCENARIO = "T07"
        move "0100000000002" to WS-CHECK-ACCOUNT
        move 2500000 to WS-CHECK-BALANCE
        perform CHECK-ACCOUNT
    end-if
    perform CHECK-JOURNAL
    if WS-TEST-FAILED = 0
        display WS-SCENARIO " RESULT: PASS"
        move 0 to return-code
    else
        display WS-SCENARIO " RESULT: FAIL"
        move 1 to return-code
    end-if
    goback.
CHECK-ACCOUNT.
    open input ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        move 1 to WS-TEST-FAILED
        exit paragraph
    end-if
    move WS-CHECK-ACCOUNT to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER
    if WS-ACC-STATUS not = "00"
        or ACC-BALANCE not = WS-CHECK-BALANCE
        move 1 to WS-TEST-FAILED
    end-if
    close ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        move 1 to WS-TEST-FAILED
    end-if.
CHECK-JOURNAL.
    move 0 to WS-JOURNAL-COUNT
    open input JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        move 1 to WS-TEST-FAILED
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
                        if WS-SCENARIO = "T07"
                            perform CHECK-T07-JOURNAL-ROW
                        end-if
                    when "10"
                        continue
                    when other
                        move 1 to WS-TEST-FAILED
                end-evaluate
            end-perform
        when "23"
            continue
        when other
            move 1 to WS-TEST-FAILED
    end-evaluate
    close JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        move 1 to WS-TEST-FAILED
    end-if
    if WS-SCENARIO = "T07"
        if WS-JOURNAL-COUNT not = 2
            move 1 to WS-TEST-FAILED
        end-if
    else
        if WS-JOURNAL-COUNT not = 0
            move 1 to WS-TEST-FAILED
        end-if
    end-if.
CHECK-T07-JOURNAL-ROW.
    evaluate JRN-STAMP
        when "20261107121500T0010001"
            if JRN-TRAN-CODE not = "TX01"
                or JRN-CR-ACCOUNT not = "0100000000002"
                or JRN-DB-ACCOUNT not = spaces
                or JRN-AMOUNT not = 1000
                move 1 to WS-TEST-FAILED
            end-if
        when "20261107121500T0010002"
            if JRN-TRAN-CODE not = "TX02"
                or JRN-CR-ACCOUNT not = spaces
                or JRN-DB-ACCOUNT not = "0100000000001"
                or JRN-AMOUNT not = 50000
                move 1 to WS-TEST-FAILED
            end-if
        when other
            move 1 to WS-TEST-FAILED
    end-evaluate.
