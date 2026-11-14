package banking.tx02;

import banking.tx01.AccountRecord;
import banking.tx01.JournalRecord;

public class Tx02Service {

    private final AccountRepository accountRepository;
    private final JournalRepository journalRepository;

    public Tx02Service(AccountRepository accountRepository, JournalRepository journalRepository) {
        this.accountRepository = accountRepository;
        this.journalRepository = journalRepository;
    }

    public Tx02Response process(Tx02Request request) {
        String rspTranCode = "TX02";
        int rspStatusCode = 1;
        int rspAlertCode = 0;
        String rspAlertMessage = "";
        long rspAccountBalance = 0;
        String rspJournalStamp = "";

        int wsAccountOpen = 0;
        int wsJournalOpen = 0;
        int wsAccountUpdated = 0;
        long wsOldBalance = 0;
        long wsNewBalance = 0;

        if (request.amount() == 0) {
            return new Tx02Response(rspTranCode, rspStatusCode, 1004, padRight("Invalid amount", 50), rspAccountBalance, rspJournalStamp);
        }

        try {
            accountRepository.open();
            wsAccountOpen = 1;
        } catch (Exception e) {
            return new Tx02Response(rspTranCode, rspStatusCode, 9001, padRight("Account file error", 50), rspAccountBalance, rspJournalStamp);
        }

        try {
            journalRepository.open();
            wsJournalOpen = 1;
        } catch (Exception e) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, 9002, padRight("Journal file error", 50), rspAccountBalance, rspJournalStamp);
        }

        AccountRecord account;
        try {
            account = accountRepository.read(request.accountNumber());
        } catch (Exception e) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, 9001, padRight("Account file error", 50), rspAccountBalance, rspJournalStamp);
        }

        if (account == null) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, 1001, padRight("Account not found", 50), rspAccountBalance, rspJournalStamp);
        }

        if ("B".equals(account.status())) {
            rspAlertCode = 1002;
            rspAlertMessage = "Account blocked";
        } else if ("C".equals(account.status())) {
            rspAlertCode = 1003;
            rspAlertMessage = "Account closed";
        } else if (!"A".equals(account.status())) {
            rspAlertCode = 9001;
            rspAlertMessage = "Invalid account status";
        }

        if (rspAlertCode != 0) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, rspAlertCode, padRight(rspAlertMessage, 50), rspAccountBalance, rspJournalStamp);
        }

        wsOldBalance = account.balance();
        if (account.balance() < request.amount()) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, 1007, padRight("Insufficient funds", 50), rspAccountBalance, rspJournalStamp);
        }

        wsNewBalance = account.balance() - request.amount();
        if (wsNewBalance > 999999999999999L) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, 1005, padRight("Balance overflow", 50), rspAccountBalance, rspJournalStamp);
        }

        StampResult stampResult = findUniqueStamp(request);
        rspAlertCode = stampResult.alertCode;
        rspAlertMessage = stampResult.alertMessage;
        rspJournalStamp = stampResult.stamp;

        if (rspAlertCode != 0) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, rspAlertCode, padRight(rspAlertMessage, 50), rspAccountBalance, rspJournalStamp);
        }

        AccountRecord updatedAccount = new AccountRecord(
                account.accountNumber(),
                account.status(),
                account.currency(),
                wsNewBalance
        );

        try {
            accountRepository.rewrite(updatedAccount);
            wsAccountUpdated = 1;
        } catch (Exception e) {
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, 9001, padRight("Account update error", 50), rspAccountBalance, rspJournalStamp);
        }

        JournalRecord journalRecord = new JournalRecord(
                rspJournalStamp,
                "TX02",
                null,
                request.accountNumber(),
                request.amount()
        );

        try {
            journalRepository.write(journalRecord);
        } catch (Exception e) {
            if (wsAccountUpdated == 1) {
                try {
                    AccountRecord rollbackAccount = accountRepository.read(request.accountNumber());
                    if (rollbackAccount != null) {
                        AccountRecord restored = new AccountRecord(
                                rollbackAccount.accountNumber(),
                                rollbackAccount.status(),
                                rollbackAccount.currency(),
                                wsOldBalance
                        );
                        accountRepository.rewrite(restored);
                    }
                } catch (Exception ignored) {}
            }
            closeFiles(wsAccountOpen, wsJournalOpen);
            return new Tx02Response(rspTranCode, rspStatusCode, 9002, padRight("Journal write error", 50), rspAccountBalance, rspJournalStamp);
        }

        rspStatusCode = 0;
        rspAlertCode = 0;
        rspAlertMessage = "";
        rspAccountBalance = wsNewBalance;

        closeFiles(wsAccountOpen, wsJournalOpen);

        return new Tx02Response(
                rspTranCode,
                rspStatusCode,
                rspAlertCode,
                padRight(rspAlertMessage, 50),
                rspAccountBalance,
                rspJournalStamp
        );
    }

    private StampResult findUniqueStamp(Tx02Request request) {
        int sequence;
        try {
            sequence = Integer.parseInt(request.transactionSequence());
        } catch (NumberFormatException e) {
            sequence = 0;
        }

        int stampFound = 0;
        int alertCode = 0;
        String alertMessage = "";
        String wsStamp = "";

        while (stampFound == 0) {
            String seqStr = String.format("%04d", sequence);
            wsStamp = request.transactionDate() +
                      request.transactionTime() +
                      request.tellerTerminal() +
                      seqStr;

            try {
                boolean exists = journalRepository.exists(wsStamp);
                if (!exists) {
                    stampFound = 1;
                } else {
                    if (sequence == 9999) {
                        alertCode = 1006;
                        alertMessage = "Journal stamp exhausted";
                        break;
                    }
                    sequence++;
                }
            } catch (Exception e) {
                alertCode = 9002;
                alertMessage = "Journal file error";
                break;
            }
        }

        return new StampResult(wsStamp, alertCode, alertMessage);
    }

    private void closeFiles(int wsAccountOpen, int wsJournalOpen) {
        if (wsJournalOpen == 1) {
            try {
                journalRepository.close();
            } catch (Exception ignored) {}
        }
        if (wsAccountOpen == 1) {
            try {
                accountRepository.close();
            } catch (Exception ignored) {}
        }
    }

    private String padRight(String s, int n) {
        if (s == null) {
            s = "";
        }
        if (s.length() >= n) {
            return s.substring(0, n);
        }
        return String.format("%-" + n + "s", s);
    }

    private static class StampResult {
        final String stamp;
        final int alertCode;
        final String alertMessage;

        StampResult(String stamp, int alertCode, String alertMessage) {
            this.stamp = stamp;
            this.alertCode = alertCode;
            this.alertMessage = alertMessage;
        }
    }
}
