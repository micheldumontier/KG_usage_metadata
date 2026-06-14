import gzip, glob, re, os, urllib.parse, collections
D=os.path.expanduser("~/data/bio2rdf.logs/bio2rdf.sparql.log.all")
OUT=os.path.expanduser("~/data/bio2rdf.logs/derived")
files=sorted(glob.glob(D+"/bio2rdf.log.*.gz"))
MON={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
DATE=re.compile(rb'\[(\d{2})/([A-Za-z]{3})/(\d{4}):')
ua_re=re.compile(rb'" 200 \d+ \d+ "[^"]*" "([^"]*)"')
q_re=re.compile(rb'[?&]query=([^& ]*)')
BROWSER=re.compile(rb'Mozilla.*(Firefox|Chrome|Safari|MSIE|Trident|Edge|Gecko/2010)',re.I)
# R3 deployed mid-2014 (build dates Jun-Sep 2014). Boundary: Aug 2014.
def period(y,m): return 'r2' if (y<2014 or (y==2014 and m<8)) else 'r3'
fr2=open(OUT+"/organic_r2period.txt","w"); fr3=open(OUT+"/organic_r3period.txt","w")
mon=collections.Counter(); n={'r2':0,'r3':0}
for fp in files:
    with gzip.open(fp,'rb') as f:
        for line in f:
            if b'/sparql?' not in line or b'query=' not in line or b'" 200 ' not in line: continue
            m=ua_re.search(line)
            if not m or not BROWSER.search(m.group(1)): continue
            dm=DATE.search(line)
            if not dm: continue
            y=int(dm.group(3)); mo=MON.get(dm.group(2).decode(),0)
            if not mo: continue
            p=period(y,mo); mon[(y,mo)]+=1
            qm=q_re.search(line)
            if not qm: continue
            try: q=urllib.parse.unquote_plus(qm.group(1).decode('latin-1')).replace("\n"," ").replace("\r"," ")
            except Exception: continue
            (fr2 if p=='r2' else fr3).write(q+"\n"); n[p]+=1
fr2.close(); fr3.close()
print(f"organic R2-period (<2014-08): {n['r2']:,}  -> organic_r2period.txt")
print(f"organic R3-period (>=2014-08): {n['r3']:,} -> organic_r3period.txt")
print("monthly organic counts:")
for k in sorted(mon): print(f"  {k[0]}-{k[1]:02d}: {mon[k]:,}")
