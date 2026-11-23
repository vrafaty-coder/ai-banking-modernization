# AI-Enabled Core Banking Modernization

A research project exploring how Generative AI can support the incremental modernization of legacy COBOL banking applications into Java.

The project focuses on extracting business rules from existing COBOL programs, generating Java implementations, and validating banking behavior through automated tests.

The experiments cover two banking transactions: **TX01 Deposit** and **TX02 Withdrawal**.

## Approach

The research follows a phased modernization process:

1. Analyze existing COBOL programs and copybooks.
2. Extract business rules using LLM-only and structure-aware LLM+RAG approaches.
3. Compare extracted rules against human-reviewed reference rules.
4. Generate Java implementations using AI assistance.
5. Validate transaction behavior through a banking-specific Validation Gate.
6. Investigate discrepancies, correct the implementation, and repeat validation.

The Validation Gate checks transaction responses, account balances, journal records, and business-rule behavior.

## Key Findings

- Structure-aware LLM+RAG achieved higher business-rule coverage than LLM-only extraction in both transactions.
- For TX01 Deposit, full reference-rule coverage increased from **13/15 to 14/15**.
- For TX02 Withdrawal, full reference-rule coverage increased from **12/17 to 15/17**.
- Following correction of the identified response-handling issue, the TX02 Java implementation passed all **64 recorded validation checks**.
- Five deliberately introduced defects in TX01 were successfully detected by the validation framework.

The experiments demonstrate how AI-assisted modernization can be combined with deterministic validation and human review.

## Technologies

- COBOL and GnuCOBOL
- Java
- Generative AI and LLMs
- Structure-aware retrieval (RAG)
- Python
- Bash
- Git and GitHub

## Repository Structure

- `cobol/` — COBOL programs, copybooks, and regression materials
- `java/` — Java implementations and validation tests
- `ai/` — AI-assisted extraction and generation artifacts
- `experiments/` — Experimental results and validation evidence
- `evaluation/` — Evaluation utilities
- `docs/` — Design documentation and research notes
- `scripts/` — Verification scripts

For detailed reproduction instructions, see [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Getting Started

Clone the repository:

```bash
git clone https://github.com/vrafaty-coder/ai-banking-modernization.git
cd ai-banking-modernization
```

Run the Java validation tests:

```bash
bash scripts/verify_java.sh
```

Run the COBOL regression tests:

```bash
bash scripts/verify_cobol.sh
```

The Java tests require a JDK, Python 3, and Bash. The COBOL regression tests additionally require GnuCOBOL.

## Research Paper

**An AI-Enabled Phased Framework for Incremental Modernization of Legacy Core Banking Systems**

Vahideh Rafati Porshokooh

Informatics Services Corporation, Tehran, Iran

The research snapshot is available under the [v1.0-paper](https://github.com/vrafaty-coder/ai-banking-modernization/tree/v1.0-paper) tag.

## Limitations

The experiments use controlled banking prototypes rather than production systems.

The Validation Gate evaluates predefined scenarios against expected behavior derived from COBOL source analysis. It does not establish formal equivalence between COBOL and Java.

The research is intended to investigate AI-assisted modernization methods, not to provide a production-ready migration solution.
