# RFC 0001: Semantic feed contract

Status: Draft

## 1. Problem statement

Semantic feeds need portable data contracts so ranking implementations can explain why an item appeared without inventing evidence or metrics.

## 2. Goals

Define the v0.1 executable contract for candidates, analysis, lenses, rank requests, feed slates, evidence-backed contributions, deterministic selection, and typed metrics.

## 3. Non-goals

RFC 0001 does not specify App Semantic Contract, MCP, AG-UI, A2UI, Bilibili, PiliPlus, Flutter UI, model calls, network crawling, cloud sync, accounts, or telemetry.

## 4. Core terms

The normative terms are FeedCandidate, Subject, Trigger, Source, Provenance, Evidence, AnalysisRecord, Signal, LensProfile, Policy, Context, ClusterAssignment, RankingReason, RankingDecision, FeedSlate, Adapter, Analyzer, and Host as defined in `docs/terminology.md`.

## 5. Normative data flow

```text
validate
→ eligibility/filtering
→ feature contributions
→ deterministic ordering
→ cluster-constrained selection
→ typed slate metrics
```

## 6. Input objects

A `RankRequest` contains `specVersion: "v0.1"`, `context.generatedAt`, candidates, one analysis record per candidate, and one LensProfile. Top-level objects use `specVersion: "v0.1"`.

## 7. Output objects

A `FeedSlate` contains `specVersion`, `generatedAt` copied from request context, selected items with a single rank location in `decision.rank`, and typed `coverage` and `diversity`.

## 8. Signal and Evidence rules

Every score-affecting Signal contains `value` and non-empty `evidenceRefs`. Implementations must not guess Evidence IDs from candidate IDs. Source signals use `source.*`; analysis signals use `analysis.*`. Evidence refs must resolve within the candidate or its analysis record.

## 9. Lens weights and feature contributions

For each candidate, implementations match Lens weights to signal names. Contribution is `signal.value * weight`. Every non-zero contribution becomes a RankingReason with signal name, value, weight, contribution, and evidence refs copied directly from that signal. Positive and negative contributions are both recorded.

## 10. Filtering and deterministic sorting

Eligibility is limited to candidates whose source type is allowed by the Lens. Candidate score is the sum of non-zero contributions. v0.1 supports only `candidateIdAsc` tie breaking: sort by descending score and then ascending candidate id.

## 11. Cluster and per-cluster limit

Cluster membership is only established by explicit ClusterAssignment. Unassigned candidates are independent and do not suppress each other. `maxPerCluster` applies to every integer value greater than or equal to 1. Candidates skipped only because a cluster is full are counted in diversity metrics.

## 12. Coverage and Diversity metrics

Coverage reports actual selected item counts by source type. Diversity reports selected cluster counts by `namespace:id`, selected unclustered count, and the count of candidates suppressed by cluster limits.

## 13. Version compatibility

v0.1 fixtures and schemas require exact `specVersion: "v0.1"`. Additive data must use explicit `extensions`; normal unknown fields are rejected.

## 14. Privacy and local-first boundary

The contract is executable without network access, model calls, databases, or telemetry. Hosts may run adapters or analyzers separately, but ranking consumes already supplied JSON.

## 15. Verifiable assumptions

The fixtures verify schema validity, reference integrity, deterministic tie breaking, positive and negative reasons, fixed time propagation, coverage, diversity, and three distinct Lens outputs over one candidate pool.

## 16. Unverified assumptions

Synthetic fixtures do not prove user value, real-world source quality, analyzer accuracy, or the best ranking formula.

## 17. Future work

Future RFCs may define exploration, live adapters, analyzer protocols, UI bindings, or broader semantic app contracts after they have deterministic, testable semantics.
