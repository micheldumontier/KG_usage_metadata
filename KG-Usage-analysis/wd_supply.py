import sys, re
ENT=re.compile(r'wd:(Q\d+)')
year=sys.argv[1]
inst={}        # class Q -> #instances (P31 objects)
pred={}        # wdt:Pxxx -> #triples (occurrences)
n=0; in_p31=False
for line in sys.stdin:
    n+=1; s=line.strip()
    if s.startswith('wdt:P31 '):
        for q in ENT.findall(s): inst[q]=inst.get(q,0)+1
        in_p31=s.endswith(',')
    elif in_p31:                      # continuation objects of a P31 list
        for q in ENT.findall(s): inst[q]=inst.get(q,0)+1
        in_p31=s.endswith(',')
    if s.startswith('wdt:P'):
        sp=s.find(' ')
        if sp>0: 
            p=s[4:sp]                 # strip 'wdt:' -> Pxxx
            pred[p]=pred.get(p,0)+1
    if n % 500_000_000==0:
        sys.stderr.write(f"  {n//1_000_000}M; classes={len(inst):,} preds={len(pred):,}\n"); sys.stderr.flush()
B="generated-usage-metadata/wikidata-supply"
import csv
with open(f"{B}/instances_per_class_{year}.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["class","instances"])
    for q,c in sorted(inst.items(),key=lambda x:-x[1]): w.writerow([q,c])
with open(f"{B}/triples_per_pred_{year}.csv","w",newline='') as f:
    w=csv.writer(f); w.writerow(["pred","triples"])
    for p,c in sorted(pred.items(),key=lambda x:-x[1]): w.writerow([p,c])
print(f"{year}: classes-with-instances={len(inst):,} predicates={len(pred):,} (saved)")
