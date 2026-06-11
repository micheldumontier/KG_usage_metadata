// Like extract_worker, but reports the parse error message for invalid queries.
// NDJSON in (one JSON-encoded query per line) -> NDJSON out {"v":0|1,"err":"..."}.
const readline = require('readline');
const { Parser } = require('sparqljs');
const parser = new Parser({ baseIRI: 'http://bio2rdf.org/' });
const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
const out = [];
rl.on('line', (line) => {
  let q, res;
  try { q = JSON.parse(line); } catch (e) { out.push('{"v":0,"err":"BAD_LINE"}'); return; }
  try { parser.parse(q); res = { v: 1, err: '' }; }
  catch (e) { res = { v: 0, err: (e.message || '').split('\n')[0] }; }
  out.push(JSON.stringify(res));
  if (out.length >= 5000) { process.stdout.write(out.join('\n') + '\n'); out.length = 0; }
});
rl.on('close', () => { if (out.length) process.stdout.write(out.join('\n') + '\n'); });
