"""Extract a version-matched Bio2RDF schema (TSE) from a release's per-dataset
*-statistics.nt.gz metric files (dataset_vocabulary:has_type -> classes,
:has_predicate -> predicates). Used to measure 2013-query coverage against the
Release 2 schema actually queried, instead of the 2024 endpoint.
Usage: python3 bio2rdf_release_schema.py <stats_dir> <out_prefix>"""
import sys, gzip, glob, os, re
HAS_TYPE=re.compile(rb'dataset_vocabulary:has_type>\s+<(http://bio2rdf\.org/[^>]+)>')
HAS_PRED=re.compile(rb'dataset_vocabulary:has_predicate>\s+<(http://bio2rdf\.org/[^>]+)>')
VOC=re.compile(r'^http://bio2rdf\.org/([A-Za-z0-9_.\-]+)_vocabulary:(.+)$')
stats_dir=sys.argv[1]; out=sys.argv[2]
types=set(); preds=set()
for fp in sorted(glob.glob(os.path.join(stats_dir,"*.nt.gz"))):
    with gzip.open(fp,'rb') as f:
        for line in f:
            for m in HAS_TYPE.finditer(line):
                iri=m.group(1).decode('utf-8','ignore')
                v=VOC.match(iri)
                if v and v.group(1)!='dataset' and v.group(2)!='Resource': types.add(iri)
            for m in HAS_PRED.finditer(line):
                iri=m.group(1).decode('utf-8','ignore')
                v=VOC.match(iri)
                if v and v.group(1)!='dataset': preds.add(iri)
ds=set(VOC.match(e).group(1) for e in types|preds)
open(out+"_types.txt","w").write("\n".join(sorted(types)))
open(out+"_predicates.txt","w").write("\n".join(sorted(preds)))
print(f"datasets: {len(ds)}  types: {len(types)}  predicates: {len(preds)}  TSE: {len(types)+len(preds)}")
print("datasets:", " ".join(sorted(ds)))
