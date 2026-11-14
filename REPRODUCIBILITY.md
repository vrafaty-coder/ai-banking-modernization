# Reproducibility and verification notes

## Prerequisites

- Java JDK with `javac` and `java` (modern Java supporting `record` types).
- GnuCOBOL (`cobc`) for COBOL regression suites (not installed in the current review environment).
- Python 3 for the research scripts; package versions must be frozen before a full reproducibility claim.
- Gemini access only for optional **new** LLM generation runs; no API key is needed for the recorded results or local Java gate.

## Checks performed on the staging copy

- Python: 36 `.py` files parsed successfully with Python AST (syntax only; imports/runtime not verified).
- Shell: both `run-tx01-tests.sh` and `run-tx02-tests.sh` passed `bash -n` (syntax only).
- Java TX01: selected Java sources compiled; `banking.tx01.Tx01ValidationGateV3` executed successfully and printed 15 PASS + 1 NOT_EVALUABLE per check dimension (60 PASS, 4 NOT_EVALUABLE total).
- Java TX02 corrected variant: selective compilation passed. The corrected TX02 gate was rerun using the canonical source tree and all 64 scenario-dimension records were checked.
- GnuCOBOL regression scripts: **user executed on Windows**, reporting TX01 T01–T07 PASS and TX02 T01–T07 PASS with GnuCOBOL 3.2.0. The assistant has not independently rerun them on this exact release candidate.

Run the verified Java checks using `bash scripts/verify_java.sh` from the repository root. This uses temporary build/output directories and does not rewrite the frozen experiment artifacts.

## COBOL regression suites (user-run on Windows)

From `cobol/programs/`, run `bash run-tx01-tests.sh` or `bash run-tx02-tests.sh` after installing GnuCOBOL. These scripts **reset test data** through `INIT-DATA.cbl`; run them only in an isolated disposable working directory. They test T01–T07 and are distinct from the paper's 16-scenario Java Validation Gate.

## Known packaging limitations

1. Java experiment snapshots contain `REFERENCE_TX01_*.java` copies whose filenames do not match their public Java class names. **Do not compile all `.java` files recursively.** Use the selective source lists in `scripts/verify_java.sh`.
2. TX02's preparation `manifest.json` records `PREPARED_NOT_EXECUTED`, whereas `generation_run_manifest.json` describes a later generation run. Both are preserved to document their respective stages.
3. The Validation Gate oracle is derived from interpreted COBOL source and response contracts, not paired live COBOL/Java execution.
4. Historical experiment logs are not the final adjudication; use frozen final records in `experiments/`.
5. Full dependency locking, end-to-end rerun, data-generation verification, and a complete secrets audit remain open before public release.

## Canonical Java dependency layout

`java/src/main/java/banking/tx01` contains the TX01 model types plus generated service/repository interfaces. `java/src/main/java/banking/tx02` contains the corrected TX02 service, request/response and repository interfaces, which import shared TX01 account/journal records. Both gates live in `java/src/test/java/banking`. Original generator output and prompts remain unchanged under `ai/java_generation/` for provenance. The build deliberately avoids recursive compilation of snapshot sources.

## Safe isolated COBOL regression command

Run `bash scripts/verify_cobol.sh` from the repository root on a machine with GnuCOBOL installed. The wrapper copies `cobol/programs/` and `cobol/copybooks/` into a disposable temporary directory, then executes the original TX01 and TX02 regression suites there. **The suites reset their test account/journal data; never execute them directly in a directory containing valuable data.** The wrapper returns an explicit error if `cobc` is unavailable. The user executed the isolated wrapper successfully after the temporary `data` directory was added. This staging copy has not been independently re-executed on the final package.

## V4 packaging verification

On the V4 staging tree, `bash scripts/verify_java.sh` completed successfully: TX01 60 PASS and 4 NOT_EVALUABLE; TX02 64 PASS. COBOL was not rerun on this V4 package; the earlier Windows V2 run reported 7/7 scenarios PASS for each transaction.
