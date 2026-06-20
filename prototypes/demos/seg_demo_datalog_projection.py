# ------------------------------------------------------------
# SEG core -> DATALOG projection, then run satisfaction + suspicion
# as stratified rules. Same core as the SHACL demo; `state` is
# consumed HERE too (the overlap the prism analogy must allow).
# ------------------------------------------------------------
from itertools import product

core = {
  "nodes": [
    {"id":"R1","type":"Requirement"}, {"id":"R2","type":"Requirement"},
    {"id":"R3","type":"Requirement"},  # R3 is the scope root; R1,R2 refine it
    {"id":"TS1","type":"TestSpecification"}, {"id":"IMPL1","type":"Implementation"},
    {"id":"TO1","type":"TestOutcome"},
  ],
  "edges": [
    {"type":"refines","from":"R1","to":"R3","state":"active"},
    {"type":"refines","from":"R2","to":"R3","state":"active"},
    {"type":"verifies","from":"TS1","to":"R1","state":"active"},
    {"type":"implements","from":"IMPL1","to":"R1","state":"active"},
    {"type":"verifies","from":"TS1","to":"R2","state":"active"},
    {"type":"implements","from":"IMPL1","to":"R2","state":"active"},
  ],
}

# ---- PROJECTION: core -> set of ground facts (EDB) ----
def project_facts(core):
    f = set()
    for n in core["nodes"]:
        f.add(("node", n["id"], n["type"]))
    for e in core["edges"]:
        f.add(("edge", e["type"], e["from"], e["to"]))
        f.add(("state", e["type"], e["from"], e["to"], e["state"]))
    return f

# ---- A tiny stratified, semi-naive fixpoint over hand-coded rule fns ----
# Stratum 0: base facts. Each higher stratum reads lower strata to fixpoint.
def stratum_suspect(facts):
    out = set()
    # direct suspicion: any strong edge whose state is 'suspect' (seed)
    for f in facts:
        if f[0]=="state" and f[4]=="suspect":
            out.add(("susp_edge", f[1], f[2], f[3]))
    # transitive: a requirement is tainted if an incident strong edge is suspect,
    # and taint flows UP refines (child->parent). Iterate to fixpoint.
    changed=True
    tainted=set()
    while changed:
        changed=False
        # seed: target requirement of any suspect verifies/implements, or
        # the parent of any suspect refines
        for f in facts | out:
            if f[0]=="susp_edge":
                etype,frm,to=f[1],f[2],f[3]
                tgt = to  # verifies/implements/refines all point toward the requirement/parent
                if tgt not in tainted: tainted.add(tgt); changed=True
        # propagate up refines: if child tainted and child refines parent, parent tainted
        for f in facts:
            if f[0]=="edge" and f[1]=="refines":
                child,parent=f[2],f[3]
                if child in tainted and parent not in tainted:
                    tainted.add(parent); changed=True
    for t in tainted: out.add(("tainted",t))
    return out

def stratum_satisfied(facts):
    # leaf requirement satisfied iff >=1 active verifies AND >=1 active implements
    # non-leaf satisfied iff all children (refines) satisfied
    nodes=[f[1] for f in facts if f[0]=="node" and f[2]=="Requirement"]
    def active(et,tgt):
        return any(f[0]=="state" and f[1]==et and f[3]==tgt and f[4]=="active" for f in facts)
    def children(p):
        return [f[2] for f in facts if f[0]=="edge" and f[1]=="refines" and f[3]==p]
    sat=set(); changed=True
    while changed:
        changed=False
        for r in nodes:
            if ("sat",r) in sat: continue
            ch=children(r)
            if ch:  # non-leaf
                if all(("sat",c) in sat for c in ch):
                    sat.add(("sat",r)); changed=True
            else:   # leaf
                if active("verifies",r) and active("implements",r):
                    sat.add(("sat",r)); changed=True
    return sat

def evaluate(core):
    facts=project_facts(core)
    facts |= stratum_suspect(facts)
    facts |= stratum_satisfied(facts)
    return facts

def report(label, core):
    f=evaluate(core)
    sat=sorted(x[1] for x in f if x[0]=="sat")
    tainted=sorted(x[1] for x in f if x[0]=="tainted")
    print(f"=== {label} ===")
    print("  satisfied :", sat)
    print("  tainted   :", tainted)
    print()

# 1. all active
report("all edges active", core)

# 2. drift: the CORE recomputed verifies(TS1->R1) as 'suspect' (endpoint drifted).
import copy
d=copy.deepcopy(core)
for e in d["edges"]:
    if e["type"]=="verifies" and e["from"]=="TS1" and e["to"]=="R1":
        e["state"]="suspect"
report("verifies(TS1->R1) went suspect", d)
