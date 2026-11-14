# Modernization Experiment Log

**Project:** An AI-Enabled Phased Framework for Incremental Modernization of Legacy Core Banking Systems  
**Repository:** `https://github.com/vrafaty-coder/ai-banking-modernization` (user reported successful push)  
**Reference baseline:** `cobol-baseline-v1.0` / `aa18959` / branch `master`.

## Baseline implementation and reported test results

| Component | Cases passed | Evidence available in conversation | Status |
|---|---:|---|---|
| TX01 Deposit | 7/7 | Prior regression report | Reported PASS |
| TX02 Withdrawal | 7/7 | Prior regression report | Reported PASS |
| TX03 Transfer | 11/11 | Full console regression output, plus T01 account and journal persistence output | Observed output: ALL PASS |
| **Total** | **25/25** | Reported execution in user's local GnuCOBOL environment | **Baseline frozen** |

**Environment reported:** Windows, VS Code, MSYS2 UCRT64, GnuCOBOL 3.2.0. The assistant did not independently execute these tests in the user's environment. Baseline is a scenario-specific regression suite, not proof of production reliability, concurrency safety, or atomicity.

## TX03 noteworthy observed results

- T01 successful transfer: source account `0100000000001` from 1,000,000 to 950,000; destination `0100000000002` from 2,500,000 to 2,550,000; exactly one TX03 journal with amount 50,000 and stamp `20261107121500T0010001`.
- T02–T10 reported PASS for insufficient funds, missing accounts, blocked/closed account, zero amount, same account, currency mismatch, and credit overflow.
- T11 duplicate stamp resolved with sequence 0002; reported PASS.

## Phase 2 — TX01 AI-assisted analysis

| Artifact | State | Notes |
|---|---|---|
| AI initial rule extraction | Recorded | 10 initial items; see `01-ai-initial-extraction-tx01.md` |
| Preliminary validation | Recorded, pending independent sign-off | 9 Correct, 1 Partial among extracted items; see `02-human-validation-tx01.md` |
| Language-neutral specification | Drafted | See `03-business-rules-specification-tx01.md` |
| Initial AI-generated Java | Not started | Preserve raw generated output before human fixes |
| Java regression and COBOL equivalence | Not started | Run matching input/state scenarios |

## Experiment protocol for Java phase

For each conversion iteration, record:

1. Source commit/tag and exact source files provided to the AI.
2. AI provider/model/version (if known), date, prompt, context and settings.
3. Raw first-pass AI output and compilation outcome **before edits**.
4. Every human intervention (reason, code diff, time/effort where measurable).
5. Test setup, exact cases, pass/fail, response differences and persistence differences.
6. Whether a change is an equivalence fix or an intentional design improvement.
7. Final commit and reproducible execution commands.

## Methodological constraints

- Assistant had previous knowledge of and involvement in COBOL design; TX01 initial extraction is **not** an independent blind extraction benchmark.
- Do not report 9/10 as rule-extraction recall or precision; a comprehensive independently annotated reference set is missing.
- GnuCOBOL indexed-file operations do not establish transactional atomicity; keep that separate from functional equivalence.
- Preserve the original baseline tag. Future improvements should be committed separately.

## Next action

Confirm documentation in `docs/` and commit it separately from the frozen COBOL baseline; then begin controlled TX01 Java conversion.
