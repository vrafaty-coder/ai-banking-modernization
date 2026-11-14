
       >>SOURCE FORMAT FREE
identification division.
program-id. TEST-TX02-WITHDRAWAL.

data division.
working-storage section.

01 TX02-RECEIVE.
   copy "COMMON-RECEIVE.cpy".
   copy "TX02-RECEIVE.cpy".

01 TX02-RESPONSE.
   copy "COMMON-RESPONSE.cpy".
   copy "TX02-RESPONSE.cpy".

01 WS-TEST-RESULT pic x(4).

procedure division.

MAIN.
    initialize TX02-RECEIVE
    initialize TX02-RESPONSE

    move "TX02" to RCV-TRAN-CODE
    move 20261107 to RCV-TRAN-DATE
    move 121500 to RCV-TRAN-TIME
    move "T001" to RCV-TRAN-TELLER-TERMINAL
    move 1 to RCV-TRAN-SEQUENCE

    move "0100000000001" to RCV-ACCOUNT-NUMBER
    move 50000 to RCV-AMOUNT

    call "TX02" using
        TX02-RECEIVE
        TX02-RESPONSE
    end-call

    display "TX02 WITHDRAWAL TEST"
    display "-------------------------"
    display "Status : " RSP-STATUS-CODE
    display "Alert  : " RSP-ALERT-CODE
    display "Message: [" RSP-ALERT-MESSAGE "]"
    display "Balance: " RSP-ACCOUNT-BALANCE
    display "Stamp  : [" RSP-JOURNAL-STAMP "]"

    move "FAIL" to WS-TEST-RESULT

    if RSP-TRAN-CODE = "TX02"
       and RSP-STATUS-CODE = 0
       and RSP-ALERT-CODE = 0
       and RSP-ACCOUNT-BALANCE = 950000
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
