# AI-Enabled Incremental Core Banking Modernization

**COBOL → Java | Generative AI | Structure-Aware Retrieval | Business-Rule Extraction | Banking-Specific Validation**

Research artifacts accompanying *An AI-Enabled Phased Framework for Incremental Modernization of Legacy Core Banking Systems*, by Vahideh Rafati Porshokooh (Informatics Services Corporation, Tehran, Iran).

This repository investigates a **human-supervised, phased approach** to understanding legacy COBOL business rules, generating Java implementations, and validating observable banking behavior. It contains **independently authored, small research prototypes**, not production banking software or customer data.

**Scope:** TX01 **Deposit** (15 reference rules) and TX02 **Withdrawal** (17 reference rules). TX03 Transfer is **not** part of the reported study.

## Research questions and contributions

- Compare **LLM-only** and **structure-aware LLM+RAG** business-rule extraction against frozen, human-reviewed reference rules.
- Evaluate generated Java through a **deterministic, COBOL-source-derived Validation Gate** for response, account, journal, and composite business-rule behavior.
- Demonstrate discrepancy detection, targeted correction, revalidation, and controlled defect injection within predefined scenarios.

The contribution is the **evaluated integration** of these steps, not the invention of LLMs, retrieval, or functional testing.

## Research workflow

```text
COBOL programs and copybooks
           |
           +--------------------------+
           |                          |
       LLM-only                Structure-aware
       extraction              LLM+RAG extraction
           |                          |
           +------------+-------------+
                        |
         Human-reviewed semantic evaluation
         (FULL / PARTIAL / NONE; unique Gold coverage)
                        |
         Evaluation-informed strategy decision
         (research-level, NOT an automatic selector)
                        |
              AI-assisted Java generation
                        |
          Banking-specific Validation Gate
          RESPONSE | ACCOUNT | JOURNAL |
             BUSINESS_RULE (composite)
                        |
          PASS / FAIL / NOT_EVALUABLE
                        |
        Targeted correction and revalidation
```

Both extraction approaches used the **same COBOL programs and copybooks**, organized and presented differently. Structure-aware retrieval uses named COBOL paragraphs, direct callers, and referenced copybook definitions; it **does not implement embedding-based/vector-search RAG**.

For Java generation, **TX01 used LLM-only extracted rules** and **TX02 used LLM+RAG extracted rules**. The study **did not** compare Java generation methods head-to-head on the same transaction. Gold Standard rules and human-validation judgments were excluded from generation prompts.

## Results reported in the paper

### 1. Human-reviewed business-rule extraction

The primary measure is **unique FULL Gold Standard coverage**: each distinct fully covered reference rule is counted once, even when extracted outputs overlap. This differs from counting output-level FULL/PARTIAL/NONE classifications.

| Transaction | Extraction method | Unique FULL-covered reference rules | Total reference rules | FULL coverage |
|---|---|---:|---:|---:|
| TX01 Deposit | LLM-only | 13 | 15 | 86.67% |
| TX01 Deposit | LLM+RAG | 14 | 15 | 93.33% |
| TX02 Withdrawal | LLM-only | 12 | 17 | 70.59% |
| TX02 Withdrawal | LLM+RAG | 15 | 17 | 88.24% |

In these cases, LLM+RAG showed **+6.67 percentage points** for TX01 and **+17.65 percentage points** for TX02 in unique FULL coverage. This does **not** establish general superiority or isolate the causal effect of retrieval. Some outputs classified **NONE** describe source-supported file-closing behavior that falls outside the frozen Gold reference set; NONE must not automatically be interpreted as hallucination.

### 2. Java functional Validation Gate

Each transaction has **16 scenarios × 4 recorded checks = 64 check records**, **not 64 independent executions**.

| Implementation | PASS | FAIL | NOT_EVALUABLE | Total checks |
|---|---:|---:|---:|---:|
| TX01 initial | 60 | 0 | 4 | 64 |
| TX02 initial | 54 | 10 | 0 | 64 |
| TX02 corrected | 64 | 0 | 0 | 64 |

The recorded dimensions are **RESPONSE**, **ACCOUNT**, **JOURNAL**, and **BUSINESS_RULE**. BUSINESS_RULE is a **composite** of relevant checks, not a fourth independent oracle.

**TX01 — S16 limitation:** All four NOT_EVALUABLE checks belong to scenario **S16 (Account Read I/O Error)**. The Java repository's `read()` returned `null` both for a missing account and for an account-read I/O error, so the gate could not conclusively distinguish these conditions. The other 15 scenarios passed all four recorded dimensions.

**TX02 — targeted correction:** In scenarios **S09, S10, S11, S12, and S15**, the initial Java implementation incorrectly included an attempted journal stamp in unsuccessful transaction responses. **RESPONSE** and composite **BUSINESS_RULE** failed (10 checks), while **ACCOUNT** and **JOURNAL** passed. After separating the internal processing stamp from the response stamp and populating the latter only on success, revalidation produced **64 PASS**. This is **post-correction success**, not first-pass success.

### 3. Controlled TX01 defect injection

Five deliberately selected mutations were detected (**5/5**): acceptance of zero amounts, acceptance of blocked accounts, disabling overflow prevention, using the wrong journal account, and disabling rollback. This is limited evidence for these mutations and targeted scenarios, not exhaustive defect detection.

## Technology and research methods

| Area | Technologies / approach |
|---|---|
| Legacy implementation | COBOL, copybooks, GnuCOBOL |
| Target implementation | Java |
| AI-assisted analysis | LLMs, structure-aware retrieval-assisted extraction |
| Rule evaluation | Frozen source-derived Gold rules, human-reviewed FULL/PARTIAL/NONE classifications |
| Validation | Deterministic scenario-based banking checks |
| Reproducibility | Bash, Python, recorded prompts/manifests, Git |

## Repository guide

- `cobol/programs/` and `cobol/copybooks/` — controlled source prototypes and regression materials.
- `ai/` — extraction, Java-generation, and validation artifacts.
- `ai/java_generation/` — preserved original generation snapshots, prompts, manifests, and uncorrected variants. **Do not recursively compile these together.**
- `java/src/main/java/banking/{tx01,tx02}/` — canonical Java implementations.
- `java/src/test/java/banking/{tx01,tx02}/` — runnable research Validation Gates.
- `experiments/` — frozen human-reviewed results and historical evidence.
- `evaluation/` — evaluation utilities; automated outputs do not replace human adjudication.
- `docs/` — design documentation and experiment notes.
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md) — detailed prerequisites, execution, and limitations.
- [SECURITY_REVIEW.md](SECURITY_REVIEW.md) and [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) — review and release preparation.
- [CITATION.cff](CITATION.cff) — citation metadata under preparation.

## Reproducing the local checks

Clone the repository:

```bash
git clone https://github.com/vrafaty-coder/ai-banking-modernization.git
cd ai-banking-modernization
```

**Java Validation Gates** (JDK, Python 3, Bash; no Gemini API key needed):

```bash
bash scripts/verify_java.sh
```

This compiles canonical TX01 and corrected TX02 implementations and runs both 16-scenario gates using a temporary directory, without modifying frozen evidence.

**Separate COBOL regression checks** (GnuCOBOL and Bash required):

```bash
bash scripts/verify_cobol.sh
```

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) before running experiments. These scripts verify the bounded prototypes; they do not perform live COBOL–Java differential testing.

## Research artifact, publication and citation

**Associated manuscript:** *An AI-Enabled Phased Framework for Incremental Modernization of Legacy Core Banking Systems*.

The manuscript references the fixed research snapshot at **[`v1.0-paper`](https://github.com/vrafaty-coder/ai-banking-modernization/tree/v1.0-paper)**. This tag is accessible on GitHub. **A separately published GitHub Release has not yet been verified/published**; a Git tag and a GitHub Release are not the same thing. Consult [CITATION.cff](CITATION.cff) and the release checklist before citing a finalized archival release or DOI.

## Limitations and future work

- Two independently authored, controlled transactions; no real banking workload or production data.
- Human-reviewed Gold/reference decisions were **not independently blinded**.
- Retrieval differs in source-context organization; results do not demonstrate general RAG superiority.
- Java generation methods were **not compared on the same transaction**.
- Expected outcomes were **derived from interpreted COBOL source**, not paired live COBOL–Java execution; **formal or differential equivalence is not established**.
- Scenario coverage and five selected mutations do **not** establish exhaustive correctness or production readiness.
- The study does not model concurrent updates or full enterprise transaction coordination; source-derived rollback behavior is not a guarantee of atomicity.

Future work includes same-transaction generation comparisons, independent expert adjudication, broader transaction and mutation coverage, live differential testing, and realistic performance, concurrency, integration, and recovery evaluation.

---

**Research focus:** Core Banking · COBOL · Legacy/Mainframe Modernization · Generative AI · Structure-Aware RAG · Java · Functional Validation
