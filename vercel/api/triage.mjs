import {getVercelOidcToken} from '@vercel/oidc';
import {facts,prompt,schema} from '../lib/data.mjs';
import {baseline,validate} from '../lib/workflow.mjs';
export const config={maxDuration:60};
const limits=new Map();
export default async function handler(req,res){
 res.setHeader('Cache-Control','no-store');
 if(req.method!=='POST')return res.status(405).json({error:'POST required'});
 const origin=req.headers.origin;
 if(origin){try{if(new URL(origin).host!==req.headers.host)return res.status(403).json({error:'Use this app to prepare a draft.'});}catch{return res.status(403).json({error:'Invalid origin'});}}
 const body=req.body;
 if(!body||typeof body.text!=='string'||!body.text.trim()||body.text.length>4000||!['codex','baseline'].includes(body.engine))return res.status(400).json({error:'Enter a message of 1–4,000 characters and choose a valid method.'});
 const start=performance.now();
 if(body.engine==='baseline')return res.status(200).json({decisions:[baseline(body.text)],engine:'First-topic template',elapsed_seconds:(performance.now()-start)/1000});
 const ip=req.headers['x-forwarded-for']?.split(',')[0]||'unknown',now=Date.now(),old=limits.get(ip)||{at:now,n:0};
 if(now-old.at>60000){old.at=now;old.n=0;}old.n++;limits.set(ip,old);
 for(const [key,l]of limits)if(now-l.at>120000)limits.delete(key);
 if(old.n>10)return res.status(429).json({error:'Please wait a minute before another draft.'});
 let token=process.env.AI_GATEWAY_API_KEY;
 if(!token)token=req.headers['x-vercel-oidc-token'];
 if(!token){try{token=await getVercelOidcToken();}catch{token=process.env.VERCEL_OIDC_TOKEN;}}
 if(!token)return res.status(503).json({error:'Cloud model access is not configured. No draft was generated.'});
 try{
  const model=process.env.AI_MODEL||'openai/gpt-4.1';
  const upstream=await fetch('https://ai-gateway.vercel.sh/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},signal:AbortSignal.timeout(45000),body:JSON.stringify({model,temperature:0,max_tokens:2400,messages:[{role:'system',content:prompt+'\nReturn exactly ONE decision per enquiry id. Answer every topic and order of that enquiry inside that single decision.'+'\nAPPROVED SOURCES:\n'+JSON.stringify(facts)},{role:'user',content:JSON.stringify([{id:'demo',text:body.text}])}],response_format:{type:'json_schema',json_schema:{name:'support_reply',strict:true,schema}}})});
  if(!upstream.ok){const failure=await upstream.json().catch(()=>({}));console.error('Gateway status',upstream.status, String(failure?.error?.message||failure?.message||'Unknown').replace(/eyJ[A-Za-z0-9_.-]+/g,'[redacted]').slice(0,400));return res.status(503).json({error:`Cloud model unavailable (gateway ${upstream.status}). No fallback draft was used.`});}
  const payload=await upstream.json(),result=JSON.parse(payload.choices?.[0]?.message?.content||'null');
  // Evidence text always comes from the approved sources; the model only chooses source IDs (unknown IDs are still rejected by validate).
  for(const d of result?.decisions||[])for(const e of d?.evidence||[])if(facts[e?.source_id])e.quote=facts[e.source_id];
  validate(result);
  return res.status(200).json({...result,engine:model,elapsed_seconds:(performance.now()-start)/1000,usage:payload.usage||null,cost_usd:null,tool_actions:0});
 }catch(err){console.error('Draft rejected',err.name);return res.status(503).json({error:'The model response could not be accepted. Please retry or ask a support colleague.'});}
}
