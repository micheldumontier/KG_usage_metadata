// Classify Wikidata entity references by query position.
// NDJSON in (JSON-encoded query) -> {"v":0|1,"cls":[Qids used as object of P31/P279],
//   "ents":[all Qids referenced as subject/object]}.
// An entity is "class-position" if it is the object of a triple whose predicate is
// wdt:P31 or wdt:P279, OR a property path that contains P31/P279 (e.g. P31/P279*).
const readline = require('readline');
const { Parser } = require('sparqljs');
const parser = new Parser({ baseIRI: 'http://www.wikidata.org/' });
const TYPEPROPS = new Set([
  'http://www.wikidata.org/prop/direct/P31',
  'http://www.wikidata.org/prop/direct/P279',
]);
function pathHasType(p) {
  if (!p) return false;
  if (p.termType === 'NamedNode') return TYPEPROPS.has(p.value);
  if (p.items) return p.items.some(pathHasType);
  return false;
}
function qid(t){ const m=t&&t.value&&t.value.match(/\/entity\/(Q\d+)$/); return m?m[1]:null; }
function walk(node, triples){
  if (Array.isArray(node)){ for(const n of node) walk(n,triples); return; }
  if (node && typeof node==='object'){
    if (Array.isArray(node.triples)) for(const t of node.triples) triples.push(t);
    if (Array.isArray(node.template)) for(const t of node.template) triples.push(t);
    for(const k of Object.keys(node)){ if(k==='triples'||k==='template') continue; walk(node[k],triples); }
  }
}
function extract(query){
  let parsed; try{ parsed=parser.parse(query);}catch(e){ return {v:0,cls:[],ents:[]}; }
  const triples=[]; walk(parsed,triples);
  const cls=new Set(), ents=new Set();
  for(const t of triples){
    const so=qid(t.subject), oo=qid(t.object);
    if(so) ents.add(so); if(oo) ents.add(oo);
    const p=t.predicate;
    const isType = (p&&p.termType==='NamedNode'&&TYPEPROPS.has(p.value)) || (p&&(p.type==='path'||p.pathType)&&pathHasType(p));
    if(isType && oo) cls.add(oo);
  }
  return {v:1, cls:[...cls], ents:[...ents]};
}
const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
const out=[];
rl.on('line',l=>{ let q; try{q=JSON.parse(l)}catch(e){out.push('{"v":0,"cls":[],"ents":[]}');return;}
  out.push(JSON.stringify(extract(q)));
  if(out.length>=5000){process.stdout.write(out.join('\n')+'\n');out.length=0;} });
rl.on('close',()=>{ if(out.length)process.stdout.write(out.join('\n')+'\n'); });
