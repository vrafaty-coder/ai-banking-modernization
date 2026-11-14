"""Shared TX extraction runner; offline by default. Python 3.10+."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

PROMPT = """You are analyzing a legacy COBOL banking program.

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
SCHEMA = {"type":"ARRAY", "items":{"type":"OBJECT","properties":{
    "rule_description":{"type":"STRING"},"condition":{"type":"STRING"},
    "action":{"type":"STRING"},"evidence":{"type":"STRING"},
    "category":{"type":"STRING","enum":["BUSINESS","TECHNICAL","INTEGRITY"]}},
    "required":["rule_description","condition","action","evidence","category"]}}
REQUIRED = {"rule_description","condition","action","evidence","category"}

def build(project, config, mode):
    tx = config['program'].upper()
    src = project / config['cobol_file']
    code = src.read_text(encoding='utf-8')
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    copies = {}
    for name in config['copybooks']:
        p = project / config['copybook_dir'] / name
        copies[name] = p.read_text(encoding='utf-8')
    found = set(re.findall(r'\bCOPY\s+[\'\"]?([A-Z0-9-]+)', code, re.I))
    expected = {Path(x).stem.upper() for x in copies}
    if found != expected:
        raise ValueError(f'COPY mismatch: source={sorted(found)}, config={sorted(expected)}')
    if mode == 'llm':
        # Same source inventory as RAG; no retrieval, one full-context prompt.
        full_context = PROMPT + '\nCOBOL SOURCE:\n' + code
        for filename, contents in copies.items():
            full_context += f'\n\nCOPYBOOK: {filename}\n{contents}'
        return tx, sha, [('FULL_PROGRAM', full_context)]
    # Matches original rag_retriever.py paragraph splitting and direct caller retrieval.
    pattern = r'(?m)^[ \t]*([A-Z][A-Z0-9-]*)\.[ \t]*$'
    matches = list(re.finditer(pattern, code))
    chunks = {m.group(1): code[m.start():matches[i+1].start() if i+1<len(matches) else len(code)].strip()
              for i,m in enumerate(matches)}
    if not chunks:
        raise ValueError('No COBOL paragraph boundaries found; inspect source before RAG execution')
    prompts = []
    for name in chunks:
        selected = {k:v for k,v in chunks.items() if k==name or re.search(r'\bPERFORM\s+'+re.escape(name)+r'\b',v,re.I)}
        context = '\n\n'.join(f'PARAGRAPH: {k}\n{v}' for k,v in selected.items())
        for filename, contents in copies.items():
            context += f'\n\nCOPYBOOK: {filename}\n{contents}'
        scope = (f'Extract rules implemented in {name}.\n'
                 'Use other retrieved paragraphs only to understand calls and outcomes.\n'
                 'Do not report unrelated rules from those paragraphs.\n')
        prompts.append((name, PROMPT + '\n' + scope + '\nCOBOL SOURCE:\n' + context))
    return tx, sha, prompts

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root',type=Path,default=Path('.'))
    ap.add_argument('--config',type=Path,required=True)
    ap.add_argument('--mode',choices=['llm','rag'],required=True)
    ap.add_argument('--execute',action='store_true',help='Requires GEMINI_API_KEY; makes real API calls')
    args=ap.parse_args()
    root=args.project_root.resolve()
    cfgpath=args.config if args.config.is_absolute() else root/args.config
    cfg=json.loads(cfgpath.read_text(encoding='utf-8'))
    tx, sha, prompts=build(root,cfg,args.mode)
    if cfg.get('source_sha256') and sha.lower()!=cfg['source_sha256'].lower():
        raise ValueError('COBOL SHA256 differs from frozen config')
    out=root / cfg['output_dir'] / args.mode
    print(f'Program: {tx} | mode: {args.mode} | SHA256: {sha}')
    print(f'Copybooks: {len(cfg["copybooks"])} | contexts: {len(prompts)}')
    print(f'Output directory: {out}')
    for name,prompt in prompts:
        print(f'  {name}: {len(prompt)} chars')
    if not args.execute:
        print('DRY RUN PASS — no API calls, no output files written')
        return
    if not os.environ.get('GEMINI_API_KEY'):
        raise RuntimeError('GEMINI_API_KEY is required for --execute')
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f'Output directory not empty: {out}; never overwrite existing runs')
    from google import genai
    from google.genai import types
    import ssl, httpx
    sslctx=ssl.create_default_context()
    sslctx.minimum_version=ssl.TLSVersion.TLSv1_2
    sslctx.maximum_version=ssl.TLSVersion.TLSv1_2
    http_client=httpx.Client(verify=sslctx,timeout=60.0)
    client=genai.Client(api_key=os.environ['GEMINI_API_KEY'],http_options=types.HttpOptions(httpx_client=http_client))
    out.mkdir(parents=True,exist_ok=False)
    (out/'manifest.json').write_text(json.dumps({'program':tx,'mode':args.mode,'source_sha256':sha,'model':cfg['model'],'temperature':0,'contexts':[n for n,_ in prompts]},indent=2),encoding='utf-8')
    for name,prompt in prompts:
        response=client.models.generate_content(model=cfg['model'],contents=prompt,
            config=types.GenerateContentConfig(temperature=0,response_mime_type='application/json',response_schema=SCHEMA))
        stem=name.lower().replace('-','_')
        (out/f'{stem}_prompt.txt').write_text(prompt,encoding='utf-8')
        (out/f'{stem}_raw.txt').write_text(response.text or '',encoding='utf-8')
        rules=json.loads(response.text)
        if not isinstance(rules,list) or any(not isinstance(r,dict) or not REQUIRED<=r.keys() for r in rules):
            raise ValueError(f'Invalid JSON for {name}; raw output preserved')
        (out/f'{stem}_rules.json').write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'{name}: {len(rules)} rules saved')
    print('Completed; no deduplication or evaluation performed')
if __name__=='__main__': main()
