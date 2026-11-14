# TX02 Withdrawal — Detailed LLM-only vs LLM+RAG Comparison

**Policy:** B v2 | **Gold:** frozen v1.0 (17 rules) | **Human Validation:** preserved, no new adjudication.

## Executive findings

- LLM+RAG: **19** extracted; **17 FULL**, **0 PARTIAL**, **2 NONE** (valid outside-Gold close-file rules); **15** unique FULL Gold; **2** duplicate FULL mappings; **4** FULL category mismatches.
- LLM-only: **11** extracted; **10 FULL**, **1 PARTIAL**, **0 NONE**; **12** unique Gold covered by FULL mappings; **13** if the PARTIAL Gold is included.
- RAG adds **3 FULL-covered Gold** relative to LLM-only, or **2** relative to FULL+PARTIAL coverage.
- **Primary duplicate-penalized F1:** RAG **83.3333%**; LLM-only **not established under the one-Gold-per-output Policy B v2** because LLM-05 and LLM-09 have user-approved multi-Gold mappings. No Human Validation decisions were changed.

## Policy B v2 metrics

| Metric | LLM-only (preserved historical review) | LLM+RAG |
|---|---:|---:|
| Extracted outputs N | 11 | 19 |
| Frozen Gold M | 17 | 17 |
| FULL outputs | 10 | 17 |
| PARTIAL outputs | 1 | 0 |
| NONE outputs | 0 | 2 |
| Unique FULL Gold covered | 12 | 15 |
| Unique FULL or PARTIAL Gold covered | 13 | 15 |
| FULL output fraction (descriptive) | 90.91% | 89.47% |
| Unique FULL Gold recall | 70.59% | 88.24% |
| Semantic Precision under Policy B v2 | Not directly comparable with multi-Gold mapping | 89.47% |
| Semantic F1 under Policy B v2 | Not established | 88.85% |
| Duplicate-Penalized Precision | Not established | 78.95% |
| **Primary Duplicate-Penalized F1** | **Not established** | **83.33%** |
| Category Accuracy on FULL | Not fully verified | 76.47% |

## LLM-only — preserved per-output decisions

| Output | Label | Approved Gold mapping(s) | Category |
|---|---|---|---|
| LLM-01 | FULL | BR-TX02-001 | Not individually verified in current source |
| LLM-02 | FULL | TECH-TX02-001 | Not individually verified in current source |
| LLM-03 | FULL | TECH-TX02-002 | Not individually verified in current source |
| LLM-04 | FULL | BR-TX02-002 | Mismatch |
| LLM-05 | FULL | BR-TX02-003, BR-TX02-004, BR-TX02-005 | Not individually verified in current source |
| LLM-06 | FULL | BR-TX02-006 | Not individually verified in current source |
| LLM-07 | FULL | BR-TX02-007 | Not individually verified in current source |
| LLM-08 | FULL | TECH-TX02-004 | Not individually verified in current source |
| LLM-09 | FULL | TECH-TX02-006, INT-TX02-003 | Not individually verified in current source |
| LLM-10 | PARTIAL | INT-TX02-002 | Mismatch |
| LLM-11 | FULL | INT-TX02-003 | Not individually verified in current source |

**Important:** LLM-05 covers three Gold rules and LLM-09 two Gold rules in the historical review. LLM-09 and LLM-11 both cover INT-TX02-003. The source-preserving table does not force these into one-to-one assignments.

## RAG — preserved per-output decisions

| Output | Label | Gold | Category match | Duplicate | Notes |
|---|---|---|---|---|---|
| RAG-01 | FULL | BR-TX02-001 | True | False |  |
| RAG-02 | FULL | TECH-TX02-001 | True | False |  |
| RAG-03 | FULL | TECH-TX02-002 | True | False |  |
| RAG-04 | FULL | BR-TX02-002 | True | False |  |
| RAG-05 | FULL | TECH-TX02-003 | True | False |  |
| RAG-06 | FULL | BR-TX02-003 | True | False |  |
| RAG-07 | FULL | BR-TX02-004 | True | False |  |
| RAG-08 | FULL | BR-TX02-005 | True | False |  |
| RAG-09 | FULL | BR-TX02-006 | True | False |  |
| RAG-10 | FULL | BR-TX02-007 | False | False |  |
| RAG-11 | FULL | TECH-TX02-004 | False | False |  |
| RAG-12 | FULL | TECH-TX02-006 | False | False |  |
| RAG-13 | FULL | INT-TX02-002 | True | False |  |
| RAG-14 | FULL | INT-TX02-002 | True | True |  |
| RAG-15 | FULL | INT-TX02-002 | False | True |  |
| RAG-16 | FULL | TECH-TX02-005 | True | False |  |
| RAG-17 | FULL | INT-TX02-003 | True | False |  |
| RAG-18 | NONE | — | None | False | OUTSIDE_FROZEN_GOLD_NOT_HALLUCINATION |
| RAG-19 | NONE | — | None | False | OUTSIDE_FROZEN_GOLD_NOT_HALLUCINATION |

## Gold coverage comparison

| Gold ID | Gold category | LLM-only | RAG |
|---|---|---|---|
| BR-TX02-001 | BUSINESS | FULL | FULL |
| BR-TX02-002 | BUSINESS | FULL | FULL |
| BR-TX02-003 | BUSINESS | FULL | FULL |
| BR-TX02-004 | BUSINESS | FULL | FULL |
| BR-TX02-005 | BUSINESS | FULL | FULL |
| BR-TX02-006 | BUSINESS | FULL | FULL |
| BR-TX02-007 | BUSINESS | FULL | FULL |
| BR-TX02-008 | BUSINESS | MISS | MISS |
| INT-TX02-001 | INTEGRITY | MISS | MISS |
| INT-TX02-002 | INTEGRITY | PARTIAL | FULL |
| INT-TX02-003 | INTEGRITY | FULL | FULL |
| TECH-TX02-001 | TECHNICAL | FULL | FULL |
| TECH-TX02-002 | TECHNICAL | FULL | FULL |
| TECH-TX02-003 | TECHNICAL | MISS | FULL |
| TECH-TX02-004 | TECHNICAL | FULL | FULL |
| TECH-TX02-005 | TECHNICAL | MISS | FULL |
| TECH-TX02-006 | TECHNICAL | FULL | FULL |

## Error and evidence analysis

- **RAG category mismatches:** RAG-10, RAG-11, RAG-12, RAG-15.
- **LLM-only known category mismatches:** LLM-04 (FULL), LLM-10 (PARTIAL). Complete category-accuracy denominator not independently verified.
- **RAG duplicate branches:** RAG-13, RAG-14, RAG-15 all map to INT-TX02-002; only one counts toward U.
- **RAG valid outside-Gold:** RAG-18 and RAG-19 close open files correctly; neither is hallucination.
- **RAG missed Gold:** BR-TX02-008, INT-TX02-001.
- **LLM-only FULL-missed Gold:** BR-TX02-008, INT-TX02-001, INT-TX02-002, TECH-TX02-003, TECH-TX02-005.
- **LLM-only FULL+PARTIAL-missed Gold:** BR-TX02-008, INT-TX02-001, TECH-TX02-003, TECH-TX02-005.

## Interpretation and limitations

RAG has greater observed FULL Gold coverage (15/17 vs 12/17), but the user-approved LLM-only review permits multiple Gold mappings for single outputs. Consequently, the official primary Policy B v2 F1 cannot be compared numerically without introducing a new mapping choice. We deliberately do not change the frozen decisions. The RAG method also comprises separate paragraph-level generations and is not proven to be a single controlled run. Human labels were user-approved, not independently blinded. Evidence fidelity is separate from semantic correctness. Rollback is an attempt and must not be claimed as guaranteed atomicity.

**Preservation:** The JSON file contains the complete frozen Gold rules, all 19 RAG reviews, the historical 11 LLM-only decisions as recoverable, computed metrics, coverage, and caveats. Original files remain unchanged.
