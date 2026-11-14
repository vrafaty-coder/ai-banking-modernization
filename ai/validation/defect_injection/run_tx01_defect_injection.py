from pathlib import Path
import tempfile, subprocess, csv, json, zipfile, re
ROOT=Path('/mnt/data')
base=(ROOT/'Tx01Service.java').read_text()
mutations={
 'M01_zero_amount_accepted':('request.amount() == 0','request.amount() < 0','Zero amount validation disabled','S02'),
 'M02_blocked_account_accepted':('"B".equals(account.status())','"NEVER_BLOCKED".equals(account.status())','Blocked account check disabled','S04'),
 'M03_overflow_accepted':('newBalance > 999999999999999L','newBalance > Long.MAX_VALUE','Balance overflow check disabled','S07'),
 'M04_wrong_journal_credit_account':('request.accountNumber(),\n                "",\n                request.amount()','"WRONGACCOUNT",\n                "",\n                request.amount()','Journal credited to wrong account','S01'),
 'M05_no_rollback':('if (rollbackAccount != null && !accountRepository.hasUpdateError())','if (false && rollbackAccount != null && !accountRepository.hasUpdateError())','Rollback disabled','S10'),
}
files=['Tx01Service.java','Tx01Request.java','Tx01Response.java','AccountRecord.java','JournalRecord.java','AccountRepository.java','JournalRepository.java','Tx01ValidationGateV3.java']
results=[]; details={}
with tempfile.TemporaryDirectory() as td:
 for mid in ['BASELINE']+list(mutations):
  work=Path(td)/mid; src=work/'src'/'banking'/'tx01';src.mkdir(parents=True)
  for name in files:(src/name).write_bytes((ROOT/name).read_bytes())
  if mid!='BASELINE':
   old,new,desc,target=mutations[mid]
   if base.count(old)!=1:raise RuntimeError(f'{mid} match count {base.count(old)}')
   (src/'Tx01Service.java').write_text(base.replace(old,new,1))
  comp=subprocess.run(['javac','-d',str(work/'classes'),*[str(src/name) for name in files]],capture_output=True,text=True)
  if comp.returncode:raise RuntimeError(mid+' compilation failed: '+comp.stderr)
  run=subprocess.run(['java','-cp',str(work/'classes'),'banking.tx01.Tx01ValidationGateV3'],cwd=work,capture_output=True,text=True)
  if run.returncode:raise RuntimeError(mid+' runtime failed: '+run.stderr)
  data=json.loads((work/'tx01_validation_gate_v3_results.json').read_text())
  failed=sorted(set(x['scenario_id'] for x in data['rows'] if x['result']=='FAIL'))
  ne=sorted(set(x['scenario_id'] for x in data['rows'] if x['result']=='NOT_EVALUABLE'))
  results.append({'variant':mid,'description':'Original unmodified Gemini Java' if mid=='BASELINE' else mutations[mid][2], 'target_scenario':'' if mid=='BASELINE' else mutations[mid][3], 'failed_scenarios':';'.join(failed),'not_evaluable_scenarios':';'.join(ne),'detected':'BASELINE' if mid=='BASELINE' else ('YES' if mutations[mid][3] in failed else 'NO'),'total_failed_scenarios':len(failed)})
  details[mid]={'summary':data['summary'],'failed_rows':[x for x in data['rows'] if x['result']=='FAIL'],'stdout':run.stdout}
with (ROOT/'tx01_defect_injection_results.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
(ROOT/'tx01_defect_injection_results.json').write_text(json.dumps({'method':'Each mutant is compiled and tested separately; original Gemini Tx01Service.java is never modified. V3 source-derived oracle, not live COBOL execution.','mutants':results,'details':details},indent=2))
readme='''TX01 Controlled Defect Injection — Experimental Run\n\nRun: python run_tx01_defect_injection.py\nRequires Java JDK 17+ and Python 3.\nInput Java files and Tx01ValidationGateV3.java must be in the same directory as the Python runner.\n\nThis experiment tests whether V3 detects FIVE deliberately introduced defects, each in a temporary compiled copy. The original generated Java is never edited.\nDetection is defined as the targeted scenario receiving FAIL in at least one V3 dimension.\nResults are source-oracle based; no executable COBOL reference was run.\nThe BUSINESS_RULE dimension in V3 is a composite, not independent evidence.\nNOT_EVALUABLE scenarios are excluded from detection counts.\nThe test suite may have additional blind spots; these five mutants do not prove comprehensive mutation adequacy.\n'''
(ROOT/'tx01_defect_injection_README.txt').write_text(readme)
with zipfile.ZipFile(ROOT/'tx01_defect_injection_package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['run_tx01_defect_injection.py','tx01_defect_injection_results.csv','tx01_defect_injection_results.json','tx01_defect_injection_README.txt']+files:
  z.write(ROOT/name,arcname=name)
for r in results:print(r)
