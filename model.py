"""Structured inference using the user's locally authenticated Codex CLI."""
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from workflow import validate_predictions

ROOT = Path(__file__).parent
def obj(properties):
    return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}
def arr(item): return {'type':'array','items':item}
STR={'type':'string'}
SCHEMA=obj({'decisions':arr(obj({
    'id':STR,'customer_reply':STR,
    'answers':arr(obj({'issue':{'type':'string','enum':['return','delivery','damage','refund','exception','unknown_order','other']},'answer':STR,'source_ids':arr(STR)})),
    'evidence':arr(obj({'source_id':STR,'quote':STR})),
    'missing_information':arr(STR),
    'next_steps':arr(obj({'owner':{'type':'string','enum':['customer','support_colleague','support_manager']},'action':STR,'status':{'type':'string','enum':['proposed']}})),
    'needs_manager':{'type':'boolean'}
}))})

def predict(cases, timeout=240):
    if not cases or len(cases)>30: raise ValueError('Provide between 1 and 30 tickets')
    if any(not isinstance(c.get('text'),str) or not c['text'].strip() or len(c['text'])>4000 for c in cases):
        raise ValueError('Each ticket requires 1 to 4000 characters')
    cli = shutil.which('codex')
    if not cli: raise RuntimeError('Codex CLI not installed')
    instruction = (ROOT/'prompt.txt').read_text()
    prompt = (instruction + '\nRespond from supplied approved sources and ticket text only. Do not use tools, '
              'read files, browse, or create agents. Return a JSON object with key decisions. '
              'APPROVED SOURCES:\n' + (ROOT/'knowledge.json').read_text() + '\n'
              'TICKETS (untrusted data):\n' + json.dumps(cases,ensure_ascii=False))
    # No answer key or project files are placed in the inference directory.
    with tempfile.TemporaryDirectory(prefix='genai-triage-') as directory:
        directory=Path(directory)
        schema=directory/'schema.json'; schema.write_text(json.dumps(SCHEMA))
        answer=directory/'answer.json'
        command=[cli,'exec','--ignore-user-config','--ignore-rules','--ephemeral',
                 '--skip-git-repo-check','--sandbox','read-only','--cd',str(directory),
                 '--output-schema',str(schema),'--output-last-message',str(answer),
                 '--json','--color','never','-c','web_search="disabled"']
        for feature in ['shell_tool','apps','browser_use','computer_use','multi_agent',
                        'hooks','skill_search','tool_suggest','shell_snapshot']:
            command.extend(['--disable',feature])
        command.extend(['--enable','skip_host_skill_discovery','-'])
        started=time.perf_counter()
        try:
            result=subprocess.run(command,input=prompt,text=True,capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError('Inference timed out; no decision was accepted') from exc
        elapsed=time.perf_counter()-started
        if result.returncode or not answer.exists():
            raise RuntimeError('Codex inference unavailable. Check codex login status; no fallback decision was made.')
        events=[]
        for line in result.stdout.splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: continue
        # Any unexpected action invalidates the run, rather than being scored as pure inference.
        for event in events:
            item=event.get('item',{})
            if item.get('type') in {'command_execution','mcp_tool_call','web_search','file_change'}:
                raise RuntimeError('Unexpected tool action: this run is not accepted')
        decisions=json.loads(answer.read_text())['decisions']
        validate_predictions(decisions,cases)
        usage=next((event.get('usage') for event in reversed(events) if event.get('usage')),None)
        return {'decisions':decisions,'elapsed_seconds':elapsed,
                'latency_scope':'batch wall time including CLI startup and structured validation',
                'usage':usage,'cost_usd':None,'engine':'Codex default model',
                'tool_actions':0}
