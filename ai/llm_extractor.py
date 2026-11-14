
import os
from pathlib import Path
from google import genai

# 1. Locate the project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 2. Read TX01 COBOL source
cobol_file = PROJECT_ROOT / "cobol" / "programs" / "TX01.cbl"
cobol_code = cobol_file.read_text(encoding="utf-8")

print(f"Loaded {cobol_file.name}: {len(cobol_code)} characters")

# 3. Build the extraction prompt
prompt = f"""
You are analyzing a legacy COBOL banking program.

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

COBOL SOURCE:
{cobol_code}
"""

# 4. Connect to Gemini
#client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

import ssl
import httpx
from google.genai import types

ssl_context = ssl.create_default_context()
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2

http_client = httpx.Client(
    verify=ssl_context,
    timeout=60.0
)

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        httpx_client=http_client
    )
)


# 5. Extract business rules
#response = client.models.generate_content(
#    model="gemini-3.5-flash-lite",
#    contents=prompt,
#)

from google.genai import types

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0,
        response_mime_type="application/json",
        response_schema={
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "rule_description": {"type": "STRING"},
                    "condition": {"type": "STRING"},
                    "action": {"type": "STRING"},
                    "evidence": {"type": "STRING"},
                    "category": {"type": "STRING","enum": ["BUSINESS", "TECHNICAL", "INTEGRITY"]}
                },
                "required": [
                    "rule_description",
                    "condition",
                    "action",
                    "evidence"
                ]
            }
        }
    )
)

# 6. Save the raw AI output
#output_file = PROJECT_ROOT / "ai" / "tx01_llm_raw.txt"
#output_file.write_text(response.text, encoding="utf-8")

import json

#print("Raw Gemini response:")
#print(response.text[:1500])

# Convert the LLM response into Python objects
rules = json.loads(response.text)

# Check the structure
if not isinstance(rules, list):
    raise ValueError("Expected a list of business rules")

required_fields = {
    "rule_description",
    "condition",
    "action",
    "evidence",
    "category"
}

for index, rule in enumerate(rules, start=1):
    if not isinstance(rule, dict):
        raise ValueError(f"Rule {index} is not an object")

    missing = required_fields - rule.keys()
    if missing:
        raise ValueError(
            f"Rule {index} is missing fields: {missing}"
        )

# rule category
from collections import Counter

categories = Counter(rule["category"] for rule in rules)

print("\nRules by category:")
for category, count in sorted(categories.items()):
    print(f"{category}: {count}")


# Save validated JSON
#output_file = PROJECT_ROOT / "ai" / "tx01_llm_run2.json"
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

output_file = (
    PROJECT_ROOT / "ai" / f"tx01_llm_{timestamp}.json"
)


output_file.write_text(
    json.dumps(rules, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Extracted rules: {len(rules)}")
print(f"Valid JSON saved to: {output_file}")

print(f"Extraction completed. Saved to: {output_file}")
