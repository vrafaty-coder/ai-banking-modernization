       >>SOURCE FORMAT FREE
identification division.
program-id. PREPARE-TX03-TEST-DATA.
environment division.
input-output section.
file-control.
    select ACCOUNT-FILE assign to "../../data/accounts.dat"
        organization is indexed access mode is dynamic
        record key is ACC-NUMBER file status is WS-ACC-STATUS.
    select JOURNAL-FILE assign to "../../data/journal.dat"
        organization is indexed access mode is dynamic
        record key is JRN-STAMP file status is WS-JRN-STATUS.
data division.
file section.
fd ACCOUNT-FILE.
copy "ACCOUNT-RECORD.cpy".
fd JOURNAL-FILE.
copy "JOURNAL-RECORD.cpy".
working-storage section.
01 WS-SCENARIO pic x(3).
01 WS-ACC-STATUS pic xx.
01 WS-JRN-STATUS pic xx.
procedure division.
MAIN.
    move 0 to return-code
    accept WS-SCENARIO from command-line
    evaluate WS-SCENARIO
        when "T09" when "T10"
            open i-o ACCOUNT-FILE
            if WS-ACC-STATUS not = "00"
                display "PREPARE: account open failed"
                move 1 to return-code
                goback
            end-if
            move "0100000000002" to ACC-NUMBER
            read ACCOUNT-FILE key is ACC-NUMBER
            if WS-ACC-STATUS not = "00"
                display "PREPARE: account read failed"
                move 1 to return-code
            else
                evaluate WS-SCENARIO
                    when "T09" move "USD" to ACC-CURRENCY
                    when "T10"
                        move 999999999990000 to ACC-BALANCE
                end-evaluate
                rewrite ACCOUNT-RECORD
                if WS-ACC-STATUS not = "00"
                    display "PREPARE: account rewrite failed"
                    move 1 to return-code
                end-if
            end-if
            close ACCOUNT-FILE
            if WS-ACC-STATUS not = "00"
                move 1 to return-code
            end-if
        when "T11"
            open i-o JOURNAL-FILE
            if WS-JRN-STATUS not = "00"
                display "PREPARE: journal open failed"
                move 1 to return-code
                goback
            end-if
            initialize JOURNAL-RECORD
            move "20261107121500T0010001" to JRN-STAMP
            move "TX03" to JRN-TRAN-CODE
            move "0100000000001" to JRN-DB-ACCOUNT
            move "0100000000002" to JRN-CR-ACCOUNT
            move 1000 to JRN-AMOUNT
            write JOURNAL-RECORD
            if WS-JRN-STATUS not = "00"
                display "PREPARE: journal write failed"
                move 1 to return-code
            end-if
            close JOURNAL-FILE
            if WS-JRN-STATUS not = "00"
                move 1 to return-code
            end-if
        when other
            display "Unsupported preparation: " WS-SCENARIO
            move 1 to return-code
    end-evaluate
    if return-code = 0
        display WS-SCENARIO " DATA PREPARED"
    end-if
    goback.
