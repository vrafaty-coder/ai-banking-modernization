package banking.tx01;

public class Tx01Service {
    private final AccountRepository accountRepository;
    private final JournalRepository journalRepository;

    public Tx01Service(AccountRepository accountRepository, JournalRepository journalRepository) {
        this.accountRepository = accountRepository;
        this.journalRepository = journalRepository;
    }

    public Tx01Response execute(Tx01Request request) {
        String rspTranCode = "TX01";
        int rspStatusCode = 1;
        int rspAlertCode = 0;
        String rspAlertMessage = "";
        long rspAccountBalance = 0;
        String rspJournalStamp = "";

        if (request.amount() == 0) {
            return new Tx01Response(rspTranCode, rspStatusCode, 1004, "Invalid amount", rspAccountBalance, rspJournalStamp);
        }

        if (accountRepository.hasOpenError()) {
            return new Tx01Response(rspTranCode, rspStatusCode, 9001, "Account file error", rspAccountBalance, rspJournalStamp);
        }

        if (journalRepository.hasOpenError()) {
            return new Tx01Response(rspTranCode, rspStatusCode, 9002, "Journal file error", rspAccountBalance, rspJournalStamp);
        }

        AccountRecord account = accountRepository.read(request.accountNumber());
        if (account == null) {
            return new Tx01Response(rspTranCode, rspStatusCode, 1001, "Account not found", rspAccountBalance, rspJournalStamp);
        }

        if (accountRepository.hasUpdateError()) {
            return new Tx01Response(rspTranCode, rspStatusCode, 9001, "Account file error", rspAccountBalance, rspJournalStamp);
        }

        if ("B".equals(account.status())) {
            return new Tx01Response(rspTranCode, rspStatusCode, 1002, "Account blocked", rspAccountBalance, rspJournalStamp);
        } else if ("C".equals(account.status())) {
            return new Tx01Response(rspTranCode, rspStatusCode, 1003, "Account closed", rspAccountBalance, rspJournalStamp);
        } else if (!"A".equals(account.status())) {
            return new Tx01Response(rspTranCode, rspStatusCode, 9001, "Invalid account status", rspAccountBalance, rspJournalStamp);
        }

        long oldBalance = account.balance();
        long newBalance = oldBalance + request.amount();

        if (newBalance > 999999999999999L) {
            return new Tx01Response(rspTranCode, rspStatusCode, 1005, "Balance overflow", rspAccountBalance, rspJournalStamp);
        }

        int sequence = Integer.parseInt(request.transactionSequence());
        String stamp = "";
        boolean stampFound = false;

        while (!stampFound) {
            String seqStr = String.format("%04d", sequence);
            stamp = request.transactionDate() + request.transactionTime() + request.tellerTerminal() + seqStr;

            JournalRecord existingJournal = journalRepository.read(stamp);
            if (journalRepository.hasFileError()) {
                rspAlertCode = 9002;
                rspAlertMessage = "Journal file error";
                break;
            }

            if (existingJournal == null) {
                stampFound = true;
            } else {
                if (sequence == 9999) {
                    rspAlertCode = 1006;
                    rspAlertMessage = "Journal stamp exhausted";
                    break;
                }
                sequence++;
            }
        }

        if (rspAlertCode != 0) {
            return new Tx01Response(rspTranCode, rspStatusCode, rspAlertCode, rspAlertMessage, rspAccountBalance, rspJournalStamp);
        }

        AccountRecord updatedAccount = new AccountRecord(
                account.accountNumber(),
                account.status(),
                account.currency(),
                newBalance
        );
        accountRepository.rewrite(updatedAccount);

        if (accountRepository.hasUpdateError()) {
            return new Tx01Response(rspTranCode, rspStatusCode, 9001, "Account update error", rspAccountBalance, rspJournalStamp);
        }

        JournalRecord newJournal = new JournalRecord(
                stamp,
                "TX01",
                request.accountNumber(),
                "",
                request.amount()
        );
        journalRepository.write(newJournal);

        if (journalRepository.hasWriteError()) {
            AccountRecord rollbackAccount = accountRepository.read(request.accountNumber());
            if (rollbackAccount != null && !accountRepository.hasUpdateError()) {
                AccountRecord restoredAccount = new AccountRecord(
                        rollbackAccount.accountNumber(),
                        rollbackAccount.status(),
                        rollbackAccount.currency(),
                        oldBalance
                );
                accountRepository.rewrite(restoredAccount);
            }
            return new Tx01Response(rspTranCode, rspStatusCode, 9002, "Journal write error", rspAccountBalance, rspJournalStamp);
        }

        rspStatusCode = 0;
        rspAlertCode = 0;
        rspAlertMessage = "";
        rspAccountBalance = newBalance;
        rspJournalStamp = stamp;

        return new Tx01Response(rspTranCode, rspStatusCode, rspAlertCode, rspAlertMessage, rspAccountBalance, rspJournalStamp);
    }
}
