import gzip, glob, re, os, json, collections, urllib.parse
D=os.path.expanduser("~/data/bio2rdf.logs/bio2rdf.sparql.log.all")
OUT=os.path.expanduser("~/data/bio2rdf.logs/derived")
files=sorted(glob.glob(D+"/bio2rdf.log.*.gz"))
ua_re=re.compile(rb'" 200 \d+ \d+ "[^"]*" "([^"]*)"')
q_re=re.compile(rb'[?&]query=([^& ]*)')
BROWSER=re.compile(rb'Mozilla.*(Firefox|Chrome|Safari|MSIE|Trident|Edge|Gecko/2010)',re.I)
BOT=re.compile(rb'bot|spider|crawl|slurp|sparqles|ahrefs|mj12|baidu|yandex|ltx71|semrush',re.I)
TOOL=re.compile(rb'Java|Jena|Python|curl|wget|httpclient|http_request|apache-http|okhttp|node|ruby|perl|lwp|guzzle',re.I)
comp=collections.Counter(); norg=0
forg=open(OUT+"/organic_2013_queries.txt","w",encoding="utf-8")
for fp in files:
    with gzip.open(fp,'rb') as f:
        for line in f:
            if b'/sparql?' not in line or b'query=' not in line or b'" 200 ' not in line: continue
            m=ua_re.search(line)
            if not m: continue
            ua=m.group(1)
            ip=line.split(b' ',3)[1] if line.count(b' ')>=2 else b''
            galway = ip.startswith(b'140.203.')      # NUI Galway / DERI (LSQ harvest infra)
            if b'compatible; Virtuoso' in ua:        cls='virtuoso_internal'
            elif ua==b'-' and galway:                cls='galway_harvest'
            elif ua==b'-':                           cls='no_agent'
            elif BROWSER.search(ua):                 cls='organic'
            elif BOT.search(ua):                     cls='crawler'
            elif TOOL.search(ua):                    cls='tool'
            else:                                    cls='other'
            comp[cls]+=1
            if cls=='organic':
                qm=q_re.search(line)
                if qm:
                    try: qtxt=urllib.parse.unquote_plus(qm.group(1).decode('latin-1'))
                    except Exception: continue
                    forg.write(qtxt.replace("\n"," ").replace("\r"," ")+"\n"); norg+=1
forg.close()
tot=sum(comp.values())
print(f"executed /sparql (200): {tot:,}")
for k,v in comp.most_common(): print(f"  {k:18s} {v:>11,}  ({100*v/max(1,tot):.2f}%)")
print(f"\norganic query texts written: {norg:,} -> {OUT}/organic_2013_queries.txt")
# infra-excluded denominator (genuine external traffic = drop virtuoso_internal + galway_harvest)
ext=tot-comp['virtuoso_internal']-comp['galway_harvest']
print(f"\ngenuine external traffic (excl. Virtuoso self-calls + Galway harvest): {ext:,}")
for k in ['organic','tool','crawler','no_agent','other']:
    print(f"  {k:18s} {comp[k]:>11,}  ({100*comp[k]/max(1,ext):.2f}% of external)")
