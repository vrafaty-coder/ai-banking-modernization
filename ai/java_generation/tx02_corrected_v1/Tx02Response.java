package banking.tx02;

public record Tx02Response(
        String transactionCode,
        int statusCode,
        int alertCode,
        String alertMessage,
        long accountBalance,
        String journalStamp
) {}
