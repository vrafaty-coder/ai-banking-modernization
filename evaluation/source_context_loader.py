
"""
Load verified COBOL source context for semantic judging.

Source files are read directly from the project.
Model-generated evidence is never treated as source truth.
"""

from pathlib import Path


def load_source_lines(file_path, start_line, end_line):
    """
    Read an inclusive range of lines from a source file.
    Preserve original line numbers for traceability.
    """

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Source file not found: {file_path}"
        )

    if start_line < 1 or end_line < start_line:
        raise ValueError("Invalid source line range")

    lines = file_path.read_text(
        encoding="utf-8"
    ).splitlines()

    if end_line > len(lines):
        raise ValueError(
            f"Requested line {end_line} exceeds "
            f"file length {len(lines)}"
        )

    return {
        "file": file_path.name,
        "start_line": start_line,
        "end_line": end_line,
        "lines": [
            {
                "line": number,
                "text": lines[number - 1]
            }
            for number in range(
                start_line,
                end_line + 1
            )
        ]
    }
