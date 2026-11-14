"""Generate TX01 Java implementation once; preserve raw model output."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
MODEL = "gemini-3.5-flash-lite"
SOURCE = ROOT / "cobol/programs/TX01.cbl"
COPY_DIR = ROOT / "cobol/copybooks"
RULES = ROOT / "ai/tx01_llm_rules.json"
JAVA_DIR = ROOT / "java/src/main/java/banking/tx01"
OUT_DIR = ROOT / "ai/java_generation/tx01_llm_only_v1"
COPYBOOKS = ["ACCOUNT-RECORD.cpy", "JOURNAL-RECORD.cpy", "COMMON-RECEIVE.cpy", "TX01-RECEIVE.cpy", "COMMON-RESPONSE.cpy", "TX01-RESPONSE.cpy"]
MODELS = ["Tx01Request.java", "Tx01Response.java", "AccountRecord.java", "JournalRecord.java"]

inputs = {"TX01.cbl": SOURCE.read_text(encoding="utf-8"),
          "tx01_llm_rules.json": RULES.read_text(encoding="utf-8")}
for name in COPYBOOKS:
    inputs[name] = (COPY_DIR / name).read_text(encoding="utf-8")
for name in MODELS:
    inputs[name] = (JAVA_DIR / name).read_text(encoding="utf-8")

prompt = """You are implementing a Java 17 banking deposit service to reproduce the COBOL TX01 program's OBSERVABLE behavior.
Use the supplied COBOL source and copybooks as the authority for actual behavior. The supplied LLM-only rules are an auxiliary extraction artifact; do not assume they are complete or correct.
Use the four provided Java records exactly as defined; do not change them.
Implement Tx01Service.java and any minimal repository interfaces needed for deterministic in-memory simulation. Output complete Java source files, not explanations.
Preserve error codes/messages, status codes, balance limits, journal stamp construction and collision handling, operation order, early returns, and rollback behavior including its limitations. Do not add business validations absent from COBOL.
Model file open/read/rewrite/write failures as injectable repository outcomes so tests can cover failure paths. Avoid using database or filesystem dependencies. Java long is sufficient for PIC 9(15), but enforce the COBOL 15-digit maximum. Preserve fixed-width numeric fields and leading zeros in the stamp.
Return ONLY a JSON object with a `files` array of objects containing `name` (filename only) and `content` (complete Java source). No Markdown fences. Do not modify the supplied records.

INPUT MATERIALS:
""" + "\n\n".join(f"===== {name} =====\n{value}" for name, value in inputs.items())

OUT_DIR.mkdir(parents=True, exist_ok=True)
if (OUT_DIR / "response_raw.txt").exists():
    raise SystemExit("Existing raw output found. Refusing to overwrite the first run.")
(OUT_DIR / "prompt.txt").write_text(prompt, encoding="utf-8")
manifest = {"model": MODEL, "temperature": 0, "utc_started": datetime.now(timezone.utc).isoformat(),
            "inputs_sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in inputs.items()},
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "note": "LLM-only rule-assisted generation; COBOL and copybooks also supplied. Gold Standard excluded."}
(OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(model=MODEL, contents=prompt,
    config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json"))
raw = response.text or ""
(OUT_DIR / "response_raw.txt").write_text(raw, encoding="utf-8")
manifest["finish_reason"] = str(response.candidates[0].finish_reason) if response.candidates else None
manifest["utc_finished"] = datetime.now(timezone.utc).isoformat()
(OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

# Parse into separate files, without changing the generated content.
payload = json.loads(raw)
for item in payload["files"]:
    name = item["name"]
    if not name.endswith(".java") or Path(name).name != name or name in MODELS:
        raise ValueError(f"Unexpected generated filename: {name}")
    (OUT_DIR / name).write_text(item["content"], encoding="utf-8")
print("Saved raw response and generated Java sources to", OUT_DIR)
