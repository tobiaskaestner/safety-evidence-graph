"""Store generator for SEG prototype graphs of varying sizes.

Public API:
    generate(cfg: GenConfig) -> list[dict]

All generated graphs are consistent: every leaf requirement has ≥1 active
Implements edge, ≥1 active Verifies edge, and every confirming outcome is
PASS at the majority SHA — so every requirement is satisfied and
generate_proof() returns "ready".

Scenarios included beyond the basic 1-impl / 1-spec pattern:
  - multi_impl_ratio  fraction of leaf reqs that get a second implementation
  - cross_req_ratio   fraction of test specs that verify 2 leaf reqs (integration tests)
  - max_outcomes_per_test_case > 1 gives multiple run outcomes per spec
"""
from __future__ import annotations

import random
from dataclasses import dataclass

REPO_SHA = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"


@dataclass
class GenConfig:
    num_sys_reqs: int
    max_reqs_per_sys_req: int
    max_test_cases_per_req: int = 2
    max_outcomes_per_test_case: int = 1
    seed: int = 42
    multi_impl_ratio: float = 0.15   # fraction of leaf reqs with a second impl
    cross_req_ratio: float = 0.05    # fraction of test specs that are cross-req


def generate(cfg: GenConfig) -> list[dict]:
    rng = random.Random(cfg.seed)
    items: list[dict] = []

    leaf_reqs: list[str] = []
    primary_impl_id:   dict[str, str] = {}   # req_id → IMPL-xxxxxx
    primary_impl_name: dict[str, str] = {}   # req_id → function name

    impl_seq = 1
    ts_seq   = 1

    # ── System and leaf requirements ──────────────────────────────────────────
    for i in range(1, cfg.num_sys_reqs + 1):
        sys_id = f"SYS-REQ-{i:04d}"
        items.append({
            "id":   sys_id,
            "type": "Requirement",
            "name": sys_id,
            "to_hash": {
                "nodeHash": (
                    f"System requirement {i:04d}: the system shall satisfy "
                    f"all sub-requirements of SYS-REQ-{i:04d}."
                )
            },
        })
        n_reqs = rng.randint(1, cfg.max_reqs_per_sys_req)
        for j in range(1, n_reqs + 1):
            req_id = f"REQ-{i:04d}-{j:03d}"
            items.append({
                "id":   req_id,
                "type": "Requirement",
                "name": req_id,
                "to_hash": {
                    "nodeHash": (
                        f"Software requirement {i:04d}.{j:03d}: the module shall "
                        f"perform operation {i}-{j} as specified by SYS-REQ-{i:04d}."
                    )
                },
                "refines": [sys_id],
            })
            leaf_reqs.append(req_id)

    # ── Implementations ───────────────────────────────────────────────────────
    for req_id in leaf_reqs:
        impl_id   = f"IMPL-{impl_seq:06d}"
        impl_name = f"impl_{impl_seq:06d}"
        items.append(_impl_item(impl_id, impl_name, req_id, impl_seq))
        primary_impl_id[req_id]   = impl_id
        primary_impl_name[req_id] = impl_name
        impl_seq += 1

        if rng.random() < cfg.multi_impl_ratio:
            alt_id   = f"IMPL-{impl_seq:06d}"
            alt_name = f"impl_{impl_seq:06d}_alt"
            items.append(_impl_item(alt_id, alt_name, req_id, impl_seq, alt=True))
            impl_seq += 1

    # ── Test specifications and outcomes ──────────────────────────────────────
    for req_id in leaf_reqs:
        n_ts = rng.randint(1, cfg.max_test_cases_per_req)
        for k in range(n_ts):
            ts_id = f"TS-{ts_seq:06d}"
            fn    = primary_impl_name[req_id]
            items.append({
                "id":   ts_id,
                "type": "TestSpecification",
                "name": ts_id,
                "to_hash": {
                    "specHash": f"Verify {req_id} behaviour, case {k + 1}.",
                    "implHash": f"    assert {fn}() is True  # case {k + 1}",
                },
                "verifies": [req_id],
            })
            n_out = rng.randint(1, cfg.max_outcomes_per_test_case)
            for m in range(1, n_out + 1):
                items.append(
                    _outcome_item(f"RUN-{m:03d}", ts_id, primary_impl_id[req_id])
                )
            ts_seq += 1

    # ── Cross-requirement (integration) test specs ────────────────────────────
    if len(leaf_reqs) >= 2:
        n_cross   = max(1, round(len(leaf_reqs) * cfg.cross_req_ratio))
        seen: set[tuple[str, str]] = set()
        added = attempts = 0
        while added < n_cross and attempts < n_cross * 20:
            attempts += 1
            r1, r2 = rng.sample(leaf_reqs, 2)
            pair   = (min(r1, r2), max(r1, r2))
            if pair in seen:
                continue
            seen.add(pair)
            ts_id = f"TS-{ts_seq:06d}"
            fn1   = primary_impl_name[r1]
            fn2   = primary_impl_name[r2]
            items.append({
                "id":   ts_id,
                "type": "TestSpecification",
                "name": ts_id,
                "to_hash": {
                    "specHash": (
                        f"Integration test {ts_seq}: verify {r1} and {r2} interact correctly."
                    ),
                    "implHash": f"    assert integration_check({fn1}, {fn2})",
                },
                "verifies": [r1, r2],
            })
            items.append(_outcome_item("RUN-001", ts_id, primary_impl_id[r1]))
            ts_seq += 1
            added += 1

    return items


def _impl_item(
    impl_id: str, name: str, req_id: str, seq: int, alt: bool = False
) -> dict:
    suffix = " (alternative)" if alt else ""
    return {
        "id":   impl_id,
        "type": "Implementation",
        "name": name,
        "to_hash": {
            "apiHash": (
                f"def {name}() -> bool:\n"
                f"    \"\"\":implements: {req_id}{suffix}\"\"\"\n"
            ),
            "bodyHash": f"    return _execute_op_{seq}()",
        },
        "implements": [req_id],
    }


def _outcome_item(run_id: str, ts_id: str, impl_id: str) -> dict:
    oid = f"{run_id}/{ts_id}"
    return {
        "id":       oid,
        "type":     "TestOutcome",
        "name":     oid,
        "runId":    run_id,
        "outcome":  "PASS",
        "repoBSha": REPO_SHA,
        "specId":   ts_id,
        "implId":   impl_id,
        "to_hash":  {"nodeHash": f"{run_id} {ts_id} PASS {REPO_SHA}"},
    }
