import test from 'node:test';
import assert from 'node:assert/strict';
import { citationCheck } from './grading.mjs';

test('synthetic memory IDs cannot masquerade as retrieved knowledge citations', () => {
  const sources=[{kind:'memory',id:'memory-1'},{kind:'knowledge',id:'guide',citation:'K:guide:0'}];
  assert.equal(citationCheck('发布代号是青鹭[K:memory-1:0]',sources).pass,false);
  assert.equal(citationCheck('端口46321[K:guide:0]',sources).pass,true);
  assert.equal(citationCheck('端口46321[K:guide:99]',sources).pass,false);
});

test('valid-looking citations do not override invalid citations later in the same answer', () => {
  const result=citationCheck('说明[K:guide:0]，另见[K:invented:0]',[{kind:'knowledge',citation:'K:guide:0'}]);
  assert.equal(result.pass,false);
  assert.deepEqual(result.invalid_citations,['K:invented:0']);
  assert.equal(citationCheck('没有资料，不能确定。',[]).pass,true);
});
