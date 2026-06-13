// Closure-bound worker. NDJSON query in -> {"v":,"star":0/1,"anchors":[Q-ids],"types":[Q-ids]}.
// star=1 if the query uses any */+ property path. anchors = object Q-ids of triples
// whose predicate path contains a */+ over wdt:P279 (subclass-of) -- i.e. exactly the
// classes whose subclasses a closure/answer-based notion of "use" would additionally credit.
// types = explicit class-position references (objects of P31/P279, incl. paths) so the
// driver can subtract already-named types and report a TIGHT closure-addition bound.
const readline = require('readline');
const { Parser } = require('sparqljs');
const parser = new Parser({ baseIRI: 'http://www.wikidata.org/entity/' });
const P279 = 'http://www.wikidata.org/prop/direct/P279';
const P31 = 'http://www.wikidata.org/prop/direct/P31';
const SUBCLASS = new Set([P279, 'http://www.w3.org/2000/01/rdf-schema#subClassOf']);
const TYPEPROPS = new Set([P31, P279, 'http://www.w3.org/2000/01/rdf-schema#subClassOf']);
const QID = /wikidata\.org\/entity\/(Q\d+)$/;
function pathHasType(p){ if(!p)return false; if(p.termType==='NamedNode')return TYPEPROPS.has(p.value);
  if(p.items)return p.items.some(pathHasType); return false; }
let usesStar = false;
// does this path subtree contain a NamedNode in SUBCLASS?
function hasSubclass(p){ if(!p) return false; if(p.termType==='NamedNode') return SUBCLASS.has(p.value);
  if(p.items) return p.items.some(hasSubclass); return false; }
// does this path subtree contain a */+ node whose subtree references the subclass property?
function starOverSubclass(p){ if(!p||typeof p!=='object') return false;
  if(p.type==='path'){ if((p.pathType==='*'||p.pathType==='+') && hasSubclass(p)) return true;
    if(p.items) return p.items.some(starOverSubclass); }
  return false; }
function anyStar(p){ if(!p||typeof p!=='object') return false;
  if(p.type==='path'){ if(p.pathType==='*'||p.pathType==='+') usesStar=true;
    if(p.items) p.items.forEach(anyStar); } return false; }
function walk(node,triples){
  if(Array.isArray(node)){for(const n of node)walk(n,triples);return;}
  if(node&&typeof node==='object'){
    if(Array.isArray(node.triples))for(const t of node.triples)triples.push(t);
    if(Array.isArray(node.template))for(const t of node.template)triples.push(t);
    for(const k of Object.keys(node)){if(k==='triples'||k==='template')continue;walk(node[k],triples);}
  }
}
function extract(query){
  usesStar=false; let parsed; try{parsed=parser.parse(query);}catch(e){return {v:0,star:0,anchors:[],types:[]};}
  const triples=[]; walk(parsed,triples); const anchors=new Set(); const types=new Set();
  for(const t of triples){
    const p=t.predicate;
    let isType=false;
    if(p&&p.termType==='NamedNode') isType=TYPEPROPS.has(p.value);
    else if(p&&typeof p==='object'&&p.type==='path'){
      anyStar(p); isType=pathHasType(p);
      if(starOverSubclass(p)&&t.object&&t.object.termType==='NamedNode'){
        const m=QID.exec(t.object.value); if(m) anchors.add(m[1]);
      }
    }
    if(isType&&t.object&&t.object.termType==='NamedNode'){
      const m=QID.exec(t.object.value); if(m) types.add(m[1]);
    }
  }
  return {v:1,star:usesStar?1:0,anchors:[...anchors],types:[...types]};
}
const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
const out=[];
rl.on('line',l=>{let q;try{q=JSON.parse(l)}catch(e){out.push('{"v":0,"star":0,"anchors":[],"types":[]}');return;}
  out.push(JSON.stringify(extract(q)));
  if(out.length>=5000){process.stdout.write(out.join('\n')+'\n');out.length=0;}});
rl.on('close',()=>{if(out.length)process.stdout.write(out.join('\n')+'\n');});
