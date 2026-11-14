from pathlib import Path
import re

# Locate the target COBOL program
ROOT = Path(__file__).resolve().parent.parent
program = "TX01"
code = (ROOT / "cobol" / "programs" / f"{program}.cbl").read_text(encoding="utf-8")

# Split the procedure into named paragraphs
pattern = r"(?m)^[ \t]*([A-Z][A-Z0-9-]*)\.[ \t]*$"
matches = list(re.finditer(pattern, code))
chunks = {
    match.group(1): code[match.start():matches[i + 1].start() if i + 1 < len(matches) else len(code)].strip()
    for i, match in enumerate(matches)
}

# Retrieve the paragraph and its direct callers
def retrieve(name):
    name = name.upper()
    if name not in chunks:
        raise ValueError(f"Unknown paragraph: {name}")
    return {
        key: value for key, value in chunks.items()
        if key == name or re.search(rf"\bPERFORM\s+{re.escape(name)}\b", value, re.IGNORECASE)
    }

# Find and read copybooks referenced by COPY statements
copy_names = dict.fromkeys(re.findall(r"\bCOPY\s+['\"]?([A-Z0-9-]+)", code, re.IGNORECASE))
copy_files = [ROOT / "cobol" / "copybooks" / f"{name}.cpy" for name in copy_names]

# Build a separate context for each COBOL paragraph
rag_contexts = {}

for name in chunks:
    # Retrieve the paragraph and its callers
    selected = retrieve(name)

    # Combine retrieved paragraphs
    context = "\n\n".join(
        f"PARAGRAPH: {key}\n{value}"
        for key, value in selected.items()
    )

    # Add copybooks referenced by the COBOL program
    for file in copy_files:
        context += f"\n\nCOPYBOOK: {file.name}\n"
        context += file.read_text(encoding="utf-8")

    rag_contexts[name] = context

# Display context sizes
# Show the paragraphs included in each retrieval
# Run diagnostics only when this file is executed directly
if __name__ == "__main__":
    for name, context in rag_contexts.items():
        print(f"{name}: {len(context)} characters")

    for name in chunks:
        print(f"{name} -> {list(retrieve(name))}")