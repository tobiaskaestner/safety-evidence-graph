"""
seg_commitment.py -- the DEC-012 `flat-openable` seal: a Merkle vector
commitment over the set of per-leaf contract members, supporting partial
openings (O(log n) inclusion proofs).

A member is the content hash of one contract C_i = (G_i, {A_ij}). The hash binds
G_i to its FULL assumption set, so a downstream cannot open the guarantee while
dropping an inconvenient assumption — the recomputed member hash would not match
its inclusion proof against the root.

Leaves are ordered deterministically by contract id (sorted). Internal nodes are
domain-separated with a "node:" prefix; an odd node duplicates the last child.
"""
import hashlib
import json


def _h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def member_hash(contract: dict) -> str:
    """contract = {'G':{'id','statement'}, 'A':[{'id','statement'}...],
    'I':[{'id','sha1'}...]} -> sha256 hex. The hash binds G to its FULL assumption
    set AND its FULL implementation-pin set (DEC-028), so a downstream cannot open
    the guarantee while dropping an assumption or swapping the pinned implementation."""
    payload = {
        "G": [contract["G"]["id"], contract["G"]["statement"]],
        "A": sorted([a["id"], a["statement"]] for a in contract["A"]),
        "I": sorted([i["id"], i["sha1"]] for i in contract.get("I", [])),
    }
    return _h(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def _levels(members: dict):
    """members: {contract_id: member_hash}. Returns (ordered_ids, levels[list of list])."""
    ids = sorted(members)
    cur = [members[i] for i in ids]
    if not cur:
        return ids, [[_h("")]]
    levels = [cur[:]]
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            left = cur[i]
            right = cur[i + 1] if i + 1 < len(cur) else cur[i]  # duplicate last if odd
            nxt.append(_h("node:" + left + right))
        levels.append(nxt)
        cur = nxt
    return ids, levels


def root(members: dict) -> str:
    return _levels(members)[1][-1][0]


def prove(members: dict, contract_id: str):
    """Inclusion proof for one contract: list of (sibling_hash, side)."""
    ids, levels = _levels(members)
    idx = ids.index(contract_id)
    path = []
    for lvl in levels[:-1]:
        sib = idx ^ 1
        sib_hash = lvl[sib] if sib < len(lvl) else lvl[idx]  # duplicated last
        path.append((sib_hash, "R" if idx % 2 == 0 else "L"))
        idx //= 2
    return path


def verify(leaf_hash: str, path, expected_root: str) -> bool:
    h = leaf_hash
    for sib, side in path:
        h = _h("node:" + (h + sib if side == "R" else sib + h))
    return h == expected_root


if __name__ == "__main__":
    # self-test: 3 members, open each, verify; tamper -> reject
    cs = {
        "c1": {"G": {"id": "g1", "statement": "s1"}, "A": [{"id": "a", "statement": "x"}]},
        "c2": {"G": {"id": "g2", "statement": "s2"}, "A": []},
        "c3": {"G": {"id": "g3", "statement": "s3"}, "A": [{"id": "b", "statement": "y"}]},
    }
    mh = {k: member_hash(v) for k, v in cs.items()}
    r = root(mh)
    assert all(verify(mh[k], prove(mh, k), r) for k in cs), "valid openings must verify"
    bad = dict(mh); bad["c1"] = _h("tampered")
    assert not verify(bad["c1"], prove(mh, "c1"), r), "tampered member must reject"
    print("seg_commitment self-test OK; root =", r[:16], "...")
