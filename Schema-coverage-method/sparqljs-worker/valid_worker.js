// NDJSON in (JSON-encoded query per line) -> "1"/"0" per line (valid/invalid). Fast.
const readline=require('readline');const {Parser}=require('sparqljs');
const p=new Parser({baseIRI:'http://www.wikidata.org/'});
const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
const out=[];
rl.on('line',l=>{let q;try{q=JSON.parse(l)}catch(e){out.push('0');return}
  try{p.parse(q);out.push('1')}catch(e){out.push('0')}
  if(out.length>=20000){process.stdout.write(out.join('\n')+'\n');out.length=0}});
rl.on('close',()=>{if(out.length)process.stdout.write(out.join('\n')+'\n')});
