// This verifies citation identifiers, not whether a cited passage entails a claim.
export function citationCheck(answer, sources) {
  const cited = [...String(answer).matchAll(/\[(K:[^\]\r\n]+)\]/g)].map(m => m[1]);
  const allowed = new Set(sources.filter(s => s.kind === 'knowledge').map(s => s.citation));
  const invalid = cited.filter(id => !allowed.has(id));
  return { dimension:'citation', name:'所有知识库引用均来自实际检索结果（不检查语义蕴含）', pass:invalid.length===0, invalid_citations:invalid };
}
