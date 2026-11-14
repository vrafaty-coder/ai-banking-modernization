
       >>SOURCE FORMAT FREE
identification division.
program-id. VERIFY-TX01-PERSISTENCE.

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
01 WS-ACC-STATUS pic xx.
01 WS-JRN-STATUS pic xx.
01 WS-COUNT      binary-long value 0.
01 WS-FAILED     pic 9 value 0.
01 WS-END        pic 9 value 0.

procedure division.

MAIN.
    display "TX01 PERSISTENCE VERIFICATION"
    display "-----------------------------"

    open input ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        display "FAIL: Cannot open Account File"
        move 1 to return-code
        goback
    end-if

    move "0100000000001" to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER

    if WS-ACC-STATUS not = "00"
       or ACC-BALANCE not = 1050000
        display "FAIL: Incorrect stored balance"
        move 1 to WS-FAILED
    else
        display "Stored Balance: " ACC-BALANCE
        display "Account Check : PASS"
    end-if

    close ACCOUNT-FILE

    open input JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        display "FAIL: Cannot open Journal File"
        move 1 to return-code
        goback
    end-if

    move "20261107121500T0010001" to JRN-STAMP
    read JOURNAL-FILE key is JRN-STAMP

    if WS-JRN-STATUS not = "00"
        display "FAIL: Journal record not found"
        move 1 to WS-FAILED
    else
        if JRN-TRAN-CODE not = "TX01"
           or JRN-CR-ACCOUNT not = "0100000000001"
           or JRN-DB-ACCOUNT not = spaces
           or JRN-AMOUNT not = 50000
            display "FAIL: Incorrect Journal data"
            move 1 to WS-FAILED
        else
            display "Journal Check : PASS"
        end-if
    end-if

    move 0 to WS-COUNT WS-END

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
            display "FAIL: Journal START error: "
                WS-JRN-STATUS
            move 1 to WS-FAILED WS-END
    end-evaluate

    perform until WS-END = 1
        read JOURNAL-FILE next record
            at end
                move 1 to WS-END
            not at end
                add 1 to WS-COUNT
        end-read

        if WS-JRN-STATUS not = "00"
           and WS-JRN-STATUS not = "10"
            display "FAIL: Journal read error"
            move 1 to WS-FAILED WS-END
        end-if
    end-perform

    close JOURNAL-FILE

    display "Journal Records: " WS-COUNT

    if WS-COUNT not = 1
        display "FAIL: Incorrect Journal count"
        move 1 to WS-FAILED
    end-if

    display "-----------------------------"

    if WS-FAILED = 0
        display "PERSISTENCE TEST: PASS"
        move 0 to return-code
    else
        display "PERSISTENCE TEST: FAIL"
        move 1 to return-code
    end-if

    goback.
