
       >>SOURCE FORMAT FREE
identification division.
program-id. READ-JOURNAL.

environment division.
input-output section.
file-control.
    select JOURNAL-FILE
        assign to "../../data/journal.dat"
        organization is indexed
        access mode is dynamic
        record key is JRN-STAMP
        file status is WS-JRN-STATUS.

data division.
file section.
fd JOURNAL-FILE.
copy "JOURNAL-RECORD.cpy".

working-storage section.
01 WS-JRN-STATUS pic xx.
01 WS-COUNT      pic 9(4) value 0.
01 WS-END        pic 9 value 0.

procedure division.
MAIN.
    open input JOURNAL-FILE

    if WS-JRN-STATUS not = "00"
        display "ERROR OPEN JOURNAL: " WS-JRN-STATUS
        move 1 to return-code
        goback
    end-if

    display "JOURNAL FILE CONTENTS"
    display "---------------------"

    perform until WS-END = 1
        read JOURNAL-FILE next record
            at end
                move 1 to WS-END
            not at end
                perform SHOW-JOURNAL
        end-read

        if WS-JRN-STATUS not = "00"
           and WS-JRN-STATUS not = "10"
            display "ERROR READING JOURNAL: "
                WS-JRN-STATUS
            move 1 to return-code
            move 1 to WS-END
        end-if
    end-perform

    close JOURNAL-FILE

    display "TOTAL JOURNAL RECORDS: " WS-COUNT
    goback.

SHOW-JOURNAL.
    add 1 to WS-COUNT
    display "Stamp         : " JRN-STAMP
    display "Transaction   : " JRN-TRAN-CODE
    display "Credit Account: [" JRN-CR-ACCOUNT "]"
    display "Debit Account : [" JRN-DB-ACCOUNT "]"
    display "Amount        : " JRN-AMOUNT
    display "---------------------".
