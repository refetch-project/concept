# Refetch Concept

Refetch Concept is the language-neutral source of truth for Refetch: an open, portable foundation for user-directed semantic feeds. It defines the terminology, RFCs, JSON Schema, and conformance fixtures that implementations use to produce explainable `FeedSlate` results.

The Rust reference implementation lives in [`refetch-project/core-rust`](https://github.com/refetch-project/core-rust). Rust structs are bindings to this repository's schemas and fixtures; they are not the specification source.

> **Project stage:** Foundation v0.1.1. The v0.1 contract is a draft, executable specification for deterministic feed ranking and slate selection.

## What Refetch enables

Refetch lets the same pool of information be reorganized through an explicit **Lens** chosen for the user's current task.

| Lens | What rises to the top |
| --- | --- |
| Production readiness | stable releases, migration notes, operational risk, compatibility |
| Frontier watch | new techniques, unusual experiments, early research signals |
| Maintenance triage | regressions, security fixes, dependency churn, high-impact issues |

For example, a GitHub release and an RSS article can both be represented as `FeedCandidate` objects. Under a production-readiness Lens, the release may rank highly because its signals show stable adoption and migration evidence. Under a frontier Lens, the RSS article may rank higher because analysis signals show novelty and active technical discussion. The source material stays the same; the selected Lens changes the ranking policy and explanations.

## Repository boundary

This repository contains:

- Shared terminology in [`docs/terminology.md`](docs/terminology.md).
- Draft semantic feed rules in [`rfcs/0001-semantic-feed.md`](rfcs/0001-semantic-feed.md).
- Versioned JSON Schema in [`schemas/v0.1/`](schemas/v0.1/).
- Conformance fixtures in [`fixtures/v0.1/`](fixtures/v0.1/).
- Mechanical validation in [`scripts/validate-fixtures.py`](scripts/validate-fixtures.py).
- Maintainer notes in [`docs/maintainers/`](docs/maintainers/).

[`core-rust`](https://github.com/refetch-project/core-rust) contains the deterministic Rust reference implementation, CLI, and Rust contract bindings. Other implementations should bind to the schemas and pass the fixtures here rather than copying Rust-specific assumptions.

## Contract shape

```text
FeedSlate = Select(Rank(Candidates, LensProfile, Policy, Context))
```

The v0.1 flow is intentionally small and testable:

```text
validate
→ eligibility/filtering
→ feature contributions
→ deterministic ordering
→ cluster-constrained selection
→ typed slate metrics
```

Every score-affecting `Signal` carries explicit `evidenceRefs`. Every non-zero contribution becomes a structured `RankingReason`. `FeedSlate.generatedAt` comes from `RankRequest.context.generatedAt`, so implementations do not read the clock while ranking.

## Validate the executable spec

Install the Python dependency and run the fixture checks:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate-fixtures.py
```

The validator checks schemas, local `$ref` resolution, valid and invalid fixtures, references, expected `FeedSlate` outputs, and observable differences across the three Lens examples.

## Contributing

Good contributions include:

- Real feed scenarios with candidate data, evidence, and the desired user-visible explanations.
- Reviews of the RFC, schemas, and fixture semantics.
- Additional conformance fixtures that expose ambiguous contract behavior.
- Implementation feedback from Rust, TypeScript, Dart, or other bindings.

Please keep product limitations and internal failure analysis in RFCs or maintainer docs rather than the README narrative.
