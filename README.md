# AI-assisted incremental core banking modernization (research prototype)

This repository contains **small, independently authored research prototypes**, not production banking software. The paper evaluates **TX01 Deposit** and **TX02 Withdrawal** only. TX03 is outside the reported study.

## Research workflow

COBOL source/copybooks → LLM-only or structure-aware retrieval-assisted business-rule extraction → **human-reviewed** evaluation against frozen reference rules → AI-assisted Java generation → deterministic, COBOL-source-derived banking Validation Gate → targeted correction and revalidation.

The retrieval method uses COBOL paragraph structure, direct callers and copybook references; it is **not embedding/vector-search RAG**. The study does not establish formal or live COBOL–Java differential equivalence.

## Frozen results reported in the paper

| Transaction | Method | Unique FULL-covered reference rules | Reference rules | FULL coverage |
|---|---|---:|---:|---:|
| TX01 | LLM-only | 13 | 15 | 86.67% |
| TX01 | LLM+RAG | 14 | 15 | 93.33% |
| TX02 | LLM-only | 12 | 17 | 70.59% |
| TX02 | LLM+RAG | 15 | 17 | 88.24% |

The TX01 Validation Gate reports **60 PASS, 0 FAIL, 4 NOT_EVALUABLE** across 16 scenarios × 4 checks. The initial TX02 gate reported **54 PASS, 10 FAIL**; after targeted correction it reported **64 PASS**. Five selected TX01 defect injections were detected (5/5). Four gate dimensions are RESPONSE, ACCOUNT, JOURNAL, BUSINESS_RULE; BUSINESS_RULE is a composite check, not an independent fourth oracle.

**Interpretation:** These are bounded scenario-based conformance findings, not proof of complete equivalence, production readiness, or a controlled causal advantage for RAG.

## Repository contents

- `cobol/programs/` and `cobol/copybooks/`: source prototypes and regression tests.
- `ai/`: extraction, generation, Java variants, and validation artifacts.
- `java/src/main/java/banking/{tx01,tx02}/`: canonical, dependency-complete Java implementations.
- `java/src/test/java/banking/{tx01,tx02}/`: runnable Validation Gates (not production code).
- `ai/java_generation/`: preserved original generation snapshots, manifests, prompts, and uncorrected variants; do not recursively compile these.
- `experiments/`: frozen final human-reviewed results (historical files may also be present).
- `evaluation/`: evaluation utilities; their automated outputs do not replace human adjudication.
- `docs/`: design documentation and historical experiment notes.
- `REPRODUCIBILITY.md`: local checks, prerequisites, and known limitations.

## Publication and provenance

All COBOL and copybook prototypes were authored independently for this research and are intentionally small. No production banking data were used. **Do not interpret this repository as a production core banking implementation.**

This is a **review/staging package**, not a verified public GitHub release. The repository's license and archival release URL have not yet been finalized. Do not cite a release until it has been published and its exact tag/commit verified.

## Verification

Run `bash scripts/verify_java.sh` from the repository root to compile canonical TX01 and corrected TX02 sources and execute both 16-scenario Java gates. This requires a JDK and Python 3, but no Gemini API key. The script uses a temporary directory and leaves frozen evidence untouched.

For isolated COBOL regression checks (GnuCOBOL required), run `bash scripts/verify_cobol.sh`. This is separate from the 16-scenario Java Validation Gates.
