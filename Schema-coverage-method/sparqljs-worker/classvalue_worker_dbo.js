// DBpedia class/value worker. NDJSON in -> {"v":,"cls":[type-object IRIs],
//   "ents":[all subject/object IRIs],"preds":[predicate IRIs]}.
// Type-properties for DBpedia: rdf:type and rdfs:subClassOf.
const readline = require('readline');
const { Parser } = require('sparqljs');
const parser = new Parser({ baseIRI: 'http://dbpedia.org/' });
const TYPEPROPS = new Set([
  'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
  'http://www.w3.org/2000/01/rdf-schema#subClassOf',
]);
function pathHasType(p){ if(!p)return false; if(p.termType==='NamedNode')return TYPEPROPS.has(p.value);
  if(p.items)return p.items.some(pathHasType); return false; }
function collectPathIris(p,s){ if(!p)return; if(p.termType==='NamedNode'){s.add(p.value);return;}
  if(p.items)for(const it of p.items)collectPathIris(it,s); }
function walk(node,triples){
  if(Array.isArray(node)){for(const n of node)walk(n,triples);return;}
  if(node&&typeof node==='object'){
    if(Array.isArray(node.triples))for(const t of node.triples)triples.push(t);
    if(Array.isArray(node.template))for(const t of node.template)triples.push(t);
    for(const k of Object.keys(node)){if(k==='triples'||k==='template')continue;walk(node[k],triples);}
  }
}
function extract(query){
  let parsed; try{parsed=parser.parse(query);}catch(e){return {v:0,cls:[],ents:[],preds:[]};}
  const triples=[]; walk(parsed,triples);
  const cls=new Set(),ents=new Set(),preds=new Set();
  for(const t of triples){
    if(t.subject&&t.subject.termType==='NamedNode')ents.add(t.subject.value);
    if(t.object&&t.object.termType==='NamedNode')ents.add(t.object.value);
    const p=t.predicate;
    let isType=false;
    if(p&&p.termType==='NamedNode'){preds.add(p.value);isType=TYPEPROPS.has(p.value);}
    else if(p&&(p.type==='path'||p.pathType)){collectPathIris(p,preds);isType=pathHasType(p);}
    if(isType&&t.object&&t.object.termType==='NamedNode')cls.add(t.object.value);
  }
  return {v:1,cls:[...cls],ents:[...ents],preds:[...preds]};
}
const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
const out=[];
rl.on('line',l=>{let q;try{q=JSON.parse(l)}catch(e){out.push('{"v":0,"cls":[],"ents":[],"preds":[]}');return;}
  out.push(JSON.stringify(extract(q)));
  if(out.length>=5000){process.stdout.write(out.join('\n')+'\n');out.length=0;}});
rl.on('close',()=>{if(out.length)process.stdout.write(out.join('\n')+'\n');});
