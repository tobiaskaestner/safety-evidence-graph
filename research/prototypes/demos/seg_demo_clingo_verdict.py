from clingo import Control
import copy

# ---- SEG core (same shape as the SHACL/Datalog demos): identities, types, states ----
core = {
  "nodes": [("r1","requirement"),("r2","requirement"),("r3","requirement"),
            ("ts1","test_specification"),("impl1","implementation"),("to1","test_outcome")],
  "edges": [("refines","r1","r3","active"),("refines","r2","r3","active"),
            ("verifies","ts1","r1","active"),("implements","impl1","r1","active"),
            ("verifies","ts1","r2","active"),("implements","impl1","r2","active")],
}

# ---- PROJECTION: core -> ASP facts (write-only, one-directional) ----
def project_asp(core) -> str:
    lines=[]
    for nid,typ in core["nodes"]:
        lines.append(f"node({nid},{typ}).")
    for et,f,t,st in core["edges"]:
        lines.append(f"edge({et},{f},{t}).")
        lines.append(f"state({et},{f},{t},{st}).")
    return "\n".join(lines)

# ---- FIXED RULES: satisfaction + suspicion, as stratified-Datalog-in-ASP ----
RULES = """
has_child(P) :- edge(refines, _, P).
leaf(R)      :- node(R, requirement), not has_child(R).
active_in(T, Tgt) :- state(T, _, Tgt, active).

% satisfaction (well-defined ONLY when refines is acyclic -> locally stratified)
satisfied(R) :- leaf(R), active_in(verifies, R), active_in(implements, R).
unsat_child(P) :- edge(refines, C, P), not satisfied(C).
satisfied(P) :- has_child(P), node(P, requirement), not unsat_child(P).

% suspicion: seed from a suspect edge, propagate UP refines (positive recursion)
susp_edge(T,F,To) :- state(T,F,To,suspect).
tainted(Tgt) :- susp_edge(_, _, Tgt).
tainted(P)   :- edge(refines, C, P), tainted(C).

#show satisfied/1.
#show tainted/1.
"""

def run(label, core):
    prog = project_asp(core) + "\n" + RULES
    ctl = Control()
    ctl.configuration.solve.models = 0          # enumerate ALL answer sets
    ctl.add("base", [], prog)
    ctl.ground([("base", [])])
    models=[]
    ctl.solve(on_model=lambda m: models.append([str(s) for s in m.symbols(shown=True)]))

    print(f"=== {label} ===")
    print(f"  answer sets returned: {len(models)}")
    # GUARDRAIL: a SEG verdict must be a single deterministic answer set.
    if len(models) != 1:
        print("  !! DETERMINISM VIOLATED — not exactly one answer set.")
        print("     (program left the stratified fragment; verdict is undefined.)")
        print()
        return
    atoms = models[0]
    sat = sorted(a[len("satisfied("):-1] for a in atoms if a.startswith("satisfied("))
    tnt = sorted(a[len("tainted("):-1]   for a in atoms if a.startswith("tainted("))
    print(f"  satisfied : {sat}")
    print(f"  tainted   : {tnt}")
    print()

# 1. all active, acyclic refines
run("all edges active (acyclic)", core)

# 2. core recomputed verifies(ts1->r1) as suspect
d = copy.deepcopy(core)
d["edges"] = [(et,f,t,"suspect") if (et,f,t)==("verifies","ts1","r1") else (et,f,t,st)
              for (et,f,t,st) in d["edges"]]
run("verifies(ts1->r1) suspect (acyclic)", d)

# 3. VIOLATE the acyclic facet: add refines r3->r1, making r1<->r3 a cycle.
c = copy.deepcopy(core)
c["edges"].append(("refines","r3","r1","active"))
run("refines cycle injected (acyclic facet VIOLATED)", c)
