package banking.tx02;

import banking.tx01.AccountRecord;

public interface AccountRepository {
    void open() throws Exception;
    void close() throws Exception;
    AccountRecord read(String accountNumber) throws Exception;
    void rewrite(AccountRecord account) throws Exception;
}
