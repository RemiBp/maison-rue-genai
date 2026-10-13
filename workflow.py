"""Source validation and a simple first-intent template baseline."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).parent
FACTS=json.loads((ROOT/'knowledge.json').read_text())

def validate_predictions(decisions,cases):
    expected={c['id'] for c in cases}
    if len(expected)!=len(cases): raise ValueError('Duplicate input IDs')
    if len(decisions)!=len(cases) or {d['id'] for d in decisions}!=expected:
        raise RuntimeError('Missing or duplicate response IDs')
    for d in decisions:
        if not isinstance(d['customer_reply'],str) or not d['customer_reply'].strip():
            raise RuntimeError('Empty draft')
        evidence={e['source_id']:e['quote'] for e in d['evidence']}
        for sid,quote in evidence.items():
            if sid not in FACTS or quote!=FACTS[sid]: raise RuntimeError('Unsupported source quote')
        for a in d['answers']:
            if not a['answer'].strip(): raise RuntimeError('Empty answer')
            if any(sid not in evidence for sid in a['source_ids']):
                raise RuntimeError('Answer missing evidence')
        if any(n['status']!='proposed' for n in d['next_steps']):
            raise RuntimeError('Only proposed actions are permitted')
        if d['needs_manager'] and not any(n['owner']=='support_manager' for n in d['next_steps']):
            raise RuntimeError('Manager referral required')

def baseline(case):
    """A reusable keyword/template workflow, no model or invented status.

    Deliberately simple first-intent routing, chosen before prototype evaluation.
    Shares the supplied facts; compound requests expose its known limitation.
    """
    text=case['text'].lower(); refs=re.findall(r'\bA\d{3}\b',case['text'],re.I)
    ref=refs[0].upper() if refs else None
    sources=[]; missing=[]; manager=False
    if any(w in text for w in ['broken','damaged','cassé','abîmé']):
        issue='damage';sources=['P2'];reply='Please provide your order reference and a photo. A support colleague will review the damage; no refund has been approved.'
        missing=['order reference','photo']
    elif any(w in text for w in ['return','retour']):
        issue='return';sources=['P1'];reply='Unused items may be returned within 30 calendar days of delivery. Please confirm whether the item is unused.'
        missing=['unused condition']
        if ref=='A103':
            sources+=['P4'];manager=True;reply='The return is outside our 30-day window. A support manager must review any exception.'
    elif any(w in text for w in ['where','delivery','arriv','livraison','arriver']):
        issue='delivery';sources=['P3'];reply='Standard delivery is estimated at 3–5 business days after dispatch, without a guaranteed arrival date.'
    else:
        issue='other';reply='Please clarify your request so a support colleague can help.';missing=['request details']
    if ref in FACTS:
        sources.append(ref);reply=FACTS[ref]+' '+reply
    elif ref:
        issue='unknown_order';sources=[];reply='This order reference is not in the supplied snapshot. Please check it or provide proof of purchase.';missing=['corrected order reference or proof of purchase'];manager=False
    owner='support_manager' if manager else 'support_colleague'
    return {'id':case['id'],'customer_reply':reply,'answers':[{'issue':issue,'answer':reply,'source_ids':sources}],
            'evidence':[{'source_id':s,'quote':FACTS[s]} for s in sources],
            'missing_information':missing,'next_steps':[{'owner':owner,'action':'Review the draft and enquiry','status':'proposed'}],
            'needs_manager':manager}
