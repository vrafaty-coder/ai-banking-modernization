package banking.tx01;

import java.util.*;

/** Independent deterministic test harness; production-generated sources are unchanged. */
public class Tx01ValidationGateV2 {
    static final String ACCOUNT = "0000000000001";
    static final String PREFIX = "20261111091530TERM";
    static int passed = 0, failed = 0;
    static int limitations = 0;

    static class Accounts implements AccountRepository {
        AccountRecord account = new AccountRecord(ACCOUNT, "A", "IRR", 1000);
        boolean openError, updateError, failNextRewrite, rollbackRewriteFailure, readError;
        int reads, writes;
        @Override public AccountRecord read(String id) { reads++; return readError ? null : (account != null && account.accountNumber().equals(id) ? account : null); }
        @Override public void rewrite(AccountRecord r) {
            writes++;
            if (failNextRewrite || (rollbackRewriteFailure && writes >= 2)) { failNextRewrite = false; updateError = true; return; }
            account = r;
        }
        @Override public boolean hasOpenError() { return openError; }
        @Override public boolean hasUpdateError() { return updateError; }
    }
    static class Journals implements JournalRepository {
        final Map<String,JournalRecord> records = new HashMap<>();
        boolean openError, writeError, lookupError;
        int reads, writes;
        @Override public JournalRecord read(String stamp) { reads++; return records.get(stamp); }
        @Override public void write(JournalRecord r) { writes++; if (!writeError) records.put(r.stamp(), r); }
        @Override public boolean hasOpenError() { return openError; }
        @Override public boolean hasWriteError() { return writeError; }
        @Override public boolean hasFileError() { return lookupError; }
    }
    static Tx01Request request(long amount, String seq) {
        return new Tx01Request("TX01", "20261111", "091530", "TERM", seq, ACCOUNT, amount);
    }
    static void check(String name, boolean condition, String details) {
        System.out.println((condition ? "PASS " : "FAIL ") + name + (condition ? "" : " — " + details));
        if (condition) passed++; else failed++;
    }
    static boolean error(Tx01Response r, int alert) {
        return r.statusCode() == 1 && r.alertCode() == alert && r.accountBalance() == 0 && r.journalStamp().isEmpty();
    }
    public static void main(String[] args) {
        Accounts a; Journals j; Tx01Response r;
        a = new Accounts(); j = new Journals(); r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("successful deposit: response/account/journal", r.statusCode()==0 && r.alertCode()==0 && r.accountBalance()==1250 && (PREFIX+"0001").equals(r.journalStamp()) && a.account.balance()==1250 && j.records.size()==1 && j.records.get(PREFIX+"0001").amount()==250, "response="+r+" balance="+a.account.balance()+" journal="+j.records.size());
        a = new Accounts(); j = new Journals(); r = new Tx01Service(a,j).execute(request(0,"0001"));
        check("zero amount: 1004 and no side effects", error(r,1004) && a.account.balance()==1000 && j.records.isEmpty() && a.reads==0, "response="+r);
        a = new Accounts(); a.account = null; j = new Journals(); r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("missing account: 1001", error(r,1001) && j.records.isEmpty(), "response="+r);
        for (String status : new String[]{"B","C","X"}) {
            a = new Accounts(); a.account = new AccountRecord(ACCOUNT,status,"IRR",1000); j = new Journals(); r = new Tx01Service(a,j).execute(request(250,"0001"));
            int alert = status.equals("B") ? 1002 : status.equals("C") ? 1003 : 9001;
            check("account status "+status+": "+alert, error(r,alert) && a.account.balance()==1000 && j.records.isEmpty(), "response="+r);
        }
        a = new Accounts(); a.account = new AccountRecord(ACCOUNT,"A","IRR",999999999999999L); j = new Journals(); r = new Tx01Service(a,j).execute(request(1,"0001"));
        check("15-digit overflow: 1005", error(r,1005) && a.account.balance()==999999999999999L && j.records.isEmpty(), "response="+r);
        a = new Accounts(); j = new Journals(); j.records.put(PREFIX+"0001",new JournalRecord(PREFIX+"0001","TX01",ACCOUNT,"",1)); r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("stamp collision increments sequence", r.statusCode()==0 && (PREFIX+"0002").equals(r.journalStamp()) && j.records.size()==2, "response="+r);
        a = new Accounts(); j = new Journals(); j.records.put(PREFIX+"9999",new JournalRecord(PREFIX+"9999","TX01",ACCOUNT,"",1)); r = new Tx01Service(a,j).execute(request(250,"9999"));
        check("stamp exhaustion: 1006", error(r,1006) && a.account.balance()==1000 && j.records.size()==1, "response="+r);
        a = new Accounts(); j = new Journals(); j.writeError = true; r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("journal write failure: rollback", error(r,9002) && a.account.balance()==1000 && a.writes==2 && j.records.isEmpty(), "response="+r+" balance="+a.account.balance()+" rewrites="+a.writes);
        a = new Accounts(); a.updateError = true; j = new Journals(); r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("injected rewrite error: should reach rewrite first", a.writes==1 && error(r,9001), "rewrites="+a.writes+" response="+r);
        a = new Accounts(); a.rollbackRewriteFailure = true; j = new Journals(); j.writeError = true; r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("injected rollback rewrite failure: state remains updated", error(r,9002) && a.account.balance()==1250 && a.writes==2, "balance="+a.account.balance()+" rewrites="+a.writes);
        // V2: four additional COBOL-derived failure-path scenarios.
        a = new Accounts(); a.openError = true; j = new Journals();
        r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("account open failure: 9001 and no state change",
                error(r,9001) && a.reads==0 && a.writes==0 && a.account.balance()==1000 && j.records.isEmpty(),
                "response="+r+" accountReads="+a.reads);

        a = new Accounts(); j = new Journals(); j.openError = true;
        r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("journal open failure: 9002 and no state change",
                error(r,9002) && a.reads==0 && a.writes==0 && a.account.balance()==1000 && j.records.isEmpty(),
                "response="+r+" accountReads="+a.reads);

        a = new Accounts(); j = new Journals(); j.lookupError = true;
        r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("journal stamp lookup failure: 9002 before account rewrite",
                error(r,9002) && j.reads==1 && a.writes==0 && a.account.balance()==1000 && j.records.isEmpty(),
                "response="+r+" journalReads="+j.reads+" rewrites="+a.writes);

        // A null read means 'not found' in the generated interface. It cannot
        // separately represent COBOL file status 23 versus an I/O read failure.
        a = new Accounts(); a.readError = true; j = new Journals();
        r = new Tx01Service(a,j).execute(request(250,"0001"));
        check("account read I/O failure: expected 9001 (interface limitation)",
                error(r,9001) && a.writes==0 && j.records.isEmpty(),
                "actual="+r.alertCode()+" (null read conflates I/O error with missing account)");

        System.out.println("RESULT passed="+passed+" failed="+failed+" total="+(passed+failed));
        if (failed>0) System.exit(1);
    }
}
