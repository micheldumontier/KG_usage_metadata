// Per-query template features for the query-template linkage analysis.
// NDJSON in (JSON-encoded preprocessed query) -> one result per line:
//   {"v":0|1, "preds":[sorted predicate IRIs], "classes":[class-position IRIs], "ntp":N}
// "template" downstream = the predicate signature (sorted preds).
// "classes" = objects of a type/subclass predicate (env TYPEPROPS, comma-separated IRIs).
// BASEIRI and TYPEPROPS are passed via environment so one worker serves both KGs.
const readline = require('readline');
const { Parser } = require('sparqljs');
const BASE = process.env.BASEIRI || 'http://www.wikidata.org/';
const TYPEPROPS = new Set((process.env.TYPEPROPS ||
  'http://www.wikidata.org/prop/direct/P31,http://www.wikidata.org/prop/direct/P279').split(','));
const parser = new Parser({ baseIRI: BASE });

function pathPreds(p, acc) {            // collect every NamedNode IRI inside a property path
  if (!p) return;
  if (p.termType === 'NamedNode') { acc.add(p.value); return; }
  if (p.items) for (const it of p.items) pathPreds(it, acc);
}
function pathHasType(p) {
  if (!p) return false;
  if (p.termType === 'NamedNode') return TYPEPROPS.has(p.value);
  if (p.items) return p.items.some(pathHasType);
  return false;
}
function walk(node, triples) {
  if (Array.isArray(node)) { for (const n of node) walk(n, triples); return; }
  if (node && typeof node === 'object') {
    if (Array.isArray(node.triples)) for (const t of node.triples) triples.push(t);
    if (Array.isArray(node.template)) for (const t of node.template) triples.push(t);
    for (const k of Object.keys(node)) { if (k === 'triples' || k === 'template') continue; walk(node[k], triples); }
  }
}
function extract(query) {
  let parsed; try { parsed = parser.parse(query); } catch (e) { return { v: 0, preds: [], classes: [], ntp: 0 }; }
  const triples = []; walk(parsed, triples);
  const preds = new Set(), classes = new Set();
  for (const t of triples) {
    const p = t.predicate;
    let isType = false;
    if (p && p.termType === 'NamedNode') { preds.add(p.value); isType = TYPEPROPS.has(p.value); }
    else if (p && (p.type === 'path' || p.pathType)) { pathPreds(p, preds); isType = pathHasType(p); }
    if (isType && t.object && t.object.termType === 'NamedNode') classes.add(t.object.value);
  }
  return { v: 1, preds: [...preds].sort(), classes: [...classes], ntp: triples.length };
}
const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
const out = [];
rl.on('line', l => {
  let q; try { q = JSON.parse(l); } catch (e) { out.push('{"v":0,"preds":[],"classes":[],"ntp":0}'); return; }
  out.push(JSON.stringify(extract(q)));
  if (out.length >= 5000) { process.stdout.write(out.join('\n') + '\n'); out.length = 0; }
});
rl.on('close', () => { if (out.length) process.stdout.write(out.join('\n') + '\n'); });
