# TX01 Semantic Matching — Evaluation Protocol v1 (proposed)

Reference: `tx01_gold_standard_v1.0.json` (15 rules). Inputs: three frozen Gemini outputs. Do not alter the reference or original model outputs.

## Units and matching

1. A model rule is matched to a reference rule only if its **condition AND action** are semantically supported. Evidence/source citations are checked separately; their absence is not automatically a semantic mismatch in these historical outputs.
2. One model rule may match several reference rules when it explicitly and correctly states every corresponding condition/action (e.g. blocked, closed, inactive statuses). Annotate each reference ID separately; no inferred rules.
3. A reference rule is covered once per run, regardless of repeated model outputs. A model output that only repeats already-covered references is a duplicate for output-level precision.
4. Unsupported or incorrect model rules are unmatched. Partially correct rules require explicit adjudication and must not be silently counted as full matches.
5. Category mismatches (BUSINESS/INTEGRITY/TECHNICAL) are tracked separately from semantic correctness. Report BUSINESS-only reference coverage as primary and INTEGRITY/TECHNICAL as supplemental.
6. Freeze the adjudicated mapping and this protocol before reporting definitive results. Record reviewer, review date, baseline hashes, and any uncertain matches.

## Metrics and caveat

- **Reference-rule coverage / recall** = number of distinct covered reference rules / total reference rules.
- **Output-level precision** = number of model output items that add at least one new, correct reference-rule match / total model output items. This deliberately penalizes duplicate output items.
- Because recall is **reference-rule-level** while precision is **model-output-level**, their harmonic mean is a *hybrid descriptive score*, not a conventional entity-level F1. Do **not** label it standard F1 in the paper.
- To report conventional Precision/Recall/F1, first adjudicate a one-to-one atomic-rule representation (split compound model rules into separately auditable atomic claims; preserve source provenance and assess unsupported fragments). Then compute TP, FP, FN in that common unit.
- Until the mapping is independently reviewed, all numbers are provisional.

## Historical pilot

Existing `tx01_llm_semantic_mapping_draft.csv` contains a proposed, non-independent mapping. Its 13/15, 11/15, and 9/15 coverage values are preliminary and must not be described as validated model performance.
