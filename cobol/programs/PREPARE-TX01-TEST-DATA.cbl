
       >>SOURCE FORMAT FREE
identification division.
program-id. PREPARE-TX01-TEST-DATA.

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
01 WS-SCENARIO   pic x(3).
01 WS-ACC-STATUS pic xx.
01 WS-JRN-STATUS pic xx.

procedure division.

MAIN.
    accept WS-SCENARIO from command-line

    evaluate WS-SCENARIO
        when "T06"
            perform PREPARE-OVERFLOW
        when "T07"
            perform PREPARE-DUPLICATE-STAMP
        when other
            display "Unsupported scenario"
            move 1 to return-code
    end-evaluate

    goback.

PREPARE-OVERFLOW.
    open i-o ACCOUNT-FILE

    if WS-ACC-STATUS not = "00"
        display "FAIL: Account open"
        move 1 to return-code
        exit paragraph
    end-if

    move "0100000000001" to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER

    if WS-ACC-STATUS not = "00"
        display "FAIL: Account read"
        move 1 to return-code
        close ACCOUNT-FILE
        exit paragraph
    end-if

    move 999999999990000 to ACC-BALANCE
    rewrite ACCOUNT-RECORD

    if WS-ACC-STATUS not = "00"
        display "FAIL: Account rewrite"
        move 1 to return-code
    else
        display "T06 DATA PREPARED"
    end-if

    close ACCOUNT-FILE.

PREPARE-DUPLICATE-STAMP.
    open i-o JOURNAL-FILE

    if WS-JRN-STATUS not = "00"
        display "FAIL: Journal open"
        move 1 to return-code
        exit paragraph
    end-if

    initialize JOURNAL-RECORD
    move "20261107121500T0010001" to JRN-STAMP
    move "TX01" to JRN-TRAN-CODE
    move "0100000000002" to JRN-CR-ACCOUNT
    move 1000 to JRN-AMOUNT

    write JOURNAL-RECORD

    if WS-JRN-STATUS not = "00"
        display "FAIL: Journal write"
        move 1 to return-code
    else
        display "T07 DATA PREPARED"
    end-if

    close JOURNAL-FILE.
