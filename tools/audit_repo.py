import os, re, csv, json
ROOT = "."
DOMAINS = {
    "personas": ["persona","traits","icp","profile","archetype","style_vector"],
    "studies": ["study","session","moderator","conductor","turn","followup","run"],
    "insights": ["insight","cluster","theme","quote","sentiment","embedding"],
    "guardrails": ["guardrail","moderation","pii","toxicity","jailbreak","policy"],
    "exports": ["export","csv","yaml","schema_version","checksum","artifact"],
    "dashboard": ["metric","latency","tokens","cost","p95","chart","endpoint","overview"]
}
skip_dirs = {".git","reports",".venv","node_modules","dist","build","__pycache__",".mypy_cache"}

def scan_file(path):
    try:
        with open(path,"r",encoding="utf-8",errors="ignore") as f:
            s=f.read().lower()
    except Exception:
        return {}
    hits={}
    for domain, keywords in DOMAINS.items():
        score=sum(1 for kw in keywords if kw in s)
        if score: hits[domain]=score
    return hits

rows=[]
for root, dirs, files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d not in skip_dirs]
    for fn in files:
        if not re.search(r"\.(py|ts|tsx|js|md)$", fn, re.I): 
            continue
        path=os.path.join(root,fn).replace("\\","/")
        hits=scan_file(path)
        if hits:
            rows.append({"path":path, **{k:hits.get(k,0) for k in DOMAINS}})

os.makedirs("reports",exist_ok=True)
with open("reports/component_inventory.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=["path"]+list(DOMAINS))
    w.writeheader(); w.writerows(rows)

print("Wrote reports/component_inventory.csv with domain scores per file.")

