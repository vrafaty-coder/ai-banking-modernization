
       >>SOURCE FORMAT FREE
identification division.
program-id. TX01.

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
01 WS-OLD-BALANCE      pic 9(15).
01 WS-NEW-BALANCE      pic 9(16).
01 WS-SEQUENCE         pic 9(04).
01 WS-STAMP            pic x(22).
01 WS-STAMP-FOUND      pic 9.
01 WS-ACCOUNT-UPDATED  pic 9.
01 WS-ACCOUNT-OPEN     pic 9.
01 WS-JOURNAL-OPEN     pic 9.

linkage section.
01 TX01-RECEIVE.
   copy "COMMON-RECEIVE.cpy".
   copy "TX01-RECEIVE.cpy".

01 TX01-RESPONSE.
   copy "COMMON-RESPONSE.cpy".
   copy "TX01-RESPONSE.cpy".

procedure division using TX01-RECEIVE TX01-RESPONSE.

MAIN.
    initialize TX01-RESPONSE
    move "TX01" to RSP-TRAN-CODE
    move 1 to RSP-STATUS-CODE

    move 0 to WS-ACCOUNT-OPEN
              WS-JOURNAL-OPEN
              WS-ACCOUNT-UPDATED

    if RCV-AMOUNT = 0
        move 1004 to RSP-ALERT-CODE
        move "Invalid amount" to RSP-ALERT-MESSAGE
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

    move RCV-ACCOUNT-NUMBER to ACC-NUMBER
    read ACCOUNT-FILE key is ACC-NUMBER

    evaluate WS-ACC-STATUS
        when "00"
            continue
        when "23"
            move 1001 to RSP-ALERT-CODE
            move "Account not found" to RSP-ALERT-MESSAGE
            perform CLOSE-FILES
            goback
        when other
            move 9001 to RSP-ALERT-CODE
            move "Account file error" to RSP-ALERT-MESSAGE
            perform CLOSE-FILES
            goback
    end-evaluate

    evaluate true
        when ACC-BLOCKED
            move 1002 to RSP-ALERT-CODE
            move "Account blocked" to RSP-ALERT-MESSAGE
        when ACC-CLOSED
            move 1003 to RSP-ALERT-CODE
            move "Account closed" to RSP-ALERT-MESSAGE
        when not ACC-ACTIVE
            move 9001 to RSP-ALERT-CODE
            move "Invalid account status" to RSP-ALERT-MESSAGE
    end-evaluate

    if RSP-ALERT-CODE not = 0
        perform CLOSE-FILES
        goback
    end-if

    move ACC-BALANCE to WS-OLD-BALANCE
    compute WS-NEW-BALANCE =
        ACC-BALANCE + RCV-AMOUNT

    if WS-NEW-BALANCE > 999999999999999
        move 1005 to RSP-ALERT-CODE
        move "Balance overflow" to RSP-ALERT-MESSAGE
        perform CLOSE-FILES
        goback
    end-if

    perform FIND-UNIQUE-STAMP

    if RSP-ALERT-CODE not = 0
        perform CLOSE-FILES
        goback
    end-if

    move WS-NEW-BALANCE to ACC-BALANCE
    rewrite ACCOUNT-RECORD

    if WS-ACC-STATUS not = "00"
        move 9001 to RSP-ALERT-CODE
        move "Account update error" to RSP-ALERT-MESSAGE
        perform CLOSE-FILES
        goback
    end-if

    move 1 to WS-ACCOUNT-UPDATED

    initialize JOURNAL-RECORD
    move WS-STAMP to JRN-STAMP
    move "TX01" to JRN-TRAN-CODE
    move RCV-ACCOUNT-NUMBER to JRN-CR-ACCOUNT
    move RCV-AMOUNT to JRN-AMOUNT

    write JOURNAL-RECORD

    if WS-JRN-STATUS not = "00"
        move 9002 to RSP-ALERT-CODE
        move "Journal write error" to RSP-ALERT-MESSAGE
        perform ROLLBACK-ACCOUNT
        perform CLOSE-FILES
        goback
    end-if

    move 0 to RSP-STATUS-CODE
              RSP-ALERT-CODE
    move spaces to RSP-ALERT-MESSAGE
    move WS-NEW-BALANCE to RSP-ACCOUNT-BALANCE
    move WS-STAMP to RSP-JOURNAL-STAMP

    perform CLOSE-FILES
    goback.

FIND-UNIQUE-STAMP.
    move RCV-TRAN-SEQUENCE to WS-SEQUENCE
    move 0 to WS-STAMP-FOUND

    perform until WS-STAMP-FOUND = 1
        move spaces to WS-STAMP

        string
            RCV-TRAN-DATE
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
                move "Journal file error"
                    to RSP-ALERT-MESSAGE
                exit perform
        end-evaluate
    end-perform.

ROLLBACK-ACCOUNT.
    if WS-ACCOUNT-UPDATED = 1
        move RCV-ACCOUNT-NUMBER to ACC-NUMBER
        read ACCOUNT-FILE key is ACC-NUMBER
        if WS-ACC-STATUS = "00"
            move WS-OLD-BALANCE to ACC-BALANCE
            rewrite ACCOUNT-RECORD
        end-if
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
