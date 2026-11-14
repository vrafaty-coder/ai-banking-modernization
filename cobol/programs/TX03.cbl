       >>SOURCE FORMAT FREE
identification division.
program-id. TX03.

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
01 WS-DB-RECORD        pic x(32).
01 WS-CR-RECORD        pic x(32).
01 WS-DB-OLD-BALANCE   pic 9(15).
01 WS-CR-OLD-BALANCE   pic 9(15).
01 WS-DB-NEW-BALANCE   pic 9(15).
01 WS-CR-NEW-BALANCE   pic 9(16).
01 WS-DB-CURRENCY      pic x(3).
01 WS-SEQUENCE         pic 9(04).
01 WS-STAMP            pic x(22).
01 WS-STAMP-FOUND      pic 9.
01 WS-DB-UPDATED       pic 9.
01 WS-CR-UPDATED       pic 9.
01 WS-ACCOUNT-OPEN     pic 9.
01 WS-JOURNAL-OPEN     pic 9.
01 WS-ROLLBACK-FAILED  pic 9.

linkage section.
01 TX03-RECEIVE.
   copy "COMMON-RECEIVE.cpy".
   copy "TX03-RECEIVE.cpy".
01 TX03-RESPONSE.
   copy "COMMON-RESPONSE.cpy".
   copy "TX03-RESPONSE.cpy".

procedure division using TX03-RECEIVE TX03-RESPONSE.
MAIN.
    initialize TX03-RESPONSE
    move "TX03" to RSP-TRAN-CODE
    move 1 to RSP-STATUS-CODE
    move 0 to WS-ACCOUNT-OPEN WS-JOURNAL-OPEN
              WS-DB-UPDATED WS-CR-UPDATED
              WS-ROLLBACK-FAILED

    if RCV-AMOUNT = 0
        move 1004 to RSP-ALERT-CODE
        move "Invalid amount" to RSP-ALERT-MESSAGE
        goback
    end-if
    if RCV-DB-ACCOUNT = RCV-CR-ACCOUNT
        move 1008 to RSP-ALERT-CODE
        move "Same source and destination account"
          to RSP-ALERT-MESSAGE
        goback
    end-if

    open i-o ACCOUNT-FILE
    if WS-ACC-STATUS not = "00"
        move 9001 to RSP-ALERT-CODE
        move "Account file error" to RSP-ALERT-MESSAGE
        goback
    end-if
    move 1 to WS-ACCOUNT-OPEN
    open i-o JOURNAL-FILE
    if WS-JRN-STATUS not = "00"
        move 9002 to RSP-ALERT-CODE
        move "Journal file error" to RSP-ALERT-MESSAGE
        perform CLOSE-FILES
        goback
    end-if
    move 1 to WS-JOURNAL-OPEN

    move RCV-DB-ACCOUNT to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER
    perform CHECK-ACCOUNT
    if RSP-ALERT-CODE not = 0
        perform CLOSE-FILES
        goback
    end-if
    move ACCOUNT-RECORD to WS-DB-RECORD
    move ACC-BALANCE to WS-DB-OLD-BALANCE
    move ACC-CURRENCY to WS-DB-CURRENCY

    move RCV-CR-ACCOUNT to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER
    perform CHECK-ACCOUNT
    if RSP-ALERT-CODE not = 0
        perform CLOSE-FILES
        goback
    end-if
    move ACCOUNT-RECORD to WS-CR-RECORD
    move ACC-BALANCE to WS-CR-OLD-BALANCE

    if ACC-CURRENCY not = WS-DB-CURRENCY
        move 1009 to RSP-ALERT-CODE
        move "Currency mismatch" to RSP-ALERT-MESSAGE
        perform CLOSE-FILES
        goback
    end-if
    if WS-DB-OLD-BALANCE < RCV-AMOUNT
        move 1007 to RSP-ALERT-CODE
        move "Insufficient funds" to RSP-ALERT-MESSAGE
        perform CLOSE-FILES
        goback
    end-if
    compute WS-CR-NEW-BALANCE =
        WS-CR-OLD-BALANCE + RCV-AMOUNT
    if WS-CR-NEW-BALANCE > 999999999999999
        move 1005 to RSP-ALERT-CODE
        move "Balance overflow" to RSP-ALERT-MESSAGE
        perform CLOSE-FILES
        goback
    end-if
    compute WS-DB-NEW-BALANCE =
        WS-DB-OLD-BALANCE - RCV-AMOUNT

    perform FIND-UNIQUE-STAMP
    if RSP-ALERT-CODE not = 0
        perform CLOSE-FILES
        goback
    end-if

    move WS-DB-RECORD to ACCOUNT-RECORD
    move WS-DB-NEW-BALANCE to ACC-BALANCE
    rewrite ACCOUNT-RECORD
    if WS-ACC-STATUS not = "00"
        move 9001 to RSP-ALERT-CODE
        move "Debit account update error" to RSP-ALERT-MESSAGE
        perform CLOSE-FILES
        goback
    end-if
    move 1 to WS-DB-UPDATED

    move WS-CR-RECORD to ACCOUNT-RECORD
    move WS-CR-NEW-BALANCE to ACC-BALANCE
    rewrite ACCOUNT-RECORD
    if WS-ACC-STATUS not = "00"
        move 9001 to RSP-ALERT-CODE
        move "Credit account update error" to RSP-ALERT-MESSAGE
        perform ROLLBACK-ACCOUNTS
        perform CLOSE-FILES
        goback
    end-if
    move 1 to WS-CR-UPDATED

    initialize JOURNAL-RECORD
    move WS-STAMP to JRN-STAMP
    move "TX03" to JRN-TRAN-CODE
    move RCV-DB-ACCOUNT to JRN-DB-ACCOUNT
    move RCV-CR-ACCOUNT to JRN-CR-ACCOUNT
    move RCV-AMOUNT to JRN-AMOUNT
    write JOURNAL-RECORD
    if WS-JRN-STATUS not = "00"
        move 9002 to RSP-ALERT-CODE
        move "Journal write error" to RSP-ALERT-MESSAGE
        perform ROLLBACK-ACCOUNTS
        perform CLOSE-FILES
        goback
    end-if

    move 0 to RSP-STATUS-CODE RSP-ALERT-CODE
    move spaces to RSP-ALERT-MESSAGE
    move WS-DB-NEW-BALANCE to RSP-DB-ACCOUNT-BALANCE
    move WS-CR-NEW-BALANCE to RSP-CR-ACCOUNT-BALANCE
    move WS-STAMP to RSP-JOURNAL-STAMP
    perform CLOSE-FILES
    goback.

CHECK-ACCOUNT.
    evaluate WS-ACC-STATUS
        when "00"
            evaluate true
                when ACC-BLOCKED
                    move 1002 to RSP-ALERT-CODE
                    move "Account blocked" to RSP-ALERT-MESSAGE
                when ACC-CLOSED
                    move 1003 to RSP-ALERT-CODE
                    move "Account closed" to RSP-ALERT-MESSAGE
                when not ACC-ACTIVE
                    move 9001 to RSP-ALERT-CODE
                    move "Invalid account status"
                      to RSP-ALERT-MESSAGE
            end-evaluate
        when "23"
            move 1001 to RSP-ALERT-CODE
            move "Account not found" to RSP-ALERT-MESSAGE
        when other
            move 9001 to RSP-ALERT-CODE
            move "Account file error" to RSP-ALERT-MESSAGE
    end-evaluate.

FIND-UNIQUE-STAMP.
    move RCV-TRAN-SEQUENCE to WS-SEQUENCE
    move 0 to WS-STAMP-FOUND
    perform until WS-STAMP-FOUND = 1
        move spaces to WS-STAMP
        string RCV-TRAN-DATE
               RCV-TRAN-TIME
               RCV-TRAN-TELLER-TERMINAL
               WS-SEQUENCE
            into WS-STAMP
        end-string
        move WS-STAMP to JRN-STAMP
        read JOURNAL-FILE key is JRN-STAMP
        evaluate WS-JRN-STATUS
            when "23"
                move 1 to WS-STAMP-FOUND
            when "00"
                if WS-SEQUENCE = 9999
                    move 1006 to RSP-ALERT-CODE
                    move "Journal stamp exhausted"
                      to RSP-ALERT-MESSAGE
                    exit perform
                end-if
                add 1 to WS-SEQUENCE
            when other
                move 9002 to RSP-ALERT-CODE
                move "Journal file error" to RSP-ALERT-MESSAGE
                exit perform
        end-evaluate
    end-perform.

ROLLBACK-ACCOUNTS.
    if WS-CR-UPDATED = 1
        move WS-CR-RECORD to ACCOUNT-RECORD
        rewrite ACCOUNT-RECORD
        if WS-ACC-STATUS not = "00"
            move 1 to WS-ROLLBACK-FAILED
        end-if
    end-if
    if WS-DB-UPDATED = 1
        move WS-DB-RECORD to ACCOUNT-RECORD
        rewrite ACCOUNT-RECORD
        if WS-ACC-STATUS not = "00"
            move 1 to WS-ROLLBACK-FAILED
        end-if
    end-if
    if WS-ROLLBACK-FAILED = 1
        move 9001 to RSP-ALERT-CODE
        move "Account rollback failed" to RSP-ALERT-MESSAGE
    end-if.

CLOSE-FILES.
    if WS-JOURNAL-OPEN = 1
        close JOURNAL-FILE
        move 0 to WS-JOURNAL-OPEN
    end-if
    if WS-ACCOUNT-OPEN = 1
        close ACCOUNT-FILE
        move 0 to WS-ACCOUNT-OPEN
    end-if.
