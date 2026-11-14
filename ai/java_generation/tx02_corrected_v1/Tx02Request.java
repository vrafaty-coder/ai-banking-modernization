package banking.tx02;

public record Tx02Request(
        String transactionCode,
        String transactionDate,
        String transactionTime,
        String tellerTerminal,
        String transactionSequence,
        String accountNumber,
        long amount
) {}
