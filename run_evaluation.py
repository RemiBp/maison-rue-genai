"""Frozen rubric and identical inputs for baseline and assistant; human audit separate."""
import hashlib
import json
import time
from datetime import datetime,timezone
from pathlib import Path
from workflow import baseline,validate_predictions
from model import predict
ROOT=Path(__file__).parent
def structural_score(d,expected):
    issues={a['issue'] for a in d['answers']}
    sources={e['source_id'] for e in d['evidence']}
    checks={'all_topics':set(expected['issues'])<=issues,
            'required_evidence':set(expected['sources'])<=sources,
            'manager_routing':d['needs_manager']==expected['manager']}
    return {'checks':checks,'pass':all(checks.values())}
def run():
    cases=json.loads((ROOT/'cases.json').read_text())
    expected=json.loads((ROOT/'expected.json').read_text())
    start=time.perf_counter(); rules=[baseline(c) for c in cases]; duration=time.perf_counter()-start
    validate_predictions(rules,cases)
    inference=predict(cases)
    predictions={d['id']:d for d in inference['decisions']}
    rows=[{'id':c['id'],'input':c['text'],'expected':expected[c['id']],
           'baseline':rules[i],'prototype':predictions[c['id']],
           'baseline_structural':structural_score(rules[i],expected[c['id']]),
           'prototype_structural':structural_score(predictions[c['id']],expected[c['id']])}
          for i,c in enumerate(cases)]
    report={'run_at':datetime.now(timezone.utc).isoformat(),'rows':rows,
            'hashes':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['prompt.txt','knowledge.json','cases.json','expected.json']},
            'inference':inference,'baseline_seconds':duration,'cost_usd':None,
            'note':'Structural scores check topics/evidence/routing only. Inspect customer replies against expected behaviour in a separate human audit. Synthetic cases, no productivity claim.'}
    (ROOT/'evaluation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('Structural baseline:',sum(r['baseline_structural']['pass'] for r in rows),'/',len(rows))
    print('Structural prototype:',sum(r['prototype_structural']['pass'] for r in rows),'/',len(rows))
    print('Batch seconds:',round(inference['elapsed_seconds'],1))
if __name__=='__main__':run()
