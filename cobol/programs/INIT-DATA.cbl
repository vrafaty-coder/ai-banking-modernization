
       >>SOURCE FORMAT FREE
identification division.
program-id. INIT-DATA.

environment division.
input-output section.
file-control.
    select ACCOUNT-FILE assign to "../../data/accounts.dat"
        organization is indexed
        access mode is dynamic
        record key is ACC-NUMBER
        file status is WS-ACC-STATUS.

    select JOURNAL-FILE assign to "../../data/journal.dat"
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
01 WS-ERROR-FLAG pic 9 value 0.

procedure division.
main.
    open output ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        display "ERROR OPEN ACCOUNT: " WS-ACC-STATUS
        move 1 to return-code
        goback
    end-if

    open output JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        display "ERROR OPEN JOURNAL: " WS-JRN-STATUS
        close ACCOUNT-FILE
        move 1 to return-code
        goback
    end-if

    move "0100000000001" to ACC-NUMBER
    move "A" to ACC-STATUS
    move "IRR" to ACC-CURRENCY
    move 1000000 to ACC-BALANCE
    perform WRITE-ACCOUNT

    move "0100000000002" to ACC-NUMBER
    move "A" to ACC-STATUS
    move "IRR" to ACC-CURRENCY
    move 2500000 to ACC-BALANCE
    perform WRITE-ACCOUNT

    move "0200000000001" to ACC-NUMBER
    move "B" to ACC-STATUS
    move "IRR" to ACC-CURRENCY
    move 500000 to ACC-BALANCE
    perform WRITE-ACCOUNT

    move "0300000000001" to ACC-NUMBER
    move "C" to ACC-STATUS
    move "IRR" to ACC-CURRENCY
    move 750000 to ACC-BALANCE
    perform WRITE-ACCOUNT

    close ACCOUNT-FILE JOURNAL-FILE

    if WS-ERROR-FLAG = 0
        display "INITIAL DATA CREATED SUCCESSFULLY"
        display "Accounts: 4"
        display "Journal: empty"
    else
        display "INITIALIZATION FAILED"
        move 1 to return-code
    end-if
    goback.

WRITE-ACCOUNT.
    if WS-ERROR-FLAG = 0
        write ACCOUNT-RECORD
        if WS-ACC-STATUS not = "00"
            display "ERROR WRITING ACCOUNT: "
                    WS-ACC-STATUS
            move 1 to WS-ERROR-FLAG
        end-if
    end-if.
