
       >>SOURCE FORMAT FREE
identification division.
program-id. TEST-TX01-REGRESSION.

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
01 TX01-RECEIVE.
   copy "COMMON-RECEIVE.cpy".
   copy "TX01-RECEIVE.cpy".

01 TX01-RESPONSE.
   copy "COMMON-RESPONSE.cpy".
   copy "TX01-RESPONSE.cpy".

01 WS-SCENARIO       pic x(3).
01 WS-EXPECTED-ALERT pic 9(4).
01 WS-EXPECTED-BAL   pic 9(15).
01 WS-ACC-STATUS     pic xx.
01 WS-JRN-STATUS     pic xx.
01 WS-FAILED         pic 9 value 0.
01 WS-JRN-COUNT      binary-long value 0.
01 WS-END            pic 9 value 0.

procedure division.

MAIN.
    accept WS-SCENARIO from command-line

    initialize TX01-RECEIVE TX01-RESPONSE

    move "TX01" to RCV-TRAN-CODE
    move 20261107 to RCV-TRAN-DATE
    move 121500 to RCV-TRAN-TIME
    move "T001" to RCV-TRAN-TELLER-TERMINAL
    move 1 to RCV-TRAN-SEQUENCE
    move "0100000000001" to RCV-ACCOUNT-NUMBER
    move 50000 to RCV-AMOUNT

    move 1000000 to WS-EXPECTED-BAL
    move 0 to WS-EXPECTED-ALERT

    evaluate WS-SCENARIO
        when "T02"
            move "9999999999999" to RCV-ACCOUNT-NUMBER
            move 1001 to WS-EXPECTED-ALERT
        when "T03"
            move "0200000000001" to RCV-ACCOUNT-NUMBER
            move 1002 to WS-EXPECTED-ALERT
            move 500000 to WS-EXPECTED-BAL
        when "T04"
            move "0300000000001" to RCV-ACCOUNT-NUMBER
            move 1003 to WS-EXPECTED-ALERT
            move 750000 to WS-EXPECTED-BAL
        when "T05"
            move 0 to RCV-AMOUNT
            move 1004 to WS-EXPECTED-ALERT
        when "T06"
            move 1005 to WS-EXPECTED-ALERT
            move 999999999990000 to WS-EXPECTED-BAL
        when "T07"
            move 0 to WS-EXPECTED-ALERT
        when other
            display "Unsupported scenario: "
                WS-SCENARIO
            move 1 to return-code
            goback
    end-evaluate

    call "TX01" using
        TX01-RECEIVE TX01-RESPONSE
    end-call

    if WS-SCENARIO = "T07"
        perform VERIFY-T07-RESPONSE
        perform VERIFY-T07-PERSISTENCE
        if WS-FAILED = 0
            display "T07 RESULT: PASS"
            move 0 to return-code
        else
            display "T07 RESULT: FAIL"
            move 1 to return-code
        end-if
        goback
    end-if

    display "SCENARIO: " WS-SCENARIO
    display "Status  : " RSP-STATUS-CODE
    display "Alert   : " RSP-ALERT-CODE
    display "Message : " RSP-ALERT-MESSAGE
    display "Balance : " RSP-ACCOUNT-BALANCE
    display "Stamp   : [" RSP-JOURNAL-STAMP "]"

    if RSP-TRAN-CODE not = "TX01"
       or RSP-STATUS-CODE not = 1
       or RSP-ALERT-CODE not = WS-EXPECTED-ALERT
       or RSP-ACCOUNT-BALANCE not = 0
       or RSP-JOURNAL-STAMP not = spaces
        display "FAIL: Incorrect response"
        move 1 to WS-FAILED
    end-if

    perform VERIFY-ACCOUNT
    perform VERIFY-JOURNAL

    if WS-FAILED = 0
        display WS-SCENARIO " RESULT: PASS"
        move 0 to return-code
    else
        display WS-SCENARIO " RESULT: FAIL"
        move 1 to return-code
    end-if

    goback.

VERIFY-ACCOUNT.
    if WS-SCENARIO = "T02"
        exit paragraph
    end-if

    open input ACCOUNT-FILE

    if WS-ACC-STATUS not = "00"
        display "FAIL: Account file open"
        move 1 to WS-FAILED
        exit paragraph
    end-if

    move RCV-ACCOUNT-NUMBER to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER

    if WS-ACC-STATUS not = "00"
        display "FAIL: Account read"
        move 1 to WS-FAILED
    else
        if ACC-BALANCE not = WS-EXPECTED-BAL
            display "FAIL: Account balance changed"
            move 1 to WS-FAILED
        end-if
    end-if

    close ACCOUNT-FILE.

VERIFY-JOURNAL.
    open input JOURNAL-FILE

    if WS-JRN-STATUS not = "00"
        display "FAIL: Journal file open"
        move 1 to WS-FAILED
        exit paragraph
    end-if

    move 0 to WS-JRN-COUNT WS-END
    move low-values to JRN-STAMP

    start JOURNAL-FILE
        key is greater than JRN-STAMP
    end-start

    evaluate WS-JRN-STATUS
        when "00"
            continue
        when "23"
            move 1 to WS-END
        when other
            display "FAIL: Journal START"
            move 1 to WS-FAILED WS-END
    end-evaluate

    perform until WS-END = 1
        read JOURNAL-FILE next record
            at end
                move 1 to WS-END
            not at end
                add 1 to WS-JRN-COUNT
        end-read

        if WS-JRN-STATUS not = "00"
           and WS-JRN-STATUS not = "10"
            display "FAIL: Journal read"
            move 1 to WS-FAILED WS-END
        end-if
    end-perform

    close JOURNAL-FILE

    if WS-JRN-COUNT not = 0
        display "FAIL: Unexpected journal records"
        move 1 to WS-FAILED
    end-if.

VERIFY-T07-RESPONSE.
    if RSP-TRAN-CODE not = "TX01"
       or RSP-STATUS-CODE not = 0
       or RSP-ALERT-CODE not = 0
       or RSP-ALERT-MESSAGE not = spaces
       or RSP-ACCOUNT-BALANCE not = 1050000
       or RSP-JOURNAL-STAMP not =
           "20261107121500T0010002"
        display "FAIL: T07 response"
        move 1 to WS-FAILED
    end-if.

VERIFY-T07-PERSISTENCE.
    open input ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        display "FAIL: T07 account open"
        move 1 to WS-FAILED
    else
        move "0100000000001" to ACC-NUMBER
        read ACCOUNT-FILE key is ACC-NUMBER
        if WS-ACC-STATUS not = "00"
           or ACC-BALANCE not = 1050000
            display "FAIL: T07 account balance"
            move 1 to WS-FAILED
        end-if
        close ACCOUNT-FILE
    end-if

    open input JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        display "FAIL: T07 journal open"
        move 1 to WS-FAILED
        exit paragraph
    end-if

    move "20261107121500T0010001" to JRN-STAMP
    read JOURNAL-FILE key is JRN-STAMP
    if WS-JRN-STATUS not = "00"
        display "FAIL: T07 original journal missing"
        move 1 to WS-FAILED
    else
        if JRN-TRAN-CODE not = "TX01"
           or JRN-CR-ACCOUNT not = "0100000000002"
           or JRN-DB-ACCOUNT not = spaces
           or JRN-AMOUNT not = 1000
            display "FAIL: T07 original journal changed"
            move 1 to WS-FAILED
        end-if
    end-if

    move "20261107121500T0010002" to JRN-STAMP
    read JOURNAL-FILE key is JRN-STAMP
    if WS-JRN-STATUS not = "00"
        display "FAIL: T07 new journal missing"
        move 1 to WS-FAILED
    else
        if JRN-TRAN-CODE not = "TX01"
           or JRN-CR-ACCOUNT not = "0100000000001"
           or JRN-DB-ACCOUNT not = spaces
           or JRN-AMOUNT not = 50000
            display "FAIL: T07 new journal incorrect"
            move 1 to WS-FAILED
        end-if
    end-if

    move 0 to WS-JRN-COUNT WS-END
    move low-values to JRN-STAMP
    start JOURNAL-FILE key is greater than JRN-STAMP
    evaluate WS-JRN-STATUS
        when "00"
            continue
        when "23"
            move 1 to WS-END
        when other
            display "FAIL: T07 journal START"
            move 1 to WS-FAILED WS-END
    end-evaluate

    perform until WS-END = 1
        read JOURNAL-FILE next record
            at end
                move 1 to WS-END
            not at end
                add 1 to WS-JRN-COUNT
        end-read
        if WS-JRN-STATUS not = "00"
           and WS-JRN-STATUS not = "10"
            display "FAIL: T07 journal iteration"
            move 1 to WS-FAILED WS-END
        end-if
    end-perform
    close JOURNAL-FILE

    if WS-JRN-COUNT not = 2
        display "FAIL: T07 journal count"
        move 1 to WS-FAILED
    end-if.
