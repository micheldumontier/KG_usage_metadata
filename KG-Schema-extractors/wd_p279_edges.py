"""Extract the Wikidata P279 (subclass-of) edge list from a Turtle dump on stdin.
Subjects start at column 0 as `wd:Qn ...`; predicate lines are tab-indented; P279 objects
may be comma-continued. Emits `child parent` (Q-id) pairs to OUT for closure computation.
Usage: gzcat wikidata-20170821.ttl.gz | python3 wd_p279_edges.py 2017"""
import sys, re
ENT=re.compile(r'wd:(Q\d+)')
SUBJ=re.compile(r'^wd:(Q\d+)\b')
year=sys.argv[1]
cur=None; in_p279=False; edges=0; n=0
out=open(f"generated-usage-metadata/wikidata-schema/p279_edges_{year}.tsv","w")
for line in sys.stdin:
    n+=1
    if line[:1] not in (' ','\t'):           # possible new subject (col-0)
        m=SUBJ.match(line)
        if m: cur=m.group(1); in_p279=False
    s=line.strip()
    if s.startswith('wdt:P279 '):
        if cur:
            for o in ENT.findall(s[len('wdt:P279'):]):
                out.write(f"{cur}\t{o}\n"); edges+=1
        in_p279=s.endswith(',')
    elif in_p279:                              # comma-continued object list
        if cur:
            for o in ENT.findall(s):
                out.write(f"{cur}\t{o}\n"); edges+=1
        in_p279=s.endswith(',')
out.close()
print(f"{year}: {edges:,} P279 edges over {n:,} lines -> p279_edges_{year}.tsv",flush=True)
