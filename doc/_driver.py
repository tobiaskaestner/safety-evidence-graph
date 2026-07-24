"""``python -m doc`` — registry-driven build orchestrator for the doc federation.

Replaces cygnus's CMake layer (which provided phony target factories, not
incrementality). The dependency structure is fixed and two layers deep, so it
is encoded literally:

  stage 1  build EVERY document once, publishing objects.inv + needs.json
           into the shared deploy tree;
  stage 2  build the SELECTED documents again — now every cross-document
           reference (intersphinx, needs_external_needs) resolves against the
           stage-1 indices. Doctrees are reused between stages.

Sphinx's own doctree cache provides incrementality; this driver provides
selection, the barrier, parallelism, and cleanup.

Commands:
  python -m doc build [DOC ...] [-b html] [--no-index] [-j N]
  python -m doc live DOC
  python -m doc clean [DOC ...]
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

DOC_ROOT = Path(__file__).resolve().parent
REPO_ROOT = DOC_ROOT.parent
BUILD_ROOT = REPO_ROOT / "build" / "doc"
DEPLOY = BUILD_ROOT / "deploy"


def registry() -> dict:
    with open(DOC_ROOT / "documents.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def doc_ids(reg: dict) -> list[str]:
    return [d["id"] for d in reg["documents"]]


def sphinx(doc: str, builder: str, *, out: Path, extra_env: dict | None = None) -> int:
    src = DOC_ROOT / doc
    doctrees = BUILD_ROOT / doc / "doctrees"
    logdir = BUILD_ROOT / doc
    logdir.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    env = os.environ | {"AFFIRMATRIX_DOC_DEPLOY": str(DEPLOY)} | (extra_env or {})
    cmd = [
        sys.executable, "-m", "sphinx",
        "-b", builder,
        "-c", str(src),
        "-d", str(doctrees),
        "-w", str(logdir / f"{builder}.log"),
        str(src), str(out),
    ]
    proc = subprocess.run(cmd, env=env)
    return proc.returncode


def build_stage(docs: list[str], builder: str, jobs: int, label: str) -> None:
    failures = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {
            pool.submit(sphinx, d, builder, out=DEPLOY / d / builder): d for d in docs
        }
        for future, doc in futures.items():
            if future.result() != 0:
                failures.append(doc)
    if failures:
        sys.exit(f"{label} failed for: {', '.join(failures)}")


def cmd_build(args: argparse.Namespace) -> None:
    reg = registry()
    everything = doc_ids(reg)
    selected = args.docs or everything
    unknown = set(selected) - set(everything)
    if unknown:
        sys.exit(f"unknown document(s): {', '.join(sorted(unknown))} (see doc/documents.yaml)")
    if not args.no_index:
        print(f"== stage 1: indices for {len(everything)} documents")
        build_stage(everything, "html", args.jobs, "stage 1")
    print(f"== stage 2: {args.builder} for {', '.join(selected)}")
    build_stage(selected, args.builder, args.jobs, "stage 2")
    print(f"done — output under {DEPLOY}")


def cmd_live(args: argparse.Namespace) -> None:
    doc = args.doc
    src = DOC_ROOT / doc
    out = DEPLOY / doc / "html"
    env = os.environ | {"AFFIRMATRIX_DOC_DEPLOY": str(DEPLOY)}
    cmd = [
        sys.executable, "-m", "sphinx_autobuild",
        "-b", "html",
        "-c", str(src),
        "--watch", str(src),
        str(src), str(out),
    ]
    raise SystemExit(subprocess.run(cmd, env=env).returncode)


def cmd_clean(args: argparse.Namespace) -> None:
    targets = args.docs or doc_ids(registry())
    for doc in targets:
        for path in (BUILD_ROOT / doc, DEPLOY / doc):
            shutil.rmtree(path, ignore_errors=True)
    if not args.docs and BUILD_ROOT.exists() and not any(BUILD_ROOT.iterdir()):
        shutil.rmtree(BUILD_ROOT.parent, ignore_errors=True)
    print("cleaned")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m doc")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build", help="two-stage build of the document federation")
    p_build.add_argument("docs", nargs="*", help="documents to build (default: all)")
    p_build.add_argument("-b", "--builder", default="html")
    p_build.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 2)
    p_build.add_argument(
        "--no-index", action="store_true",
        help="skip stage 1 (fast rebuild against existing indices)",
    )
    p_build.set_defaults(func=cmd_build)

    p_live = sub.add_parser("live", help="sphinx-autobuild live preview for one document")
    p_live.add_argument("doc")
    p_live.set_defaults(func=cmd_live)

    p_clean = sub.add_parser("clean", help="remove build intermediates and deploy output")
    p_clean.add_argument("docs", nargs="*")
    p_clean.set_defaults(func=cmd_clean)

    args = parser.parse_args(argv)
    args.func(args)
