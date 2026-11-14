package banking.tx01;

// Fields correspond to COMMON-RECEIVE and TX01-RECEIVE.
public record Tx01Request(
        String transactionCode,       // X(04)
        String transactionDate,       // 9(08), preserve leading zeros
        String transactionTime,       // 9(06), preserve leading zeros
        String tellerTerminal,        // X(04)
        String transactionSequence,   // 9(04), preserve leading zeros
        String accountNumber,         // X(13)
        long amount                   // 9(15)
) {}
