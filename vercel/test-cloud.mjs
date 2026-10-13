import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {baseline,validate} from './lib/workflow.mjs';import handler from './api/triage.mjs';
const report=JSON.parse(readFileSync('../evaluation.json','utf8'));
function response(){return {code:null,body:null,setHeader(){},status(c){this.code=c;return this},json(v){this.body=v;return this}}}
test('template parity with the original twelve test outputs',()=>{for(const r of report.rows){assert.deepEqual({...baseline(r.input),id:r.id},r.baseline)}});
test('source fabrication is rejected',()=>{const d=baseline('Where is A102?');d.evidence[0].quote='Guaranteed tomorrow';assert.throws(()=>validate({decisions:[d]}))});
test('completed actions are rejected',()=>{const d=baseline('Where is A102?');d.next_steps[0].status='completed';assert.throws(()=>validate({decisions:[d]}))});
test('invalid request never reaches model',async()=>{const r=response();await handler({method:'POST',headers:{host:'app.test'},body:{text:'',engine:'codex'}},r);assert.equal(r.code,400)});
test('foreign origin rejected',async()=>{const r=response();await handler({method:'POST',headers:{host:'app.test',origin:'https://evil.test'},body:{text:'Hello',engine:'codex'}},r);assert.equal(r.code,403)});
test('template works without cloud credentials',async()=>{const r=response();await handler({method:'POST',headers:{host:'app.test'},body:{text:'Where is A999?',engine:'baseline'}},r);assert.equal(r.code,200);assert.equal(r.body.decisions[0].evidence.length,0)});
test('provider authentication failure is visible with no template fallback',async()=>{const old=globalThis.fetch;process.env.AI_GATEWAY_API_KEY='test-only';globalThis.fetch=async()=>({ok:false,status:401,json:async()=>({error:{message:'Test rejection'}})});try{const r=response();await handler({method:'POST',headers:{host:'app.test'},body:{text:'Where is A102?',engine:'codex'}},r);assert.equal(r.code,503);assert.ok(!r.body.decisions)}finally{globalThis.fetch=old;delete process.env.AI_GATEWAY_API_KEY}});
