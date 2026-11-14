package banking.tx01;

// Fields correspond to COMMON-RESPONSE and TX01-RESPONSE.
public record Tx01Response(
        String transactionCode,       // X(04)
        int statusCode,               // 9(02)
        int alertCode,                // 9(04)
        String alertMessage,         // X(50)
        long accountBalance,          // 9(15)
        String journalStamp           // X(22)
) {}
