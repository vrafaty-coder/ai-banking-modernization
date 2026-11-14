package banking.tx02;

import banking.tx01.JournalRecord;

public interface JournalRepository {
    void open() throws Exception;
    void close() throws Exception;
    boolean exists(String stamp) throws Exception;
    void write(JournalRecord journal) throws Exception;
}
