// Variable-invariant query fingerprint, for matching logged queries to WDQS example
// templates (example-query contamination, R2). NDJSON query in -> {"v":,"fp":"<sha1>","nt":<#content-triples>}.
// Canonical form: content triples (BGP), variables->?v, literals->?lit, blanks->_:b, IRIs kept;
// label-service / Blazegraph plumbing (wikibase:, bigdata:) excluded; triples sorted; sha1 hashed.
// A standard WDQS prefix header is injected so prefixed example queries parse (harmless for
// logged queries, which use full IRIs).
const readline = require('readline');
const crypto = require('crypto');
const { Parser } = require('sparqljs');
const PREFIXES = `
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wdtn: <http://www.wikidata.org/prop/direct-normalized/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX pqv: <http://www.wikidata.org/prop/qualifier/value/>
PREFIX pr: <http://www.wikidata.org/prop/reference/>
PREFIX prv: <http://www.wikidata.org/prop/reference/value/>
PREFIX wdref: <http://www.wikidata.org/reference/>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX wdv: <http://www.wikidata.org/value/>
PREFIX wdno: <http://www.wikidata.org/prop/novalue/>
PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX bds: <http://www.bigdata.com/rdf/search#>
PREFIX hint: <http://www.bigdata.com/queryHints#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
`;
const parser = new Parser({ baseIRI: 'http://www.wikidata.org/entity/' });
const PLUMB = ['http://wikiba.se/', 'http://www.bigdata.com/'];
function isPlumb(v){ return typeof v==='string' && PLUMB.some(p=>v.startsWith(p)); }
function term(t){ if(!t) return '?v';
  if(t.termType==='NamedNode') return '<'+t.value+'>';
  if(t.termType==='Literal') return '"?lit"';
  return '?v'; } // Variable or BlankNode
function pathStr(p){ if(!p) return '?v';
  if(p.termType==='NamedNode') return '<'+p.value+'>';
  if(p.type==='path'){ return (p.pathType||'/')+'('+(p.items||[]).map(pathStr).join(',')+')'; }
  return '?v'; }
function predHasPlumb(p){ if(!p) return false;
  if(p.termType==='NamedNode') return isPlumb(p.value);
  if(p.items) return p.items.some(predHasPlumb); return false; }
function walk(node,triples){
  if(Array.isArray(node)){for(const n of node)walk(n,triples);return;}
  if(node&&typeof node==='object'){
    if(Array.isArray(node.triples))for(const t of node.triples)triples.push(t);
    if(Array.isArray(node.template))for(const t of node.template)triples.push(t);
    for(const k of Object.keys(node)){if(k==='triples'||k==='template')continue;walk(node[k],triples);}
  }
}
function extract(q){
  let parsed; try{parsed=parser.parse(PREFIXES+q);}catch(e){return {v:0,fp:'',nt:0};}
  const triples=[]; walk(parsed,triples);
  const strs=[];
  for(const t of triples){
    const p=t.predicate;
    // skip label-service / blazegraph plumbing triples
    if(p&&p.termType==='NamedNode'&&isPlumb(p.value)) continue;
    if(p&&typeof p==='object'&&p.type==='path'&&predHasPlumb(p)) continue;
    if((t.subject&&isPlumb(t.subject.value))||(t.object&&isPlumb(t.object.value))) continue;
    const ps=(p&&typeof p==='object'&&p.type==='path')?pathStr(p):term(p);
    strs.push(term(t.subject)+' '+ps+' '+term(t.object));
  }
  if(!strs.length) return {v:1,fp:'',nt:0};
  strs.sort();
  const fp=crypto.createHash('sha1').update(strs.join('\n')).digest('hex');
  return {v:1,fp,nt:strs.length};
}
const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
const out=[];
rl.on('line',l=>{let q;try{q=JSON.parse(l)}catch(e){out.push('{"v":0,"fp":"","nt":0}');return;}
  out.push(JSON.stringify(extract(q)));
  if(out.length>=5000){process.stdout.write(out.join('\n')+'\n');out.length=0;}});
rl.on('close',()=>{if(out.length)process.stdout.write(out.join('\n')+'\n');});
