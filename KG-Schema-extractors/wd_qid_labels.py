"""Extract English rdfs:label for a set of Wikidata QIDs from a period-matched dump.

Figure 8 (top frequent schema types) labels the Wikidata panels with natural-language names
alongside QIDs. Those names must come from the dump for the log period rather than from live
Wikidata: labels change over time (Q1004 is "comic" in the 2017 dump but "comics" today), and
a figure describing 2017 logs should carry 2017 names.

Usage:
    python3 KG-Schema-extractors/wd_qid_labels.py \
        data/kg/wikidata-20170821.ttl.gz \
        generated-usage-metadata/wikidata-schema/qid_labels_en.tsv [Q5 Q515 ...]

With no QID list, the QIDs are those appearing in the top-10 types of each Wikidata panel of
Figure 8, read from the committed per-element count files.

Implementation note: the dump is ~20 GB gzipped (~250 GB of Turtle), so this is a single
streaming pass and the inner loop matters. We read large binary chunks and locate the fixed
byte string b" a wikibase:Item ;" with bytes.find (a memmem-class search, GB/s), then test only
the ~40M entity headers that hit against a set. Do NOT use `grep -F -f patterns -A N` here:
BSD grep with a pattern file plus context lines runs orders of magnitude slower than the
decompressor and does not finish in practical time on this input.
"""
import csv, os, re, subprocess, sys

HDR = b" a wikibase:Item ;"
LABEL_RE = re.compile(rb'rdfs:label "([^"]*)"@en ;')
CHUNK  = 1 << 24         # 16 MiB
WINDOW = 1 << 17         # search 128 KiB past an entity header for its @en label: heavily
                         # labelled items (e.g. Q33999 actor) carry hundreds of language
                         # variants, so the English one can sit far into the block
TAIL   = 1 << 18         # retain 256 KiB of overlap so a block is never split mid-search

def panel_qids(D="generated-usage-metadata"):
    QID = re.compile(r'/entity/(Q\d+)$')
    need = set()
    for f in os.listdir(D):
        if not (f.startswith("Wikidata") and f.endswith("_combined_schema_elements.csv")): continue
        rows = []
        with open(os.path.join(D, f)) as fh:
            r = csv.reader(fh); next(r)
            for row in r:
                m = QID.search(row[0].strip())
                if m:
                    try: rows.append((int(float(row[1])), m.group(1)))
                    except ValueError: pass
        rows.sort(reverse=True)
        need.update(q for _, q in rows[:10])
    return sorted(need, key=lambda q: int(q[1:]))

def main():
    dump, out = sys.argv[1], sys.argv[2]
    qids = sys.argv[3:] or panel_qids()
    want = {q.encode() for q in qids}
    lab, buf = {}, b""
    gz = subprocess.Popen(["gzip", "-dc", dump], stdout=subprocess.PIPE, bufsize=CHUNK)
    try:
        while want:
            chunk = gz.stdout.read(CHUNK)
            if not chunk: break
            buf += chunk
            pos = 0
            while True:
                i = buf.find(HDR, pos)
                if i < 0: break
                nl = buf.rfind(b"\n", 0, i)
                qid = buf[nl + 1:i] if nl >= 0 else buf[:i]
                if qid.startswith(b"wd:") and qid[3:] in want:
                    m = LABEL_RE.search(buf, i, i + WINDOW)
                    if m:
                        q = qid[3:]
                        lab[q.decode()] = m.group(1).decode("utf-8", "replace")
                        want.discard(q)
                pos = i + len(HDR)
            buf = buf[-TAIL:] if len(buf) > TAIL else buf
    finally:
        gz.kill(); gz.stdout.close()
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for q in qids:
            if q in lab: f.write("%s\t%s\n" % (q, lab[q]))
    print("wrote %s: %d/%d labels" % (out, len(lab), len(qids)))
    miss = [q for q in qids if q not in lab]
    if miss: print("MISSING (not found in dump):", " ".join(miss))

if __name__ == "__main__":
    main()
