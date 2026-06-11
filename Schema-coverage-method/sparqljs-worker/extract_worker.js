// sparqljs extraction worker.
// Reads NDJSON from stdin: one JSON-encoded *preprocessed* query string per line.
// Writes NDJSON to stdout, one result per input line, in order:
//   {"v":0|1, "iris":[...subject/object NamedNodes...], "preds":[...predicate IRIs...], "path":0|1}
// v=1 valid (parsed), v=0 invalid. preds includes every NamedNode inside property paths.
const readline = require('readline');
const { Parser } = require('sparqljs');
// Use the same base IRI as the rdflib backend (and as the Virtuoso endpoint would), so
// relative IRIs in logged queries (e.g. <no-such-g-qazxswedc>) resolve instead of failing.
const parser = new Parser({ baseIRI: 'http://bio2rdf.org/' });

function collectPathIris(path, preds) {
  // sparqljs path: {type:'path', pathType:'/|*|+|?|^|!', items:[...]}
  if (!path) return;
  if (path.termType === 'NamedNode') { preds.add(path.value); return; }
  if (path.items) for (const it of path.items) collectPathIris(it, preds);
}

function walk(node, triples) {
  if (Array.isArray(node)) { for (const n of node) walk(n, triples); return; }
  if (node && typeof node === 'object') {
    if (Array.isArray(node.triples)) for (const t of node.triples) triples.push(t);
    if (Array.isArray(node.template)) for (const t of node.template) triples.push(t);
    for (const k of Object.keys(node)) {
      if (k === 'triples' || k === 'template') continue;
      walk(node[k], triples);
    }
  }
}

function extract(query) {
  let parsed;
  try { parsed = parser.parse(query); }
  catch (e) { return { v: 0, iris: [], preds: [], path: 0 }; }
  const triples = [];
  walk(parsed, triples);
  const iris = new Set(), preds = new Set();
  let usesPath = 0;
  for (const t of triples) {
    if (t.subject && t.subject.termType === 'NamedNode') iris.add(t.subject.value);
    if (t.object  && t.object.termType  === 'NamedNode') iris.add(t.object.value);
    const p = t.predicate;
    if (p && p.termType === 'NamedNode') preds.add(p.value);
    else if (p && (p.type === 'path' || p.pathType)) { usesPath = 1; collectPathIris(p, preds); }
  }
  return { v: 1, iris: [...iris], preds: [...preds], path: usesPath };
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
const out = [];
rl.on('line', (line) => {
  if (line === '') { out.push('{"v":0,"iris":[],"preds":[],"path":0}'); return; }
  let q;
  try { q = JSON.parse(line); } catch (e) { out.push('{"v":0,"iris":[],"preds":[],"path":0}'); return; }
  out.push(JSON.stringify(extract(q)));
  if (out.length >= 5000) { process.stdout.write(out.join('\n') + '\n'); out.length = 0; }
});
rl.on('close', () => { if (out.length) process.stdout.write(out.join('\n') + '\n'); });
