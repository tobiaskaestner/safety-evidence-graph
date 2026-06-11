import json
import glob
import pytest
from pathlib import Path
from rdflib import Dataset, URIRef, Literal, Namespace

ROOT = Path(__file__).parent.parent
SEG = Namespace("https://zephyrproject.org/seg#")
NS = "https://zephyrproject.org/safety/"


def load_graph():
    with open(ROOT / "context.jsonld") as f:
        ctx = json.load(f)["@context"]

    g = Dataset()
    for path in sorted(ROOT.glob("**/*.jsonld")):
        if "context.jsonld" in str(path):
            continue
        with open(path) as f:
            data = json.load(f)
        # inject shared context so id/type/seg: are interpreted as RDF
        if isinstance(data, list):
            wrapped = {"@context": ctx, "@graph": data}
        else:
            wrapped = {"@context": ctx, **data}
        g.parse(data=json.dumps(wrapped), format="json-ld")
    return g


@pytest.fixture(scope="module")
def graph():
    return load_graph()


def test_graph_loads(graph):
    assert len(graph) > 0, "Graph is empty"
    print(f"\nLoaded {len(graph)} triples")


def test_q1_evidence_chain_req001(graph):
    """Q1 — evidence chain for REQ-001: implements, verifies, and a PASS confirms."""
    query = """
    PREFIX seg: <https://zephyrproject.org/seg#>

    SELECT ?edgeType ?source WHERE {
        ?edge   a           ?edgeType ;
                seg:to      <https://zephyrproject.org/safety/req/REQ-001> ;
                seg:from    ?source .
        FILTER(?edgeType IN (seg:Implements, seg:Verifies))
    }
    ORDER BY ?edgeType ?source
    """
    rows = [(str(r.edgeType), str(r.source)) for r in graph.query(query)]
    assert (str(SEG.Implements), NS + "impl/z_sched_preempt") in rows
    assert (str(SEG.Verifies),   NS + "ts/TS-017")            in rows

    # follow the confirms leg: TS-017 ← confirms — RUN-44/TS-017
    confirms_query = """
    PREFIX seg: <https://zephyrproject.org/seg#>

    SELECT ?outcome ?result WHERE {
        ?edge   a           seg:Confirms ;
                seg:to      <https://zephyrproject.org/safety/ts/TS-017> ;
                seg:from    ?outcome .
        ?outcome seg:outcome ?result .
    }
    """
    rows = [(str(r.outcome), str(r.result)) for r in graph.query(confirms_query)]
    assert (NS + "outcome/RUN-44/TS-017", "PASS") in rows


def test_q2_evidence_chain_req002(graph):
    """Q2 — evidence chain for REQ-002: implements, verifies, FAIL outcome, and waiver."""
    inbound_query = """
    PREFIX seg: <https://zephyrproject.org/seg#>

    SELECT ?edgeType ?source WHERE {
        ?edge   a           ?edgeType ;
                seg:to      <https://zephyrproject.org/safety/req/REQ-002> ;
                seg:from    ?source .
        FILTER(?edgeType IN (seg:Implements, seg:Verifies))
    }
    ORDER BY ?edgeType ?source
    """
    rows = [(str(r.edgeType), str(r.source)) for r in graph.query(inbound_query)]
    assert (str(SEG.Implements), NS + "impl/z_sched_lock") in rows
    assert (str(SEG.Verifies),   NS + "ts/TS-019")         in rows

    # TS-019 ← confirms — RUN-44/TS-019 (FAIL), excused by WAV-001
    tail_query = """
    PREFIX seg: <https://zephyrproject.org/seg#>

    SELECT ?outcome ?result ?waiver WHERE {
        ?confirmEdge    a           seg:Confirms ;
                        seg:to      <https://zephyrproject.org/safety/ts/TS-019> ;
                        seg:from    ?outcome .
        ?outcome        seg:outcome ?result .
        OPTIONAL {
            ?excusesEdge    a           seg:Excuses ;
                            seg:to      ?outcome ;
                            seg:from    ?waiver .
        }
    }
    """
    rows = [(str(r.outcome), str(r.result), str(r.waiver)) for r in graph.query(tail_query)]
    assert (NS + "outcome/RUN-44/TS-019", "FAIL", NS + "waiver/WAV-001") in rows


def test_q3_no_suspect_links(graph):
    """Q3 — all strong edges should be active (review event resolved the suspect link)."""
    query = """
    PREFIX seg: <https://zephyrproject.org/seg#>

    SELECT ?edge ?linkState WHERE {
        ?edge seg:linkState ?linkState .
        FILTER(?linkState != "active")
    }
    """
    rows = [(str(r.edge), str(r.linkState)) for r in graph.query(query)]
    assert rows == [], f"Unexpected suspect links: {rows}"


def test_q4_scope_completeness(graph):
    """Q4 — every in-scope requirement has at least one verifies and one implements edge."""
    query = """
    PREFIX seg: <https://zephyrproject.org/seg#>

    SELECT ?req
           (COUNT(DISTINCT ?vEdge) AS ?verifyCount)
           (COUNT(DISTINCT ?iEdge) AS ?implCount)
    WHERE {
        VALUES ?req {
            <https://zephyrproject.org/safety/req/REQ-001>
            <https://zephyrproject.org/safety/req/REQ-002>
        }
        OPTIONAL { ?vEdge a seg:Verifies  ; seg:to ?req . }
        OPTIONAL { ?iEdge a seg:Implements ; seg:to ?req . }
    }
    GROUP BY ?req
    """
    for row in graph.query(query):
        req = str(row.req)
        assert int(row.verifyCount) >= 1, f"{req} has no verifies edge"
        assert int(row.implCount)   >= 1, f"{req} has no implements edge"


def test_q5_waiver_validity(graph):
    """Q5 — all waivers referenced by excuses edges are non-expired as of 2024-03-15."""
    TEST_DATE = "2024-03-15"
    query = """
    PREFIX seg: <https://zephyrproject.org/seg#>

    SELECT ?waiver ?outcome ?expiry WHERE {
        ?edge       a           seg:Excuses ;
                    seg:from    ?waiver ;
                    seg:to      ?outcome .
        ?waiver     seg:expiry  ?expiry .
    }
    """
    rows = list(graph.query(query))
    assert rows, "No excuses edges with waivers found"
    for row in rows:
        expiry = str(row.expiry)
        assert expiry > TEST_DATE, (
            f"Waiver {row.waiver} expired on {expiry}, before test date {TEST_DATE}"
        )
