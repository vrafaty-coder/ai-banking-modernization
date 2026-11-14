"""One-shot Gemini Java generation for TX02, using the frozen prepared prompt.
Run from project root: python ai/generate_tx02_java.py
Requires: pip install google-genai ; GEMINI_API_KEY environment variable.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'ai' / 'java_generation' / 'tx02_rag_v1'
MODEL = 'gemini-3.5-flash-lite'
PROMPT_PATH = OUT_DIR / 'prompt.txt'
PREPARED_MANIFEST = OUT_DIR / 'manifest.json'
RUN_MANIFEST = OUT_DIR / 'generation_run_manifest.json'
RAW_PATH = OUT_DIR / 'response_raw.txt'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    prompt_bytes = PROMPT_PATH.read_bytes()
    prepared = json.loads(PREPARED_MANIFEST.read_text(encoding='utf-8'))
    expected_prompt_hash = prepared.get('prompt_sha256')
    if not expected_prompt_hash or sha256(prompt_bytes) != expected_prompt_hash:
        raise SystemExit('Prompt hash mismatch: do not run until the frozen prompt is restored.')
    for filename, expected_hash in prepared.get('input_sha256', {}).items():
        actual_path = OUT_DIR / filename
        if not actual_path.is_file() or sha256(actual_path.read_bytes()) != expected_hash:
            raise SystemExit(f'Frozen input missing or modified: {filename}')
    if prepared.get('model_target') != MODEL or prepared.get('temperature_target') != 0:
        raise SystemExit('Model/temperature differs from prepared experiment manifest.')
    if RAW_PATH.exists() or RUN_MANIFEST.exists():
        raise SystemExit('An existing generation record was found; refusing to overwrite it.')
    if not os.environ.get('GEMINI_API_KEY'):
        raise SystemExit('GEMINI_API_KEY is not set in this terminal.')

    prompt = prompt_bytes.decode('utf-8')
    run = {
        'experiment': 'TX02 Withdrawal LLM+RAG Java generation',
        'model': MODEL, 'temperature': 0,
        'prompt_sha256': sha256(prompt_bytes),
        'prepared_manifest_sha256': sha256(PREPARED_MANIFEST.read_bytes()),
        'utc_started': datetime.now(timezone.utc).isoformat(),
        'status': 'STARTED',
        'gold_in_prompt': False,
        'human_validation_in_prompt': False,
    }
    RUN_MANIFEST.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding='utf-8')
    try:
        client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
        response = client.models.generate_content(
            model=MODEL, contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0, response_mime_type='application/json'))
        raw = response.text or ''
        RAW_PATH.write_text(raw, encoding='utf-8')
        run['response_sha256'] = sha256(raw.encode('utf-8'))
        run['finish_reason'] = str(response.candidates[0].finish_reason) if response.candidates else None
        run['utc_finished'] = datetime.now(timezone.utc).isoformat()
        run['status'] = 'RESPONSE_SAVED'
        RUN_MANIFEST.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding='utf-8')
        payload = json.loads(raw)
        files = payload['files']
        if not isinstance(files, list) or not files:
            raise ValueError('Expected a nonempty files array.')
        reserved = {'AccountRecord.java', 'JournalRecord.java', 'Tx01Request.java', 'Tx01Response.java'}
        seen = set()
        for item in files:
            name, content = item['name'], item['content']
            if (not isinstance(name, str) or not name.endswith('.java')
                    or Path(name).name != name or name in reserved or name in seen
                    or not isinstance(content, str)):
                raise ValueError(f'Unexpected generated file: {name!r}')
            if (OUT_DIR / name).exists():
                raise ValueError(f'Will not overwrite existing file: {name}')
            seen.add(name)
        for item in files:
            (OUT_DIR / item['name']).write_text(item['content'], encoding='utf-8')
        run['generated_files_sha256'] = {item['name']: sha256(item['content'].encode('utf-8')) for item in files}
        run['status'] = 'SOURCES_SAVED'
        RUN_MANIFEST.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding='utf-8')
        print('Saved raw response and Java files to:', OUT_DIR)
        print('Files:', ', '.join(sorted(seen)))
    except Exception as exc:
        run['status'] = 'FAILED_AFTER_START'
        run['error_type'] = type(exc).__name__
        run['error_message'] = str(exc)
        run['utc_finished'] = datetime.now(timezone.utc).isoformat()
        RUN_MANIFEST.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
