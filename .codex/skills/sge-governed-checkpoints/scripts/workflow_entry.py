#!/usr/bin/env python3
"""统一执行包入口。仅协调已有工具，不产生批准、独立审查或完成结论。"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile, uuid
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parent
WRITE_ACTIONS={'builder','install','upgrade','release','deploy'}
LAYERS=('design','implementation','integration','independent_validation')
class Rejected(ValueError):
    def __init__(self,code,detail=''):
        super().__init__(detail);self.code=code

def fail(code,detail=''): raise Rejected(code,detail)
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(x): return hashlib.sha256(x).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(canonical(x)+b'\n')
def path(root,raw,exists=False):
    if not isinstance(raw,str) or not raw or Path(raw).is_absolute() or '..' in Path(raw).parts: fail('PATH_OUTSIDE_ROOT',str(raw))
    p=(root/raw).resolve()
    if not p.is_relative_to(root):fail('PATH_OUTSIDE_ROOT',raw)
    if exists and not p.is_file():fail('INPUT_MISSING',raw)
    return p

def digest(p,serialization):
    if serialization=='raw_bytes':return sha(p.read_bytes())
    if serialization=='canonical_json':return sha(canonical(read(p)))
    fail('DIGEST_TYPE_INVALID')
def legacy(name,root=None):
    location=(root/'.codex/skills/sge-governed-checkpoints/scripts' if root else SCRIPTS)/(name+'.py')
    key='_workflow_'+name+'_'+sha(str(location).encode())
    if key not in sys.modules:
        spec=importlib.util.spec_from_file_location(key,location);mod=importlib.util.module_from_spec(spec)
        sys.modules[key]=mod;spec.loader.exec_module(mod)
    return sys.modules[key]
def pointer(x,p):
    if p=='':return x
    if not isinstance(p,str) or not p.startswith('/'):fail('SOURCE_POINTER_INVALID')
    for token in p[1:].split('/'):
        # RFC 6901: 只有~0/~1转义；数组只接受0或无前导零的ASCII十进制索引。
        i=0
        while i<len(token):
            if token[i]=='~':
                if i+1==len(token) or token[i+1] not in '01':fail('SOURCE_POINTER_INVALID')
                i+=1
            i+=1
        token=token.replace('~1','/').replace('~0','~')
        if isinstance(x,list):
            if not token or any(c not in '0123456789' for c in token) or (len(token)>1 and token[0]=='0'):
                fail('SOURCE_POINTER_INVALID')
            try:x=x[int(token)]
            except (IndexError,ValueError):fail('SOURCE_POINTER_MISSING')
        elif isinstance(x,dict):
            if token not in x:fail('SOURCE_POINTER_MISSING')
            x=x[token]
        else:fail('SOURCE_POINTER_INVALID')
    return x

def nonempty_text(value):
    return isinstance(value,str) and bool(value.strip())

def text_fields(value,names):
    return isinstance(value,dict) and all(nonempty_text(value.get(name)) for name in names)

def units_valid(units,task):
    ids=set()
    for u in units:
        if not isinstance(u,dict):fail('WORK_UNIT_UNGROUNDED')
        if (not u.get('id') or u['id'] in ids or not u.get('ac_ids') or not set(u['ac_ids']).issubset(task['acceptance_criteria_ids'])
            or not u.get('releases_dependency') or not u.get('observable_result')):fail('WORK_UNIT_UNGROUNDED')
        ids.add(u['id'])
    table={u['id']:u for u in units};active=set();done=set()
    def visit(k):
        if k not in table or k in active:fail('WORK_DEPENDENCY_INVALID')
        if k in done:return
        active.add(k)
        for d in table[k].get('depends_on',[]):visit(d)
        active.remove(k);done.add(k)
    for k in ids:visit(k)

def validate_inputs(root,spec):
    if spec.get('schema_version')!='workflow_spec_v1':fail('SPEC_INVALID')
    if not isinstance(spec.get('commands'),dict) or not spec['commands']:fail('COMMAND_INVALID')
    for c in spec['commands'].values():
        if c.get('action') not in WRITE_ACTIONS|{'check'}:fail('ACTION_INVALID')
        if not isinstance(c.get('mutating'),bool) or c['mutating']!=(c['action'] in WRITE_ACTIONS):fail('COMMAND_METADATA_CONFLICT')
        if not isinstance(c.get('argv'),list) or not c['argv'] or any(not isinstance(a,str) or not a for a in c['argv']):fail('COMMAND_INVALID')
        if not c.get('target') or not c.get('checkpoint'):fail('COMMAND_INVALID')
        if not path(root,c.get('cwd','.')).is_dir():fail('INPUT_MISSING','cwd')
    task=pointer(read(path(root,spec['task_source']['path'],True)),spec['task_source']['pointer'])
    card=read(path(root,spec['card_template'],True));ctx=read(path(root,spec['context'],True))
    try:legacy('lane_task_card').validate_card(card,repo_root=root)
    except (ValueError,OSError) as exc:fail('LEGACY_CARD_INVALID',str(exc))
    try:legacy('context_bootstrap').validate_packet(ctx)
    except (ValueError,OSError) as exc:fail('LEGACY_CONTEXT_INVALID',str(exc))
    pairs=[('session_id',card.get('session_id')),('acceptance_criteria_ids',card.get('acceptance_criteria_ids')),
           ('write_scope',card.get('write_scope')),('required_outputs',card.get('required_outputs')),
           ('maximum_claim',card.get('maximum_claim_ref',{}).get('summary'))]
    if (task.get('task_id')!=spec.get('task_id') or card['topology']['task_id']!=spec['task_id'] or ctx.get('task_id')!=spec['task_id']
        or any(task.get(k)!=v for k,v in pairs)):fail('TASK_RESIDUE')
    if read(path(root,spec['topology'],True)).get('task_id')!=spec['task_id']:fail('TASK_RESIDUE')
    for out in task['required_outputs']:
        p=path(root,out)
        if not any(p==path(root,s) or ((s.endswith('/') or path(root,s).is_dir()) and p.is_relative_to(path(root,s))) for s in task['write_scope']):fail('TASK_RESIDUE','output outside write scope')
    units_valid(spec.get('work_units',[]),task)
    for name,ref in spec.get('state_sources',{}).items():
        for r in ([ref['baseline'],ref['current']] if name=='snapshot' else [ref]):
            path(root,r['path'])
            if r.get('expected_task_id')!=spec['task_id']:fail('SOURCE_TASK_MISMATCH')
            if not isinstance(r.get('pointer'),str):fail('SOURCE_POINTER_INVALID')
    for h in spec.get('history_refs',[]):
        if h.get('purpose') not in {'background','dependency'} or not h.get('task_id'):fail('HISTORY_INVALID')
        path(root,h['path'],True)
    return task,card,ctx

def records(root,specpath,spec,card,ctx,out):
    refs={}
    def add(raw,role='source',serial='raw_bytes'):
        p=path(root,raw,True)
        if p==out or p.is_relative_to(out):fail('BUNDLE_INPUT_OVERLAP')
        k=p.relative_to(root).as_posix()
        if role not in {'source','authority','governance','topology','background','contract','cases'}:fail('BINDING_ROLE_INVALID')
        if k not in refs or refs[k]['role']=='background':refs[k]={'path':k,'role':role,'serialization':serial}
    for b in spec.get('bindings',[]):add(b['path'],b['role'],b['serialization'])
    for raw,role in [(specpath,'authority'),(spec['task_source']['path'],'authority'),(spec['card_template'],'authority'),(spec['context'],'governance'),(spec['topology'],'topology')]:add(raw,role)
    if spec.get('admission') and any(c['mutating'] for c in spec['commands'].values()):
        add(spec['admission'],'authority')
        for r in read(path(root,spec['admission'],True)).values():
            if isinstance(r,dict) and 'path' in r and 'sha256' in r:add(r['path'],'authority')
    elif any(c['mutating'] for c in spec['commands'].values()):fail('INPUT_MISSING','admission')
    def walk(x):
        if isinstance(x,dict):
            if 'path' in x and 'sha256' in x:add(x['path'],'authority')
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(card)
    for k in ('forbidden_claims_ref','rebaseline_ref'):add(card[k],'authority')
    if card['snapshot'].get('parent_snapshot_ref'):add(card['snapshot']['parent_snapshot_ref'],'authority')
    for r in ctx['required_read_set']:
        raw=r['path']
        if not Path(raw).is_absolute() and '..' not in Path(raw).parts and (root/raw).is_file() and r.get('applicability')!='not_applicable':add(raw,'governance')
    for h in spec.get('history_refs',[]):add(h['path'],'background' if h['purpose']=='background' else 'source')
    if 'snapshot' in spec.get('state_sources',{}):add(spec['state_sources']['snapshot']['baseline']['path'])
    for c in spec['commands'].values():
        for a in c['argv']:
            if a=='{python}' or a.startswith('-'):continue
            candidate=str(Path(c['cwd'])/a)
            if not Path(candidate).is_absolute() and (root/candidate).is_file():add(candidate)
            elif a.endswith('.py'):path(root,candidate,True)
    result=[]
    for i,r in enumerate(sorted(refs.values(),key=lambda x:x['path'])):
        serial=r.pop('serialization');result.append(dict(r,frozen_path=f'inputs/{i:04d}',digest={'algorithm':'sha256','serialization':serial,'value':digest(path(root,r['path'],True),serial)}))
    return result

def seal(directory):
    return {p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in sorted(directory.rglob('*')) if p.is_file() and p!=directory/'seal.json'}

def inspect(root,bundle,current=True):
    try:
        if read(bundle/'seal.json')!=seal(bundle):fail('BUNDLE_TAMPERED')
        m=read(bundle/'manifest.json');spec=read(bundle/'spec.json')
        if m['schema_version']!='workflow_manifest_v1':fail('BUNDLE_TAMPERED')
        for r in m['files']:
            d=r['digest']
            if d['algorithm']!='sha256' or digest(path(bundle,r['frozen_path'],True),d['serialization'])!=d['value']:fail('BUNDLE_TAMPERED')
        if current:
            for r in m['files']:
                if r['role']=='background':continue
                p=path(root,r['path'])
                if not p.is_file() or digest(p,r['digest']['serialization'])!=r['digest']['value']:fail('BINDING_DRIFT',r['path'])
            validate_inputs(root,spec)
        return m,spec
    except Rejected as exc:
        if exc.code in {'INPUT_MISSING','DIGEST_TYPE_INVALID'}:fail('BUNDLE_TAMPERED',str(exc))
        raise
    except (ValueError,OSError,KeyError,TypeError) as exc:fail('BUNDLE_TAMPERED',str(exc))

def prepare(root,req):
    spec=read(path(root,req['spec'],True));task,card,ctx=validate_inputs(root,spec)
    out=path(root,req['out']);files=records(root,req['spec'],spec,card,ctx,out)
    identity=sha(canonical({'spec':spec,'files':files}));out.parent.mkdir(parents=True,exist_ok=True)
    lock=out.parent/('.'+out.name+'.prepare-lock')
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:fail('PREPARE_BUSY')
    stage=None
    try:
        os.close(fd)
        if out.exists():
            m,_=inspect(root,out,False)
            if m['input_identity']!=identity:fail('BUNDLE_CONFLICT')
            return {'verdict':'pass','bundle':req['out'],'input_identity':identity}
        stage=Path(tempfile.mkdtemp(prefix='.'+out.name+'.stage-',dir=out.parent))
        for r in files:
            dest=stage/r['frozen_path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path(root,r['path'],True),dest)
            if digest(dest,r['digest']['serialization'])!=r['digest']['value']:fail('BINDING_DRIFT',r['path'])
        write(stage/'spec.json',spec);write(stage/'card.json',card)
        # 使用原renderer；消费者fixture/安装副本自带相同CLI，保留其实际相对路径。
        renderer=legacy('lane_task_card') if SCRIPTS.is_relative_to(root) else legacy('lane_task_card',root)
        (stage/'prompt.md').write_text(renderer.render_card(out/'card.json',card,repo_root=root),encoding='utf-8')
        write(stage/'manifest.json',{'schema_version':'workflow_manifest_v1','task_id':spec['task_id'],'input_identity':identity,'files':files,
            'card_digest':{'algorithm':'sha256','serialization':'canonical_json','value':sha(canonical(card))}})
        write(stage/'seal.json',seal(stage))
        if req.get('failpoint')=='before_publish':fail('PREPARE_INTERRUPTED')
        for r in files:
            if r['role']!='background' and digest(path(root,r['path'],True),r['digest']['serialization'])!=r['digest']['value']:fail('BINDING_DRIFT',r['path'])
        stage.rename(out);stage=None
        return {'verdict':'pass','bundle':req['out'],'input_identity':identity}
    finally:
        if stage is not None:shutil.rmtree(stage)
        lock.unlink(missing_ok=True)

def evidence(root,refs):
    try:return bool(refs) and all(digest(path(root,r['path'],True),r['serialization'])==r['sha256'] for r in refs)
    except (Rejected,ValueError,OSError,KeyError,TypeError):return False

def findings(root,items):
    result=[]
    for item in items:
        f=dict(item,confirmed_blocker=False)
        if f.get('status')=='closed':result.append(f);continue
        try:
            if not text_fields(f,('finding_id','assertion','observation','impact','status','producer')):
                fail('FINDING_FIELDS_INVALID')
            if f['status'] not in {'pending','needs_evidence','needs_review','unsupported','confirmed'}:
                fail('FINDING_FIELDS_INVALID')
            if 'confirmation_ref' not in f or (f['confirmation_ref'] is not None and not nonempty_text(f['confirmation_ref'])):
                fail('FINDING_FIELDS_INVALID')
            source=f.get('source')
            if not text_fields(source,('path','quote')):fail('SOURCE_MISSING')
            p=path(root,source['path'],True);lines=p.read_text().splitlines()
            a,b=source.get('start_line'),source.get('end_line')
            if type(a) is not int or type(b) is not int or a<1 or b<a or b>len(lines) or '\n'.join(lines[a-1:b])!=source['quote']:
                fail('SOURCE_LOCATOR_MISMATCH')
            valid=False
            if f['confirmation_ref'] is not None:
                c=read(path(root,f['confirmation_ref'],True))
                valid=(text_fields(c,('finding_id','assertion','source_sha256','reviewer','producer','verdict'))
                    and c['finding_id']==f['finding_id'] and c['assertion']==f['assertion']
                    and c['source_sha256']==sha(p.read_bytes()) and c['producer']==f['producer']
                    and c['reviewer']!=c['producer'])
                if valid and c['verdict']=='unsupported':f['status']='unsupported'
                elif valid and c['verdict']=='supported':f.update(status='confirmed',confirmed_blocker=True)
                else:valid=False
            if not valid and f['status']=='confirmed':f['status']='needs_review'
        except (Rejected,ValueError,OSError,KeyError,TypeError) as exc:
            f.update(status='needs_evidence',reason=exc.code if isinstance(exc,Rejected) else 'SOURCE_MISSING')
        result.append(f)
    return result

def runnable(root,bundle):
    try:inspect(root,bundle);return True
    except Rejected:return False

def resume(root,bundle,m,spec):
    observations=[];statuses={}
    def source(name,ref,frozen=False):
        observation={'path':ref.get('path'),'pointer':ref.get('pointer'),'sha256':None};observations.append(observation)
        try:
            p=path(root,ref['path'],True)
            if frozen:p=path(bundle,next(r for r in m['files'] if r['path']==ref['path'])['frozen_path'],True)
            x=read(p);observation['sha256']=sha(p.read_bytes())
            if not isinstance(x,dict):fail('SOURCE_TYPE_INVALID')
            if x.get('task_id')!=ref.get('expected_task_id') or x.get('task_id')!=spec['task_id']:fail('SOURCE_TASK_MISMATCH')
            v=pointer(x,ref['pointer']);statuses[name]='valid';return v
        except (Rejected,ValueError,OSError,KeyError,TypeError,IndexError,StopIteration) as exc:
            statuses[name]='unknown';observation['reason']=exc.code if isinstance(exc,Rejected) else 'SOURCE_UNAVAILABLE';return None
    sources=spec.get('state_sources',{});values={}
    for name in ('findings','work_units','review_budget'):
        values[name]=source(name,sources[name]) if name in sources else spec.get(name,None if name=='review_budget' else [])
        if values[name] is not None:
            valid=isinstance(values[name],dict if name=='review_budget' else list)
            if name!='review_budget' and valid:valid=all(isinstance(v,dict) for v in values[name])
            if not valid:statuses[name]='unknown';values[name]=None
            elif name=='review_budget' and legacy('review_budget_preflight').evaluate_budget(values[name])['status']=='invalid_input':statuses[name]='unknown';values[name]=None
    comparison=None
    if 'snapshot' in sources:
        ref=sources['snapshot'];baseline=source('snapshot',ref['baseline'],True);current=source('snapshot',ref['current'])
        if baseline is None or current is None:statuses['snapshot']='unknown';comparison={'status':'unknown'}
        else:
            try:comparison=legacy('context_state').compare_snapshots(baseline,current,delta_read_set=ref.get('delta_read_set',[]))
            except (ValueError,KeyError,TypeError,AttributeError):statuses['snapshot']='unknown';comparison={'status':'unknown'}
    layers=dict.fromkeys(LAYERS,'unknown');rounds=[]
    for raw in spec.get('reviews',[]):
        try:
            r=read(path(root,raw,True))
            if not isinstance(r,dict):continue
            if r.get('task_id')!=spec['task_id'] or r.get('layer') not in layers:continue
            if type(r.get('round')) is int and r['round']>=1:rounds.append(r['round'])
            if not text_fields(r,('task_id','layer','verdict','reviewer','producer')) or r['reviewer']==r['producer']:continue
            if type(r.get('round')) is not int or r['round']<1 or not isinstance(r.get('bindings'),list) or not r['bindings']:continue
            if r['verdict']=='pass':layers[r['layer']]='valid' if evidence(root,r['bindings']) else 'stale'
        except (Rejected,ValueError,OSError,KeyError,TypeError):continue
    units=values['work_units'] or [];task=pointer(read(path(root,spec['task_source']['path'],True)),spec['task_source']['pointer'])
    try:units_valid(units,task)
    except (Rejected,TypeError,KeyError,AttributeError):
        if 'work_units' not in sources:raise
        statuses['work_units']='unknown';units=[]
    proven={u['id'] for u in units if u.get('state')=='done' and evidence(root,u.get('evidence'))}
    ready=[u['id'] for u in units if u.get('state')=='ready' and set(u.get('depends_on',[])).issubset(proven)]
    action='execute_ready_work' if ready else 'inspect_evidence'
    if len(units)>=2 and all(u.get('state')=='no_progress' and not u.get('evidence') for u in units[-2:]):action='diagnose_no_progress'
    if 'stale' in layers.values() or (comparison or {}).get('status')=='rebaseline_required':action='rebaseline'
    if 'unknown' in statuses.values():ready=[];action='inspect_state_sources'
    return {'verdict':'pass','runnable':runnable(root,bundle),'layers':layers,'review_rounds':rounds,'findings':findings(root,values['findings'] or []),
        'ready_work_units':ready,'unproven_done_work_units':[u['id'] for u in units if u.get('state')=='done' and u['id'] not in proven],
        'review_budget':legacy('review_budget_preflight').evaluate_budget(values['review_budget']),'state_source_status':statuses,
        'state_source_observations':observations,'snapshot_comparison':comparison,'next_action':action}

def execute(request):
    try:
        root=Path(request['repo']).resolve(strict=True)
        if not Path(request['repo']).is_absolute() or not root.is_dir():fail('REPO_INVALID')
        op=request['op']
        if op=='prepare':return prepare(root,request)
        bundle=path(root,request['bundle'])
        if op=='run':
            _,spec=inspect(root,bundle,False);name=request.get('command')
            if name not in spec['commands']:fail('COMMAND_UNKNOWN')
            c=spec['commands'][name]
            if request.get('action')!=c['action'] or request.get('target')!=c['target']:fail('ACTION_TARGET_MISMATCH')
            if request.get('checkpoint')!=c['checkpoint']:fail('CHECKPOINT_MISMATCH')
            inspect(root,bundle)
            if c['mutating']:
                try:legacy('execution_admission').validate(read(path(root,spec['admission'],True)),root,expected_action=c['action'],expected_target=c['target'])
                except (ValueError,OSError) as exc:fail('LEGACY_ADMISSION_INVALID',str(exc))
            argv=[sys.executable if a=='{python}' else a for a in c['argv']]
            r=subprocess.run(argv,cwd=path(root,c['cwd']),shell=False,capture_output=True,text=True)
            result={'verdict':'pass' if r.returncode==0 else 'blocked','returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,
                    'argv':argv,'checkpoint':c['checkpoint'],'action':c['action'],'target':c['target']}
            if r.returncode:result['fingerprint']='COMMAND_FAILED'
            receipt=bundle.parent/(bundle.name+'.run-'+uuid.uuid4().hex+'.json');write(receipt,result)
            return dict(result,receipt=receipt.relative_to(root).as_posix())
        if op=='check':inspect(root,bundle);return {'verdict':'pass'}
        if op=='resume':
            m,spec=inspect(root,bundle,False);return resume(root,bundle,m,spec)
        fail('OPERATION_INVALID')
    except Rejected as exc:return {'verdict':'blocked','fingerprint':exc.code,'detail':str(exc)}
    except (ValueError,OSError,KeyError,TypeError,IndexError,AttributeError) as exc:return {'verdict':'blocked','fingerprint':'INPUT_INVALID','detail':str(exc)}

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='op',required=True)
    for op in ('prepare','check','run','resume'):
        cmd=subs.add_parser(op);cmd.add_argument('--repo',required=True)
        for key in (('spec','out') if op=='prepare' else ('bundle',)):cmd.add_argument('--'+key,required=True)
        if op=='run':
            for key in ('command','checkpoint','action','target'):cmd.add_argument('--'+key,required=True)
    result=execute(vars(p.parse_args()));print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0 if result['verdict']=='pass' else 1
if __name__=='__main__':raise SystemExit(main())
