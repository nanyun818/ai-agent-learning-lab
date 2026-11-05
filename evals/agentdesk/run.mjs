import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import os from 'node:os';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { citationCheck } from './grading.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const option = name => { const i = args.indexOf(name); return i < 0 ? '' : args[i + 1] || ''; };
const live = args.includes('--run'), check = args.includes('--check');
const source = option('--source') || process.env.AGENT_DESK_SOURCE;
const model = option('--model') || 'deepseek-flash';
const datasetBytes = await fs.readFile(path.join(here, 'cases.json'));
const dataset = JSON.parse(datasetBytes);
const requestedCase = option('--case');
// The cross-session case requires an actual previous session to exist.
const selected = dataset.cases.filter(c => !requestedCase || c.id === requestedCase || requestedCase === 'ad07' && c.id === 'ad06');
if (!selected.length) throw Error('Unknown case ID');
if (!source) throw Error('Use --source with your Agent Desk source directory, or set AGENT_DESK_SOURCE');
if (live && check) throw Error('Choose --check or --run');
if (!live && !check) {
  console.log(JSON.stringify({ mode: 'preview', dataset: dataset.dataset_id, cases: selected.map(c => ({ id:c.id, name:c.name, criterion:c.human_criterion })), maximum_model_requests: selected.reduce((n,c) => n+c.turns.length,0), generation_output_cap:512, model, new_model_calls:0 }, null, 2));
  process.exit(0);
}
if (live && !process.env.DEEPSEEK_API_KEY) throw Error('DEEPSEEK_API_KEY is missing; no model request was sent');
const root = await fs.realpath(source);
const load = name => import(pathToFileURL(path.join(root, 'server', name)).href);
const [{ createStore }, { createApp }] = await Promise.all([load('store.mjs'), load('app.mjs')]);
const sha = data => createHash('sha256').update(data).digest('hex');
const sourceNames = ['app.mjs','store.mjs','extensions.mjs','providers.mjs','harness-policy.mjs'];
const hashes = Object.fromEntries(await Promise.all(sourceNames.map(async n => ['server/'+n, sha(await fs.readFile(path.join(root,'server',n)))])));
let commit = 'unknown', dirty = true;
try { commit = execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(); dirty = Boolean(execFileSync('git',['-C',root,'status','--porcelain'],{encoding:'utf8'}).trim()); } catch {}
const scratch = await fs.mkdtemp(path.join(os.tmpdir(),'agentdesk-eval-'));
const store = createStore(path.join(scratch,'data'));
const planned = selected.reduce((n,c) => n+c.turns.length,0);
const report = { schema_version:1, dataset_id:dataset.dataset_id, dataset_sha256:sha(datasetBytes), started_at:new Date().toISOString(), mode:live?'live-app-generation':'retrieval-preflight', source:{commit,dirty,files_sha256:hashes}, scope:'Actual source backend HTTP APIs; isolated synthetic data; no Electron UI, task engine, MCP execution, or production database', model:live?model:null, configuration_override:{max_tokens:512,thinking:'disabled',temperature:0}, planned_model_requests:live?planned:0, attempted_model_requests:0, judge_model_requests:0, human_review:'pending', results:[] };
let app, appServer, gateway;
let activeCase = '', observed = [];
const listen = server => new Promise((resolve,reject) => {server.once('error',reject);server.listen(0,'127.0.0.1',resolve);});
const close = server => new Promise(resolve => { if(!server) return resolve(); server.closeAllConnections?.(); server.close(resolve); });
const checksFor = (c, context, mapping) => {
  const ids = new Set(context.sources.map(s=>s.id));
  const checks = [];
  for(const key of c.expected_sources) checks.push({dimension:'retrieval',name:'应提供资料:'+key,pass:ids.has(mapping[key])});
  for(const key of c.forbidden_sources) checks.push({dimension:'isolation',name:'不得注入资料:'+key,pass:!ids.has(mapping[key])});
  return checks;
};
const unknown = text => /不知道|不清楚|不确定|无法|不能确定|没有.{0,12}(信息|资料|记录|提供)|未.{0,8}(提供|记录|知)|缺少|缺乏|不足|未提及/.test(text);
try {
  // Only this local gateway may call the official DeepSeek endpoint. No mock answers.
  gateway = http.createServer(async (req,res) => {
    if(req.method!=='POST'||req.url!=='/v1/chat/completions'||!live) {res.writeHead(403);res.end();return;}
    if(report.attempted_model_requests >= planned) {res.writeHead(429);res.end();return;}
    let text='';for await(const part of req) {text+=part;if(text.length>200000) {res.writeHead(413);res.end();return;}}
    const body=JSON.parse(text);
    observed.push({case_id:activeCase,messages:body.messages});
    report.attempted_model_requests++;
    const timer = AbortSignal.timeout(60000);
    try {
      const response=await fetch('https://api.deepseek.com/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+process.env.DEEPSEEK_API_KEY},body:JSON.stringify({...body,model,max_tokens:512,temperature:0,thinking:{type:'disabled'}}),signal:timer});
      if(!response.ok) {res.writeHead(response.status);res.end(JSON.stringify({error:{message:'Upstream HTTP '+response.status}}));return;}
      res.writeHead(200,{'Content-Type':'text/event-stream'});
      await pipeline(Readable.fromWeb(response.body),res);
    } catch {if(!res.headersSent)res.writeHead(502);res.end();}
  });
  await listen(gateway);
  app=createApp(store,{noExternalCredentials:true,importRoots:{}});
  const providerId='eval-provider';
  store.put('provider',{id:providerId,name:'Evaluation gateway',baseUrl:`http://127.0.0.1:${gateway.address().port}/v1`,models:[model],protocol:'chat-completions',thinking:true,requiresKey:false});
  appServer=http.createServer(app);await listen(appServer);
  const base=`http://127.0.0.1:${appServer.address().port}`;
  const boot=await(await fetch(base+'/api/bootstrap')).json();
  const api=async (route,body) => {
    const response=await fetch(base+'/api'+route,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json','x-agent-token':boot.token},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(75000)});
    if(!response.ok)throw Error('Agent Desk API HTTP '+response.status);
    return response.headers.get('Content-Type')?.includes('text/event-stream')?response.text():response.json();
  };
  for(const p of dataset.projects)store.put('project',{...p,path:'',createdAt:new Date().toISOString()});
  const mapping={};
  for(const r of dataset.references) {
    const value=await api('/extensions/items/'+r.kind,{...r,targets:['provider:'+providerId]});mapping[r.key]=value.id;
  }
  for(const c of selected) {
    activeCase=c.id;
    const started=performance.now();
    const query=c.turns.at(-1);
    const context=await api('/extensions/preview',{projectId:'eval-a',target:'provider:'+providerId,query});
    const result={id:c.id,name:c.name,category:c.category,question:query,human_criterion:c.human_criterion,source_keys:context.sources.map(s=>Object.keys(mapping).find(k=>mapping[k]===s.id)),reference_documents:context.sources,checks:checksFor(c,context,mapping),human_review:'pending'};
    if(live) {
      const session=await api('/sessions',{projectId:'eval-a',providerId,model,title:'Eval '+c.id});
      try {
        for(const turn of c.turns) {
          const stream=await api(`/sessions/${session.id}/chat`,{content:turn,thinking:false});
          if(!stream.includes('event: done'))throw Error('Missing final SSE event');
          const saved=await api('/sessions/'+session.id);
          if(saved.messages.at(-1)?.status!=='complete')throw Error(saved.messages.at(-1)?.error||'Incomplete answer');
        }
        const saved=await api('/sessions/'+session.id);
        const assistant=saved.messages.at(-1);
        result.answer=assistant.content;result.usage=assistant.usage||null;result.finish_reason=assistant.finishReason||null;
        result.persisted_sources=assistant.sources||[];
        result.requests=observed.filter(r=>r.case_id===c.id);
        const request=result.requests.at(-1);
        const answer=assistant.content;
        result.checks.push(citationCheck(answer,result.persisted_sources));
        for(const value of c.answer_contains||[])result.checks.push({dimension:'answer',name:'回答包含:'+value,pass:answer.toLowerCase().includes(value.toLowerCase())});
        for(const value of c.answer_forbids||[])result.checks.push({dimension:'isolation',name:'回答不包含:'+value,pass:!answer.includes(value)});
        if(c.expect_unknown)result.checks.push({dimension:'answer',name:'明确说明信息不足（规则初筛）',pass:unknown(answer)});
        if(c.forbid_money)result.checks.push({dimension:'answer',name:'没有编造金额（规则初筛）',pass:!/[\d一二三四五六七八九十百千万亿]+\s*(?:万元|亿元|元)/.test(answer)});
        if(c.citation_source) {
          const valid=assistant.sources?.filter(s=>s.id===mapping[c.citation_source]).map(s=>'['+s.citation+']')||[];
          result.checks.push({dimension:'citation',name:'引用已检索到的指定资料（未验证语义蕴含）',pass:valid.some(cite=>answer.includes(cite))});
        }
        if(c.history_contains) result.checks.push({dimension:'history',name:'第二次请求包含第一轮用户消息',pass:request.messages.some(m=>m.role==='user'&&m.content.includes(c.history_contains))});
        for(const value of c.request_forbids||[])result.checks.push({dimension:'isolation',name:'请求不包含:'+value,pass:!JSON.stringify(request.messages).includes(value)});
        for(const key of c.forbidden_sources)result.checks.push({dimension:'isolation',name:'真实模型请求不包含禁用/跨项目内容:'+key,pass:!JSON.stringify(request.messages).includes(dataset.references.find(r=>r.key===key).content)});
        result.checks.push({dimension:'persistence',name:'用户和助手消息已完整保存',pass:saved.messages.length===c.turns.length*2&&saved.messages.every(m=>m.status==='complete')});
        result.checks.push({dimension:'transport',name:'输出未因token上限截断',pass:assistant.finishReason!=='length'});
        result.status='graded';
      } catch(error) {
        result.status='error';result.error=String(error.message).slice(0,180);report.results.push(result);
        console.log(c.id+' ERROR: '+result.error);break;
      }
    } else result.status='preflight-only';
    result.elapsed_ms=Math.round(performance.now()-started);
    result.rule_pass=result.checks.every(c=>c.pass);
    report.results.push(result);
    console.log(c.id+' '+(result.rule_pass?'PASS':'FAIL')+' '+c.name);
  }
  const graded=report.results.filter(r=>r.status==='graded');
  const gates=report.results.filter(r=>r.status==='preflight-only');
  report.summary={completed_cases:graded.length,preflight_cases:gates.length,rule_passed_cases:graded.filter(r=>r.rule_pass).length,errors:report.results.filter(r=>r.status==='error').length,not_run_cases:selected.length-report.results.length,rule_pass_rate:graded.length?graded.filter(r=>r.rule_pass).length/graded.length:null,not_a_general_model_score:true};
} finally {
  await app?.locals.shutdown();await close(appServer);await close(gateway);store.close();
  // Check the resolved absolute path before removing only our disposable fixture DB.
  const checkedScratch=await fs.realpath(scratch);
  const checkedTemp=await fs.realpath(os.tmpdir());
  if(path.dirname(checkedScratch)!==checkedTemp || !path.basename(checkedScratch).startsWith('agentdesk-eval-')) throw Error('Refusing cleanup outside the evaluation fixture');
  await fs.rm(checkedScratch,{recursive:true,force:true});
  report.finished_at=new Date().toISOString();
  const output=path.resolve(option('--out')||path.join(here,'results',new Date().toISOString().replace(/[:.]/g,'-')+'-'+randomUUID().slice(0,8)+'.json'));
  await fs.mkdir(path.dirname(output),{recursive:true});await fs.writeFile(output,JSON.stringify(report,null,2)+'\n');
  console.log('REPORT '+output);console.log('MODEL REQUESTS '+report.attempted_model_requests);
}
