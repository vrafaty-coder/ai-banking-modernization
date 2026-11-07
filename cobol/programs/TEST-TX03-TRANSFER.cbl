
       >>SOURCE FORMAT FREE
identification division.
program-id. TEST-TX03-TRANSFER.

data division.
working-storage section.

01 WS-RECEIVE.
    copy "COMMON-RECEIVE.cpy".
    copy "TX03-RECEIVE.cpy".

01 WS-RESPONSE.
    copy "COMMON-RESPONSE.cpy".
    copy "TX03-RESPONSE.cpy".

procedure division.

MAIN.
    initialize WS-RECEIVE WS-RESPONSE

    move "TX03" to RCV-TRAN-CODE
    move 20261107 to RCV-TRAN-DATE
    move 121500 to RCV-TRAN-TIME
    move "T001" to RCV-TRAN-TELLER-TERMINAL
    move 1 to RCV-TRAN-SEQUENCE

    move "0100000000001" to RCV-DB-ACCOUNT
    move "0100000000002" to RCV-CR-ACCOUNT
    move 50000 to RCV-AMOUNT

    call "TX03" using WS-RECEIVE WS-RESPONSE

    display "TX03 TRANSFER TEST"
    display "-------------------------"
    display "Status : " RSP-STATUS-CODE
    display "Alert  : " RSP-ALERT-CODE
    display "Message: [" RSP-ALERT-MESSAGE "]"
    display "Debit Balance : " RSP-DB-ACCOUNT-BALANCE
    display "Credit Balance: " RSP-CR-ACCOUNT-BALANCE
    display "Stamp  : [" RSP-JOURNAL-STAMP "]"
    display "-------------------------"

    if RSP-TRAN-CODE = "TX03"
       and RSP-STATUS-CODE = 0
       and RSP-ALERT-CODE = 0
       and RSP-ALERT-MESSAGE = spaces
       and RSP-DB-ACCOUNT-BALANCE = 950000
       and RSP-CR-ACCOUNT-BALANCE = 2550000
       and RSP-JOURNAL-STAMP =
           "20261107121500T0010001"
        display "T01 RESULT: PASS"
        move 0 to return-code
    else
        display "T01 RESULT: FAIL"
        move 1 to return-code
    end-if

    goback.
