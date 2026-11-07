# TX01 — Human Validation Record (v1)

**Reference code:** `TX01.cbl` and six supporting copybooks; baseline tag `cobol-baseline-v1.0` / commit `aa18959`.  
**Status:** Preliminary assistant-supported review of the initial extraction. **Independent domain-expert sign-off is pending.**

| Rule | Preliminary verdict | Source-based explanation |
|---|---|---|
| BR-01 | Correct | Explicitly rejects `RCV-AMOUNT = 0` with alert 1004. |
| BR-02 | Correct | Indexed read; file status `23` yields alert 1001. |
| BR-03 | Correct | `ACC-BLOCKED` yields 1002. |
| BR-04 | Correct | `ACC-CLOSED` yields 1003. |
| BR-05 | Correct | Any status other than A/B/C is rejected as invalid with alert 9001; active A proceeds. |
| BR-06 | Correct | Intermediate 16-digit value checked against maximum 999999999999999; alert 1005. |
| BR-07 | Correct | Existing stamp triggers sequence increment, up to 9999; exhaustion yields 1006. |
| BR-08 | Correct | Balance rewritten using `WS-NEW-BALANCE`. |
| BR-09 | Correct | Journal record is initialized, populated and written with transaction code TX01. |
| BR-10 | Partial | `ROLLBACK-ACCOUNT` attempts to restore old balance after journal write failure, but does not verify success of rollback `REWRITE`. |

**Preliminary tally:** 9 Correct, 1 Partial, 0 Incorrect **among the 10 initially identified items**. This is not extraction recall, precision, or a validated model score. A separate exhaustive gold-standard inventory would be required for those metrics.

## Additional code observations

- The journal stamp concatenates transaction date (8), time (6), terminal (4), and sequence (4): 22 characters.
- The success response contains status 00, alert 0000, blank message, resulting balance, and journal stamp.
- On validation failure the initialized transaction-specific response remains zero/blank.
- `OPEN`, `READ`, `REWRITE`, and `WRITE` errors are mapped to 9001 or 9002 as applicable.
- Account and journal are separate indexed files; the code does not establish atomic durability or isolation across the two writes.
- `RCV-TRAN-CODE` is present in the common input but TX01 does not explicitly compare it to `"TX01"`.

## Human review checklist

- [ ] Domain expert confirms the classification of each BR item.
- [ ] Domain expert reviews missing rules and edge cases against source.
- [ ] Record any corrections in a new dated review or Git commit, preserving initial extraction.
- [ ] Separate equivalence requirements from desired production hardening.

## Research integrity note

The same assistant participated in prior system design and initial extraction. This is a documented workflow demonstration, not evidence of zero-context AI rule discovery.
