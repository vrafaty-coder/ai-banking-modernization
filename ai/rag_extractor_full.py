"""Extract COBOL rules from four retrieved contexts using Gemini."""
import json
import os
import ssl
from pathlib import Path

import httpx
from google import genai
from google.genai import types
from rag_retriever import rag_contexts

ROOT = Path(__file__).resolve().parent.parent
PROGRAM = "TX01"

# Preserve the TLS settings used in the original extractor.
ssl_context = ssl.create_default_context()
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
http_client = httpx.Client(verify=ssl_context, timeout=60.0)
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(httpx_client=http_client),
)

# Keep the original LLM-only output schema.
schema = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "rule_description": {"type": "STRING"},
            "condition": {"type": "STRING"},
            "action": {"type": "STRING"},
            "evidence": {"type": "STRING"},
            "category": {"type": "STRING", "enum": ["BUSINESS", "TECHNICAL", "INTEGRITY"]},
        },
        "required": ["rule_description", "condition", "action", "evidence", "category"],
    },
}

# Use the original extraction instructions for every context.
BASE_PROMPT = """You are analyzing a legacy COBOL banking program.

Extract the business rules explicitly implemented in the source code.

For each rule, provide:
1. Rule description
2. Condition
3. Action or outcome
4. Evidence from the COBOL source

Do not invent rules.
Do not use external banking assumptions.
If a rule cannot be verified from the code, do not include it.

Return the extracted rules as valid JSON, not Markdown.

Classify each extracted rule into exactly one category:

BUSINESS: Banking policies, transaction conditions,
account eligibility, and financial limits.

TECHNICAL: File operations, system errors,
and technical exception handling.

INTEGRITY: Rules that preserve transaction consistency,
account balances, and journal integrity.

Do not invent rules. Base each classification
on the COBOL source evidence.
"""

for paragraph, context in rag_contexts.items():
    # MAIN provides caller context for other paragraphs, not extra rules.
    scope = (f"Extract rules implemented in {paragraph}.\n"
             "Use other retrieved paragraphs only to understand calls and outcomes.\n"
             "Do not report unrelated rules from those paragraphs.\n")
    prompt = f"{BASE_PROMPT}\n{scope}\nCOBOL SOURCE:\n{context}"
    print(f"Extracting {paragraph}...", flush=True)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    # Save the original Gemini response for inspection
    if paragraph == "MAIN":
        (ROOT / "ai" / "tx01_rag_main_response_raw.txt").write_text(
            response.text, encoding="utf-8"
        )

    # Check whether Gemini finished generating its response
    print("Finish reason:", response.candidates[0].finish_reason)
    print("Response length:", len(response.text or ""))

    rules = json.loads(response.text)
    # Show the JSON structure returned by Gemini
    print("Response type:", type(rules).__name__)

    if isinstance(rules, list):
        print("Rule fields:", [list(r.keys()) for r in rules if isinstance(r, dict)])
    else:
        print("Response:", str(rules)[:1000])


    if not isinstance(rules, list) or any(
        not isinstance(rule, dict) or
        not {"rule_description", "condition", "action", "evidence", "category"} <= rule.keys()
        for rule in rules
    ):
        raise ValueError(f"Invalid rule JSON for {paragraph}")

    # Save each response immediately; do not merge or deduplicate yet.
    output = ROOT / "ai" / f"{PROGRAM.lower()}_rag_{paragraph.lower().replace('-', '_')}.json"
    output.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{paragraph}: {len(rules)} rules -> {output.name}", flush=True)

print("Finished. Outputs are separate; no deduplication or evaluation yet.")
