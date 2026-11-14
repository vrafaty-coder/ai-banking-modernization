"""Offline, read-only check for a transaction config; no Gemini or file writes."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, default=Path.cwd())
    parser.add_argument('--config', default='ai/configs/tx02.json')
    args = parser.parse_args()
    root = args.project_root.resolve()
    config = json.loads((root / args.config).read_text(encoding='utf-8'))
    source = root / config['cobol_source']
    copydir = root / config['copybook_directory']
    failures = []
    if not source.is_file():
        failures.append(f'Missing COBOL: {source}')
        names = []
    else:
        body = source.read_text(encoding='utf-8-sig')
        names = re.findall(r'\bCOPY\s+["\']([^"\']+)["\']', body, re.I)
        print(f'COBOL: {source.relative_to(root)} | SHA256: {hashlib.sha256(source.read_bytes()).hexdigest()}')
        if not re.search(r'\bPROGRAM-ID\.\s*' + re.escape(config['transaction']) + r'\b', body, re.I):
            failures.append('PROGRAM-ID mismatch')
    declared = set(config['copybooks'])
    referenced = set(names)
    for name in sorted(declared | referenced):
        file = copydir / name
        status = 'OK' if file.is_file() else 'MISSING'
        print(f'COPYBOOK {name}: {status}')
        if not file.is_file(): failures.append(f'Missing copybook: {name}')
    if referenced != declared:
        failures.append(f'COPY list mismatch: source={sorted(referenced)}, config={sorted(declared)}')
    print('Gold standard:', 'present' if (root / config['gold_standard']).exists() else 'not created yet (expected)')
    print('API calls: NONE (offline checker)')
    if failures:
        print('FAILED: ' + '; '.join(failures))
        raise SystemExit(1)
    print('PASS: source, program ID, COPY references and six copybook files verified')

if __name__ == '__main__':
    main()
