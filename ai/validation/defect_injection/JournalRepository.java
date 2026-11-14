package banking.tx01;

public interface JournalRepository {
    JournalRecord read(String stamp);
    void write(JournalRecord record);
    boolean hasOpenError();
    boolean hasWriteError();
    boolean hasFileError();
}
