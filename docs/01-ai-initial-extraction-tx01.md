# TX01 — AI Initial Business Rule Extraction (v1)

**Project:** An AI-Enabled Phased Framework for Incremental Modernization of Legacy Core Banking Systems  
**Reference:** `cobol-baseline-v1.0`, commit `aa18959` (reported by project owner)  
**Inputs inspected:** `TX01.cbl`, `ACCOUNT-RECORD.cpy`, `JOURNAL-RECORD.cpy`, `COMMON-RECEIVE.cpy`, `COMMON-RESPONSE.cpy`, `TX01-RECEIVE.cpy`, `TX01-RESPONSE.cpy`.  
**Provenance:** Reconstructed verbatim in substance from the first AI extraction recorded in the project conversation; formatting and traceability references were added for archiving. **Not a blind, independent model evaluation:** the assistant had prior involvement in designing the reference implementation.

## Initial extracted rules (preserved)

| ID | Initial extraction | Evidence in source |
|---|---|---|
| BR-01 | Deposit amount must not be zero. | `RCV-AMOUNT = 0` |
| BR-02 | Destination account must exist. | `READ ACCOUNT-FILE` |
| BR-03 | Deposits to blocked accounts are prohibited. | `ACC-BLOCKED` |
| BR-04 | Deposits to closed accounts are prohibited. | `ACC-CLOSED` |
| BR-05 | Account must have active status. | `ACC-ACTIVE` |
| BR-06 | Resulting balance must fit within 15 decimal digits. | `WS-NEW-BALANCE > 999999999999999` |
| BR-07 | Journal stamp must be unique. | `FIND-UNIQUE-STAMP` |
| BR-08 | Successful deposit increases account balance. | `REWRITE ACCOUNT-RECORD` |
| BR-09 | Successful deposit writes one TX01 journal record. | `WRITE JOURNAL-RECORD` |
| BR-10 | On journal write failure, program attempts to restore prior balance. | `ROLLBACK-ACCOUNT` |

**Classification caveat:** BR-10 describes failure recovery, rather than a standalone banking business rule.

## Initially extracted processing outline

1. Initialize response to failure.
2. Validate nonzero amount; open account and journal files.
3. Find account and validate account status.
4. Calculate proposed balance and check overflow.
5. Find a unique journal stamp.
6. Rewrite account, then write journal.
7. Return success, or an error response with cleanup and possible rollback.

## Initially identified risks / omissions

- Rollback is best effort: the return status of the rollback rewrite is not checked.
- No explicit locking, concurrency control, or atomic commit guarantee appears in this implementation.
- TX01 does not implement daily deposit limits or currency validation.

## Evaluation boundary

This file preserves the *initial AI output*, not an independently verified gold standard. Do not overwrite its extracted-rule list with human corrections; use `02-human-validation-tx01.md` for validation.
