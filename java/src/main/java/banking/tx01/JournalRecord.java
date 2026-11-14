package banking.tx01;

// Fields correspond to JOURNAL-RECORD.
public record JournalRecord(
        String stamp,                 // X(22)
        String transactionCode,       // X(04)
        String creditAccount,         // X(13)
        String debitAccount,          // X(13)
        long amount                   // 9(15)
) {}
