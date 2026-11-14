# TX01 — Language-Neutral Behavior Specification (v1.0)

**Reference:** COBOL `cobol-baseline-v1.0`, commit `aa18959`.  
**Purpose:** Behavioral contract for incremental migration and functional-equivalence testing. This specifies **observed reference behavior**, not a production banking design.

## Interface and storage

| Item | Contract |
|---|---|
| Transaction | `TX01` — deposit |
| Input header | Transaction code X(4), date 8 digits, time 6 digits, terminal X(4), sequence 4 digits |
| Input body | Account number X(13), amount 15-digit unsigned decimal |
| Output header | Transaction code X(4), status 2 digits, alert 4 digits, message X(50) |
| Output body | Resulting account balance 15 digits, journal stamp X(22) |
| Account record | Account number X(13), status X(1), currency X(3), balance 15 digits |
| Journal record | Stamp X(22), transaction code X(4), credit account X(13), debit account X(13), amount 15 digits |

Account and journal files use indexed records, with account number and journal stamp as their respective keys.

## Rules and ordered behavior

1. Initialize response: code TX01, failure status 01, alert 0000, blank message, zero balance, blank stamp.
2. Reject amount zero (1004). The input format is unsigned, so negative amounts are not represented by this contract.
3. Open account file (9001 on failure), then journal file (9002 on failure).
4. Read account by number: missing key (1001), other read error (9001).
5. Reject blocked B (1002), closed C (1003), or any non-active/unrecognized status (9001). Active A proceeds.
6. Calculate new balance using a sufficiently wide intermediate. Reject values above 999999999999999 (1005).
7. Build candidate stamp from date + time + terminal + sequence. If already present, increment sequence; if occupied at 9999, fail 1006. Other journal read errors fail 9002.
8. Rewrite account with new balance; account rewrite error fails 9001.
9. Initialize journal; set stamp, code TX01, credit account = input account, debit account = blanks, amount = input amount. Write journal.
10. If journal write fails, return 9002 and attempt to restore original account balance; rollback success is not checked.
11. On success, return status 00, alert 0000, blank message, new balance and final journal stamp.
12. Close any successfully opened files on the paths implemented in the reference.

## Error response matrix

| Condition | Status | Alert | Message | Balance | Stamp |
|---|---|---|---|---|---|
| Success | 00 | 0000 | spaces | New balance | Selected stamp |
| Account not found | 01 | 1001 | Account not found | 0 | spaces |
| Account blocked | 01 | 1002 | Account blocked | 0 | spaces |
| Account closed | 01 | 1003 | Account closed | 0 | spaces |
| Amount zero | 01 | 1004 | Invalid amount | 0 | spaces |
| Balance overflow | 01 | 1005 | Balance overflow | 0 | spaces |
| Stamp exhausted | 01 | 1006 | Journal stamp exhausted | 0 | spaces |
| Account file/open/read error | 01 | 9001 | Account file error (or relevant account error text) | 0 | spaces |
| Invalid account status | 01 | 9001 | Invalid account status | 0 | spaces |
| Account update error | 01 | 9001 | Account update error | 0 | spaces |
| Journal file/open/read error | 01 | 9002 | Journal file error | 0 | spaces |
| Journal write error | 01 | 9002 | Journal write error | 0 | spaces |

Messages are space-padded to 50 characters. Exact error messages should be checked against source for each tested path.

## Equivalence acceptance criteria

For the same initial account/journal state and same request, compare:

- Response transaction code, status, alert, padded message, resulting balance and stamp.
- Final account balance and unchanged unrelated accounts.
- Journal count and exact journal content (stamp, transaction code, debit/credit accounts, amount).
- No state changes for pre-write validation errors.
- Collision behavior of journal stamp and sequence increment.

**Important limitations:** A failed journal write after a successful account rewrite can leave inconsistent state if rollback fails; this reference has no transactional atomicity guarantee. The Java implementation must distinguish strict behavioral equivalence from intentional robustness improvements. Daily deposit limits and currency validation are not present in TX01.
