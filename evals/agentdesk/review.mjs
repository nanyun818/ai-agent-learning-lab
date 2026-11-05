import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { citationCheck } from './grading.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
if(!process.argv[2])throw Error('Usage: node review.mjs result.json');
const report=JSON.parse(await fs.readFile(process.argv[2],'utf8'));
for(const row of report.results) {
  if(row.status!=='graded')continue;
  row.checks=row.checks.filter(c=>!c.name.startsWith('所有知识库引用均来自'));
  row.checks.push(citationCheck(row.answer,row.persisted_sources||row.reference_documents));
  row.rule_pass=row.checks.every(c=>c.pass);
}
const graded=report.results.filter(r=>r.status==='graded');
report.summary.rule_passed_cases=graded.filter(r=>r.rule_pass).length;
report.summary.rule_pass_rate=graded.length?report.summary.rule_passed_cases/graded.length:null;
report.offline_regrade={date:new Date().toISOString(),reason:'Added detection of invented knowledge citations, including memory IDs presented as knowledge citations',new_model_calls:0,grader_sha256:(await import('node:crypto')).createHash('sha256').update(await fs.readFile(path.join(here,'grading.mjs'))).digest('hex')};
await fs.writeFile(process.argv[2],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({summary:report.summary,failures:report.results.filter(r=>r.rule_pass===false).map(r=>({id:r.id,checks:r.checks.filter(c=>!c.pass)})),new_model_calls:0},null,2));
