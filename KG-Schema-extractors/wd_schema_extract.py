import sys, re
ENT=re.compile(r'wd:(Q\d+)')
year=sys.argv[1]
types=set(); preds=set(); n=0; in_typelist=False
for line in sys.stdin:
    n+=1; s=line.strip()
    if s.startswith('wdt:P31 ') or s.startswith('wdt:P279 '):
        types.update(ENT.findall(s)); in_typelist=s.endswith(',')
    elif in_typelist:
        types.update(ENT.findall(s)); in_typelist=s.endswith(',')
    if s.startswith('wdt:P'):
        sp=s.find(' ')
        if sp>0 and 'wd:Q' in s[sp:]: preds.add(s[4:sp])   # strip 'wdt:' -> Pxxx
OUT=f"generated-usage-metadata/wikidata-schema"
with open(f"{OUT}/types_{year}.txt","w") as f: f.write("\n".join(sorted(types)))
with open(f"{OUT}/preds_{year}.txt","w") as f: f.write("\n".join(sorted(preds)))
print(f"{year}: types={len(types):,} preds={len(preds):,} -> saved",flush=True)
