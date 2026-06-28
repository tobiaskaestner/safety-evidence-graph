# `research/` — grounding and throwaway prototypes

The second stage of the [maturity pipeline](../notes/seg_pipeline_model.md): go deeper
into the literature, build **small self-contained prototypes** (inputs mocked, meant to
be thrown away), and derive conclusions **on general grounds**. Output is understanding,
not shippable code.

| Path | What lives there |
|---|---|
| [`notes/`](notes/) | Design drafts, prior art, and the research decision-log slice — assume-guarantee composition ([`seg_composability_cbd.md`](notes/seg_composability_cbd.md)), the DSL ([`seg_definition_language.md`](notes/seg_definition_language.md)), ADR/projection core ([`seg_adr_projection_core.md`](notes/seg_adr_projection_core.md)), the idealization ledger ([`GAPS.md`](notes/GAPS.md)), prior art, open threads. |
| [`prototypes/spdx-v3.1-exchange/`](prototypes/spdx-v3.1-exchange/) | The three-party SPDX FuSa safety-BOM round-trip (its own README). |
| [`prototypes/demos/`](prototypes/demos/) | Self-contained clingo/SHACL verdict and composition proofs. |
| [`prototypes/examples/`](prototypes/examples/) | DSL example inputs (`*.dsl`). |
| [`paper/`](paper/) | Reserved for write-up (currently empty). |

Decisions of record are not duplicated here — see
[`../notes/decision_log_index.md`](../notes/decision_log_index.md).
