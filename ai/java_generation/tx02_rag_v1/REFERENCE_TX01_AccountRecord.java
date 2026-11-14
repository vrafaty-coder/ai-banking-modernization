package banking.tx01;

// Fields correspond to ACCOUNT-RECORD.
public record AccountRecord(
        String accountNumber,         // X(13)
        String status,                // X(01): A, B, C
        String currency,              // X(03)
        long balance                  // 9(15)
) {}
