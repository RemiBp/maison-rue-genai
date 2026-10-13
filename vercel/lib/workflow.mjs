import {facts} from './data.mjs';
export function baseline(text){
 const refs=text.match(/\bA\d{3}\b/gi)||[],ref=refs[0]?.toUpperCase(),t=text.toLowerCase();
 let issue,sources=[],missing=[],manager=false,reply;
 if(['broken','damaged','cassé','abîmé'].some(w=>t.includes(w))){issue='damage';sources=['P2'];reply='Please provide your order reference and a photo. A support colleague will review the damage; no refund has been approved.';missing=['order reference','photo'];}
 else if(['return','retour'].some(w=>t.includes(w))){issue='return';sources=['P1'];reply='Unused items may be returned within 30 calendar days of delivery. Please confirm whether the item is unused.';missing=['unused condition'];if(ref==='A103'){sources.push('P4');manager=true;reply='The return is outside our 30-day window. A support manager must review any exception.';}}
 else if(['where','delivery','arriv','livraison','arriver'].some(w=>t.includes(w))){issue='delivery';sources=['P3'];reply='Standard delivery is estimated at 3–5 business days after dispatch, without a guaranteed arrival date.';}
 else{issue='other';reply='Please clarify your request so a support colleague can help.';missing=['request details'];}
 if(facts[ref]){sources.push(ref);reply=facts[ref]+' '+reply;}
 else if(ref){issue='unknown_order';sources=[];reply='This order reference is not in the supplied snapshot. Please check it or provide proof of purchase.';missing=['corrected order reference or proof of purchase'];manager=false;}
 return {id:'demo',customer_reply:reply,answers:[{issue,answer:reply,source_ids:sources}],evidence:sources.map(source_id=>({source_id,quote:facts[source_id]})),missing_information:missing,next_steps:[{owner:manager?'support_manager':'support_colleague',action:'Review the draft and enquiry',status:'proposed'}],needs_manager:manager};
}
export function validate(result){
 if(!Array.isArray(result.decisions)||result.decisions.length!==1)throw Error('Invalid response count');
 const d=result.decisions[0];
 if(d.id!=='demo'||typeof d.customer_reply!=='string'||!d.customer_reply.trim()||d.customer_reply.length>10000)throw Error('Invalid draft');
 if(!Array.isArray(d.answers)||!d.answers.length||!Array.isArray(d.evidence)||!Array.isArray(d.missing_information)||!Array.isArray(d.next_steps)||typeof d.needs_manager!=='boolean')throw Error('Invalid response structure');
 if(d.missing_information.some(s=>typeof s!=='string'))throw Error('Invalid clarification');
 const evidence=new Map();
 for(const e of d.evidence){if(!facts[e.source_id]||e.quote!==facts[e.source_id])throw Error('Unsupported source quote');evidence.set(e.source_id,e.quote);}
 for(const a of d.answers){if(!['return','delivery','damage','refund','exception','unknown_order','other'].includes(a.issue)||typeof a.answer!=='string'||!a.answer.trim()||!Array.isArray(a.source_ids)||a.source_ids.some(s=>!evidence.has(s)))throw Error('Unsupported answer');}
 for(const n of d.next_steps){if(n.status!=='proposed'||!['customer','support_colleague','support_manager'].includes(n.owner)||typeof n.action!=='string'||!n.action.trim())throw Error('Only proposed actions are permitted');}
 if(d.needs_manager&&!d.next_steps.some(n=>n.owner==='support_manager'))throw Error('Missing manager referral');
 return d;
}
