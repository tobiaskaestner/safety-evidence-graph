"""The proof generator — the evidence package.

Collects the scope, assembles the four documents (DesignConsistencyProof,
ExecutionCoverageRecord, CoverageReport, EvidenceManifest), and supplies the
snapshot metadata to the commitment layer's design-root primitive — it holds no
hashing logic of its own (ADR-0003).

Invariants it must preserve (AC-016), because compositional proof will need
them even though composition is not v1: the root is recomputable from the
package's own ``nodeManifest``, and every proof publishes its scope explicitly,
including the partial-vs-total top-level signal (DEC-002).

Scope expansion must be total — ``refines`` upward, then ``implements`` and
``verifies``, then ``confirms``, then ``excuses``; a missing hop yields a
silently partial scope.

**Refusal precedes writing (SEG-SYS-008).** Because writes land in place
(ADR-0008), the gate runs to completion first and no proof file is opened for a
blocked scope.

**Capability, not authority (AC-006):** the FSM operates generation.

Iteration 0, backlog items B16 (scope), B17 (artifacts), B18 (refusal).
"""
