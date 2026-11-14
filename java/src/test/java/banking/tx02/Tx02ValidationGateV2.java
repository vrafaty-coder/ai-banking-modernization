
package banking.tx02;

import banking.tx01.AccountRecord;
import banking.tx01.JournalRecord;
import java.util.*;

public class Tx02ValidationGateV2 {

    static final String ID = "0000000000001";
    static final String PREFIX = "20261111091530TERM";
    static final long INITIAL_BALANCE = 1000;

    static class Accounts implements AccountRepository {
        AccountRecord record =
            new AccountRecord(ID, "A", "IRR", INITIAL_BALANCE);

        boolean failOpen = false;
        boolean failRead = false;
        boolean failRewrite = false;
        boolean failRollback = false;
        boolean failRollbackRead = false;

        int reads = 0;
        int writes = 0;

        public void open() throws Exception {
            if (failOpen) throw new Exception("Account open error");
        }

        public void close() {}

        public AccountRecord read(String accountNumber) throws Exception {
            reads++;

            if (failRead || (failRollbackRead && reads == 2))
                throw new Exception("Account read error");

            if (record == null) return null;

            return record.accountNumber().equals(accountNumber)
                ? record : null;
        }

        public void rewrite(AccountRecord updated) throws Exception {
            writes++;

            if (failRewrite || (failRollback && writes == 2))
                throw new Exception("Account rewrite error");

            record = updated;
        }
    }

    static class Journals implements JournalRepository {
        Map<String, JournalRecord> records = new HashMap<>();

        int writes = 0;
        boolean failOpen = false;
        boolean failLookup = false;
        boolean failWrite = false;

        public void close() {}

        public void open() throws Exception {
            if (failOpen) throw new Exception("Journal open error");
        }

        public boolean exists(String stamp) throws Exception {
            if (failLookup) throw new Exception("Journal lookup error");
            return records.containsKey(stamp);
        }

        public void write(JournalRecord record) throws Exception {
            writes++;
            if (failWrite) throw new Exception("Journal write error");
            records.put(record.stamp(), record);
        }
    }

    static class Scenario {
        String id;
        String name;
        long amount = 250;
        String sequence = "0001";
        int expectedStatus = 1;
        int expectedAlert = 0;
        String expectedMessage = "";
        long expectedResponseBalance = 0;
        long expectedFinalBalance = INITIAL_BALANCE;
        int expectedJournalCount = 0;
        int expectedJournalWrites = 0;
        int expectedRewrites = 0;
        String expectedStamp = "";

        Accounts accounts = new Accounts();
        Journals journals = new Journals();

        Scenario(String id, String name) {
            this.id = id;
            this.name = name;
        }
    }

    static void check(String scenario, String dimension,
                      boolean passed, String details) {
        System.out.printf(
            "%s | %-13s | %-4s | %s%n",
            scenario,
            dimension,
            passed ? "PASS" : "FAIL",
            details
        );
    }

    static String clean(String value) {
        return value == null ? "" : value.trim();
    }

    static void evaluate(Scenario s) {
        Tx02Request request = new Tx02Request(
            "TX02", "20261111", "091530",
            "TERM", s.sequence, ID, s.amount
        );

        Tx02Response response;

        try {
            response = new Tx02Service(
                s.accounts, s.journals
            ).process(request);
        } catch (Exception ex) {
            for (String dimension : new String[]{
                    "RESPONSE", "ACCOUNT",
                    "JOURNAL", "BUSINESS_RULE"}) {
                check(s.id, dimension, false,
                      "Unexpected exception: " + ex);
            }
            return;
        }

        boolean responsePass =
            "TX02".equals(response.transactionCode())
            && response.statusCode() == s.expectedStatus
            && response.alertCode() == s.expectedAlert
            && clean(response.alertMessage())
                .equals(s.expectedMessage)
            && response.accountBalance()
                == s.expectedResponseBalance
            && clean(response.journalStamp())
                .equals(s.expectedStamp);

        boolean accountPass =
            (s.accounts.record == null
                ? s.id.equals("S03")
                : s.accounts.record.balance()
                    == s.expectedFinalBalance)
            && s.accounts.writes == s.expectedRewrites;


        boolean journalPass =
            s.journals.records.size() == s.expectedJournalCount
            && s.journals.writes == s.expectedJournalWrites;

        if (journalPass && s.expectedStatus == 0
        && s.expectedJournalCount > 0) {
            JournalRecord jr =
                s.journals.records.get(s.expectedStamp);

            journalPass = jr != null
                && "TX02".equals(jr.transactionCode())
                && ID.equals(jr.debitAccount())
                && clean(jr.creditAccount()).isEmpty()
                && jr.amount() == s.amount;
        }

        if (s.id.equals("S08")) {
            JournalRecord original =
                s.journals.records.get(PREFIX + "0001");

            journalPass = journalPass
                && original != null
                && "TX02".equals(original.transactionCode())
                && ID.equals(original.debitAccount())
                && original.amount() == 100;
        }

        boolean businessRulePass =
            responsePass && accountPass && journalPass;

        check(s.id, "RESPONSE", responsePass,
            "alert=" + response.alertCode()
            + " balance=" + response.accountBalance()
            + " stamp=[" + response.journalStamp() + "]"
            + " message=[" + response.alertMessage() + "]");

        check(s.id, "ACCOUNT", accountPass,
              "balance=" + (s.accounts.record == null
                  ? "null" : s.accounts.record.balance())
              + " rewrites=" + s.accounts.writes);


        check(s.id, "JOURNAL", journalPass,
            "count=" + s.journals.records.size()
            + " writes=" + s.journals.writes);


        check(s.id, "BUSINESS_RULE", businessRulePass,
              s.name);
    }

    public static void main(String[] args) {
        List<Scenario> scenarios = new ArrayList<>();

        Scenario s;

        s = new Scenario("S01", "Successful withdrawal");
        s.expectedStatus = 0;
        s.expectedResponseBalance = 750;
        s.expectedFinalBalance = 750;
        s.expectedJournalCount = 1;
        s.expectedJournalWrites = 1;
        s.expectedRewrites = 1;
        s.expectedStamp = PREFIX + "0001";
        scenarios.add(s);

        s = new Scenario("S02", "Zero amount");
        s.amount = 0;
        s.expectedAlert = 1004;
        s.expectedMessage = "Invalid amount";
        scenarios.add(s);

        s = new Scenario("S03", "Missing account");
        s.accounts.record = null;
        s.expectedAlert = 1001;
        s.expectedMessage = "Account not found";
        scenarios.add(s);

        s = new Scenario("S04", "Blocked account");
        s.accounts.record =
            new AccountRecord(ID, "B", "IRR", INITIAL_BALANCE);
        s.expectedAlert = 1002;
        s.expectedMessage = "Account blocked";
        scenarios.add(s);

        s = new Scenario("S05", "Closed account");
        s.accounts.record =
            new AccountRecord(ID, "C", "IRR", INITIAL_BALANCE);
        s.expectedAlert = 1003;
        s.expectedMessage = "Account closed";
        scenarios.add(s);

        s = new Scenario("S06", "Invalid account status");
        s.accounts.record =
            new AccountRecord(ID, "X", "IRR", INITIAL_BALANCE);
        s.expectedAlert = 9001;
        s.expectedMessage = "Invalid account status";
        scenarios.add(s);

        s = new Scenario("S07", "Insufficient funds");
        s.amount = 1500;
        s.expectedAlert = 1007;
        s.expectedMessage = "Insufficient funds";
        scenarios.add(s);

        s = new Scenario("S08", "Journal stamp collision");
        s.expectedStatus = 0;
        s.expectedResponseBalance = 750;
        s.expectedFinalBalance = 750;
        s.expectedJournalCount = 2;
        s.expectedJournalWrites = 1;
        s.expectedRewrites = 1;
        s.expectedStamp = PREFIX + "0002";

        s.journals.records.put(
            PREFIX + "0001",
            new JournalRecord(PREFIX + "0001", "TX02", null, ID, 100)
        );

        scenarios.add(s);

        s = new Scenario("S09", "Journal stamp exhaustion");
        s.sequence = "9999";
        s.expectedAlert = 1006;
        s.expectedMessage = "Journal stamp exhausted";
        s.expectedJournalCount = 1;
        s.expectedRewrites = 0;

        s.journals.records.put(
            PREFIX + "9999",
            new JournalRecord(PREFIX + "9999", "TX02", null, ID, 100)
        );

        scenarios.add(s);

        s = new Scenario("S10", "Journal write failure and rollback");

        s.journals.failWrite = true;

        s.expectedAlert = 9002;
        s.expectedMessage = "Journal write error";
        s.expectedResponseBalance = 0;
        s.expectedFinalBalance = INITIAL_BALANCE;
        s.expectedJournalCount = 0;
        s.expectedJournalWrites = 1;
        s.expectedRewrites = 2;
        s.expectedStamp = "";

        scenarios.add(s);

        s = new Scenario("S11", "Account rewrite failure");

        s.accounts.failRewrite = true;

        s.expectedAlert = 9001;
        s.expectedMessage = "Account update error";
        s.expectedResponseBalance = 0;
        s.expectedFinalBalance = INITIAL_BALANCE;
        s.expectedJournalCount = 0;
        s.expectedRewrites = 1;
        s.expectedStamp = "";

        scenarios.add(s);

        s = new Scenario("S12", "Rollback rewrite failure");

        s.journals.failWrite = true;
        s.accounts.failRollback = true;

        s.expectedAlert = 9002;
        s.expectedMessage = "Journal write error";
        s.expectedResponseBalance = 0;
        s.expectedFinalBalance = 750;
        s.expectedJournalCount = 0;
        s.expectedJournalWrites = 1;
        s.expectedRewrites = 2;
        s.expectedStamp = "";

        scenarios.add(s);

        s = new Scenario("S13", "Account open failure");

        s.accounts.failOpen = true;

        s.expectedAlert = 9001;
        s.expectedMessage = "Account file error";
        s.expectedResponseBalance = 0;
        s.expectedFinalBalance = INITIAL_BALANCE;
        s.expectedJournalCount = 0;
        s.expectedRewrites = 0;
        s.expectedStamp = "";

        scenarios.add(s);

        s = new Scenario("S14", "Journal open failure");

        s.journals.failOpen = true;

        s.expectedAlert = 9002;
        s.expectedMessage = "Journal file error";
        s.expectedResponseBalance = 0;
        s.expectedFinalBalance = INITIAL_BALANCE;
        s.expectedJournalCount = 0;
        s.expectedRewrites = 0;
        s.expectedStamp = "";

        scenarios.add(s);

        s = new Scenario("S15", "Journal lookup failure");

        s.journals.failLookup = true;

        s.expectedAlert = 9002;
        s.expectedMessage = "Journal file error";
        s.expectedResponseBalance = 0;
        s.expectedFinalBalance = INITIAL_BALANCE;
        s.expectedJournalCount = 0;
        s.expectedRewrites = 0;
        s.expectedStamp = "";

        scenarios.add(s);

        s = new Scenario("S16", "Account read failure");

        s.accounts.failRead = true;

        s.expectedAlert = 9001;
        s.expectedMessage = "Account file error";
        s.expectedResponseBalance = 0;
        s.expectedFinalBalance = INITIAL_BALANCE;
        s.expectedJournalCount = 0;
        s.expectedRewrites = 0;
        s.expectedStamp = "";

scenarios.add(s);

        for (Scenario scenario : scenarios) {
            evaluate(scenario);
        }
    }
}
