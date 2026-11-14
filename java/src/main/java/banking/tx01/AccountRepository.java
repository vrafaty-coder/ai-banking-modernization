package banking.tx01;

public interface AccountRepository {
    AccountRecord read(String accountNumber);
    void rewrite(AccountRecord record);
    boolean hasOpenError();
    boolean hasUpdateError();
}
