
       >>SOURCE FORMAT FREE
identification division.
program-id. READ-ACCOUNTS.

environment division.
input-output section.
file-control.
    select ACCOUNT-FILE
        assign to "../../data/accounts.dat"
        organization is indexed
        access mode is dynamic
        record key is ACC-NUMBER
        file status is WS-ACC-STATUS.

data division.
file section.

fd ACCOUNT-FILE.
copy "ACCOUNT-RECORD.cpy".

working-storage section.
01 WS-ACC-STATUS pic xx.
01 WS-COUNT      pic 9(4) value 0.
01 WS-END        pic 9 value 0.

procedure division.
main.
    open input ACCOUNT-FILE

    if WS-ACC-STATUS not = "00"
        display "ERROR OPEN ACCOUNT FILE: "
                WS-ACC-STATUS
        move 1 to return-code
        goback
    end-if

    display "ACCOUNT FILE CONTENTS"
    display "---------------------"

    perform until WS-END = 1
        read ACCOUNT-FILE next record
            at end
                move 1 to WS-END
            not at end
                perform SHOW-ACCOUNT
        end-read

        if WS-ACC-STATUS not = "00"
           and WS-ACC-STATUS not = "10"
            display "ERROR READING ACCOUNT: "
                    WS-ACC-STATUS
            move 1 to return-code
            move 1 to WS-END
        end-if
    end-perform

    close ACCOUNT-FILE

    display "TOTAL ACCOUNTS: " WS-COUNT
    goback.

SHOW-ACCOUNT.
    add 1 to WS-COUNT

    display "Account: " ACC-NUMBER
    display "Status : " ACC-STATUS
    display "Currency: " ACC-CURRENCY
    display "Balance: " ACC-BALANCE
    display "---------------------".
