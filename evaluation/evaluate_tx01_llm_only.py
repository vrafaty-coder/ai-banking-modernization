import csv,json
from pathlib import Path
P=Path(__file__).resolve().parent
reference=json.loads((P/'tx01_gold_standard_v1.0.json').read_text(encoding='utf-8'))
ref={r['id']:r for r in reference['rules']}
# Human-authored semantic mapping, 1-indexed Gemini output items to reference rule IDs.
# This mapping must be reviewed and frozen before reporting definitive paper metrics.
mappings={
 'tx01_llm_rules.json':[['BR-TX01-001'],['TECH-TX01-001'],['TECH-TX01-002'],['BR-TX01-002'],['TECH-TX01-003'],['BR-TX01-003'],['BR-TX01-004'],['BR-TX01-005'],['BR-TX01-006'],['TECH-TX01-004'],['INT-TX01-001'],['INT-TX01-003'],['TECH-TX01-005'],['INT-TX01-001']],
 'tx01_llm_20261109_123124_492698.json':[['BR-TX01-001'],['TECH-TX01-001'],['TECH-TX01-002'],['BR-TX01-002'],['BR-TX01-003'],['BR-TX01-004'],['BR-TX01-005'],['BR-TX01-006'],['TECH-TX01-004'],['INT-TX01-001'],['INT-TX01-003'],['INT-TX01-001']],
 'tx01_llm_run1.json':[['BR-TX01-001'],['TECH-TX01-001'],['TECH-TX01-002'],['BR-TX01-002'],['BR-TX01-003','BR-TX01-004','BR-TX01-005'],['BR-TX01-006'],['INT-TX01-001']]
}
rows=[]; summary=[]
for filename, mapping in mappings.items():
 output=json.loads((P/filename).read_text(encoding='utf-8'))
 assert len(output)==len(mapping)
 seen=set()
 for i,(item,ids) in enumerate(zip(output,mapping),1):
  assert all(x in ref for x in ids)
  duplicate=bool(ids and set(ids).issubset(seen))
  seen.update(ids)
  rows.append({'file':filename,'item':i,'model_category':item['category'],'model_rule':item['rule_description'],'matched_reference_ids':';'.join(ids),'duplicate_only':duplicate,'category_mismatch':';'.join(x for x in ids if item['category']!=ref[x]['category'])})
 for cat in ('BUSINESS','INTEGRITY','TECHNICAL'):
  ids={x for x,r in ref.items() if r['category']==cat}
  summary.append({'file':filename,'category':cat,'reference_total':len(ids),'matched_reference':len(seen&ids),'coverage_recall':round(len(seen&ids)/len(ids),4),'missing_ids':';'.join(sorted(ids-seen))})
 summary.append({'file':filename,'category':'ALL','reference_total':len(ref),'matched_reference':len(seen),'coverage_recall':round(len(seen)/len(ref),4),'missing_ids':';'.join(sorted(set(ref)-seen))})
for name,data in [('tx01_llm_semantic_mapping_draft.csv',rows),('tx01_llm_coverage_draft.csv',summary)]:
 with (P/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
print('Draft semantic mapping and reference coverage created.')
for s in summary:
 if s['category']=='ALL':print(s)
