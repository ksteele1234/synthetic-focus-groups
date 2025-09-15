import os, re, csv, json, subprocess, sys, shutil
from collections import defaultdict
ROOT="."
SKIP={".git",".venv","node_modules","dist","build","__pycache__"}

# ---------- helpers ----------
def run(cmd:list, capture=True):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return (0, out.decode("utf-8","ignore") if capture else "")
    except subprocess.CalledProcessError as e:
        return (e.returncode, e.output.decode("utf-8","ignore") if e.output else "")

def py_files():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fn in files:
            if fn.endswith(".py"):
                yield os.path.join(root,fn).replace("\\","/")

def modname(path):  # naive module name
    return re.sub(r"\.py$","",path).replace("/",".")

# ---------- domain mapping (align to your spec) ----------
DOMAINS = {
    "personas":  ["persona","traits","icp","profile","archetype","style_vector"],
    "studies":   ["study","session","moderator","conductor","turn","followup","run"],
    "insights":  ["insight","cluster","theme","quote","sentiment","embedding"],
    "guardrails":["guardrail","moderation","pii","toxicity","jailbreak","policy"],
    "exports":   ["export","csv","yaml","schema_version","checksum","artifact"],
    "dashboard": ["metric","latency","tokens","cost","p95","chart","endpoint","overview"]
}

def domain_score(path):
    try:
        s=open(path,"r",encoding="utf-8",errors="ignore").read().lower()
    except Exception:
        return {}
    hits={}
    for dom, keys in DOMAINS.items():
        hits[dom]=sum(1 for k in keys if k in s)
    return hits

# ---------- import graph ----------
imports=defaultdict(set)
revdeps=defaultdict(set)
imp_re=re.compile(r"^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))")
for f in py_files():
    try:
        for line in open(f,encoding="utf-8",errors="ignore"):
            m=imp_re.match(line)
            if m:
                t=(m.group(1) or m.group(2)).split()[0]
                if t: imports[modname(f)].add(t)
    except Exception:
        pass
for src, tgts in imports.items():
    for t in tgts:
        revdeps[t].add(src)

# ---------- radon (complexity) ----------
complexity_rank={}
code, out = run(["radon","cc",".","-s","-j"])
if code==0 and out.strip():
    data=json.loads(out)
    for path, blocks in data.items():
        path=path.replace("\\","/")
        ranks=[b.get("rank","A") for b in blocks] if isinstance(blocks,list) else []
        complexity_rank[path]=max(ranks) if ranks else "A"

# ---------- vulture (dead code) ----------
dead=set()
code, out = run(["vulture",".","--min-confidence","80"])
if out:
    for line in out.splitlines():
        if ":" in line and ".py" in line:
            dead.add(line.split(":")[0].replace("\\","/"))

# ---------- bandit (security summary) ----------
bandit_warn=set()
code, out = run(["bandit","-r",".","-q","-f","json"])
if out:
    try:
        b=json.loads(out)
        for issue in b.get("results",[]):
            path=issue.get("filename","").replace("\\","/")
            sev=issue.get("issue_severity","LOW")
            if sev in ("MEDIUM","HIGH"):
                bandit_warn.add(path)
    except Exception:
        pass

# ---------- deptry (deps; optional signal) ----------
dep_issues=set()
if shutil.which("deptry"):
    code, out = run(["deptry",".","--exclude",".venv","--json"])
    if out:
        try:
            d=json.loads(out)
            for item in d.get("report",{}).get("unused",[]):
                for occ in item.get("occurrences",[]):
                    dep_issues.add(occ.get("file","").replace("\\","/"))
            for item in d.get("report",{}).get("missing",[]):
                for occ in item.get("occurrences",[]):
                    dep_issues.add(occ.get("file","").replace("\\","/"))
        except Exception:
            pass

# ---------- suggest decision ----------
def suggest(path):
    dom=domain_score(path)
    hits=sum(dom.values())
    rank=complexity_rank.get(path,"A")
    mod=modname(path)
    used = any(mod==k or mod.startswith(k+".") for k in revdeps.keys())
    is_dead = path in dead
    has_sec = path in bandit_warn
    has_dep = path in dep_issues

    # Heuristics: prefer safety; default to refactor when unsure
    if hits==0 and not used:
        return ("remove","no-domain-match & no dependents", dom, rank, used, is_dead, has_sec, has_dep)
    if is_dead and not used:
        return ("remove","vulture dead-code", dom, rank, used, is_dead, has_sec, has_dep)
    if rank in ("D","E","F") or has_sec or has_dep:
        reason=[]
        if rank in ("D","E","F"): reason.append(f"complexity {rank}")
        if has_sec: reason.append("security findings")
        if has_dep: reason.append("dependency issues")
        return ("refactor","; ".join(reason), dom, rank, used, is_dead, has_sec, has_dep)
    return ("keep",f"domain_hits={hits}, complexity={rank}, used={used}", dom, rank, used, is_dead, has_sec, has_dep)

rows=[]
for f in py_files():
    d, reason, dom, rank, used, deadflag, sec, dep = suggest(f)
    rows.append({
        "path": f,
        "decision": d,
        "reason": reason,
        "dependents_count": len(revdeps.get(modname(f),[])),
        "dependents": ";".join(sorted(revdeps.get(modname(f),[])))[:1000],
        "complexity_rank": rank,
        "domain_personas": dom.get("personas",0),
        "domain_studies": dom.get("studies",0),
        "domain_insights": dom.get("insights",0),
        "domain_guardrails": dom.get("guardrails",0),
        "domain_exports": dom.get("exports",0),
        "domain_dashboard": dom.get("dashboard",0),
        "is_used": used,
        "is_dead_code": deadflag,
        "security_flag": sec,
        "dependency_flag": dep
    })

os.makedirs("reports",exist_ok=True)
with open("reports/triage.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

print("✅ Wrote reports/triage.csv with keep/refactor/remove suggestions and impact.")
print("Open it in Excel and sort by decision, complexity_rank, and dependents_count.")



