
"""
Build reproducible COBOL source context for semantic judging.

Uses fixed source ranges and verified reference evidence.
Does not call Gemini or modify frozen research artifacts.
"""

from pathlib import Path

from source_context_loader import load_source_lines


TX01_COMPLEX_CONTEXT = {
    "INT-TX01-001": [(133, 174), (214, 223)],
    "INT-TX01-002": [(177, 213)],
    "INT-TX01-003": [(177, 213)],
    "BR-TX01-007": [(133, 174)],
}


def merge_ranges(ranges):
    """Merge overlapping or adjacent source ranges."""

    merged = []

    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(
                merged[-1][1], end
            )

    return [tuple(item) for item in merged]


def build_source_context(
    gold_rule,
    source_file,
    padding=5
):
    """
    Build source context using reference evidence.

    Additional fixed ranges cover known multi-paragraph
    banking operations.
    """

    source_file = Path(source_file)
    evidence = gold_rule.get("evidence", [])

    ranges = []

    for entry in evidence:
        if entry.get("file") != source_file.name:
            continue

        line = int(entry["line"])

        ranges.append((
            max(1, line - padding),
            line + padding
        ))

    ranges.extend(
        TX01_COMPLEX_CONTEXT.get(
            gold_rule["id"], []
        )
    )

    merged = merge_ranges(ranges)

    return {
        "file": source_file.name,
        "reference_id": gold_rule["id"],
        "ranges": [
            load_source_lines(source_file, start, end)
            for start, end in merged
        ],
        "context_strategy": "verified_evidence_plus_fixed_ranges",
    }
