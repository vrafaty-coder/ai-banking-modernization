
       >>SOURCE FORMAT FREE
identification division.
program-id. TEST-TX01-DEPOSIT.

data division.
working-storage section.

01 TX01-RECEIVE.
   copy "COMMON-RECEIVE.cpy".
   copy "TX01-RECEIVE.cpy".

01 TX01-RESPONSE.
   copy "COMMON-RESPONSE.cpy".
   copy "TX01-RESPONSE.cpy".

01 WS-TEST-RESULT pic x(4).

procedure division.

MAIN.
    initialize TX01-RECEIVE
    initialize TX01-RESPONSE

    move "TX01" to RCV-TRAN-CODE
    move 20261107 to RCV-TRAN-DATE
    move 121500 to RCV-TRAN-TIME
    move "T001" to RCV-TRAN-TELLER-TERMINAL
    move 1 to RCV-TRAN-SEQUENCE

    move "0100000000001" to RCV-ACCOUNT-NUMBER
    move 50000 to RCV-AMOUNT

    call "TX01" using
        TX01-RECEIVE
        TX01-RESPONSE
    end-call

    display "TX01 DEPOSIT TEST"
    display "-------------------------"
    display "Status : " RSP-STATUS-CODE
    display "Alert  : " RSP-ALERT-CODE
    display "Message: [" RSP-ALERT-MESSAGE "]"
    display "Balance: " RSP-ACCOUNT-BALANCE
    display "Stamp  : [" RSP-JOURNAL-STAMP "]"

    move "FAIL" to WS-TEST-RESULT

    if RSP-TRAN-CODE = "TX01"
       and RSP-STATUS-CODE = 0
       and RSP-ALERT-CODE = 0
       and RSP-ACCOUNT-BALANCE = 1050000
       and RSP-JOURNAL-STAMP =
           "20261107121500T0010001"
        move "PASS" to WS-TEST-RESULT
    end-if

    display "-------------------------"
    display "TEST RESULT: " WS-TEST-RESULT

    if WS-TEST-RESULT = "FAIL"
        move 1 to return-code
    else
        move 0 to return-code
    end-if

    goback.
