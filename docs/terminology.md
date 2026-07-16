# Refetch terminology

- **FeedCandidate**: a rankable unit from a source, with subject, trigger, provenance, evidence, and source signals.
- **Subject**: the object being understood, such as a repository release, article, issue, or discussion.
- **Trigger**: why the subject became a candidate now, such as a release, publication, update, or observed activity.
- **Source**: the origin system and type, currently constrained in fixtures to `github` and `rss` examples.
- **Provenance**: traceable source metadata such as URL, author, and retrieval time.
- **Evidence**: a traceable data basis for a signal or cluster assignment. Evidence is not natural-language decoration.
- **AnalysisRecord**: analyzer-produced facts for exactly one candidate, including analysis signals and optional cluster assignments.
- **Signal**: a named numeric feature with a finite value and explicit evidence references. Source signal names use `source.*`; analysis signal names use `analysis.*`.
- **LensProfile**: the user-selected task perspective for this ranking run, including weights, filters, and policy. A Lens is not a secret permanent personality inferred by the system.
- **Policy**: deterministic limits and ordering rules such as `maxItems`, `maxPerCluster`, and `candidateIdAsc`.
- **Context**: request-level data. In v0.1 it includes `generatedAt`, which is copied to the output slate.
- **ClusterAssignment**: an explicit analyzer statement that a candidate belongs to a cluster namespace and id, with evidence refs.
- **RankingReason**: the structured record of a non-zero feature contribution. It must come from a Signal that actually participated in scoring.
- **RankingDecision**: the selected candidate's score, rank, and reasons.
- **FeedSlate**: the deterministic output containing selected items, generated time, coverage, and diversity metrics.
- **Adapter**: an implementation component that converts source data into candidates. Adapters are out of scope for RFC 0001 execution.
- **Analyzer**: an implementation component that emits AnalysisRecords. Model calls and live analyzers are out of scope for RFC 0001 execution.
- **Host**: the application embedding Refetch and selecting the current Lens.
