# Related work and research-gap assessment

Reviewed on 27 October 2026. This is a targeted primary-source review, not an exhaustive systematic review or independent reproduction of the cited studies. Recent preprint results below are their authors' reports. They do not independently validate NyAI.

## What established work already addresses

**AI control and research sabotage.** [Greenblatt et al., AI Control](https://arxiv.org/abs/2312.06942) evaluate monitoring and editing protocols against intentional subversion in programming tasks, including errors missed by tests. [Ward et al., CTRL-ALT-DECEIT](https://arxiv.org/abs/2511.09904) evaluate sabotage and sandbagging in realistic ML engineering, including monitor limitations. These establish a stronger adversarial setting than NyAI's constructed records. NyAI currently cannot claim control of a strategically deceptive researcher.

**Verifying what an agent actually did.** [Sediqin et al., A Trust Layer for Agent Evaluation](https://arxiv.org/abs/2610.07274), an October 2026 preprint, separates grading support, traceable computation, honest completion and repeatability. This directly overlaps NyAI's distinction between a reported success and execution evidence. NyAI should cite this overlap rather than present execution verification as a new idea.

**Observation integrity.** [Qin et al., LLM Agents Can Easily Tamper With Their Own Traces](https://arxiv.org/abs/2609.30266) report failures of trace integrity in local agent harnesses and motivate capture outside agent control. A JSON log and matching hash do not establish a protected recording boundary. NyAI's local observer remains trusted; its experiments do not cover a compromised operating system or observer.

**Artifact provenance and attestation.** [in-toto](https://in-toto.io/) provides metadata about performed supply-chain steps, actors and order. [SLSA verification guidance](https://slsa.dev/spec/v1.2/verifying-artifacts) specifies trusted builder identities, signatures, artifact digest matching and expected build parameters. NyAI's execution binding is an application of familiar safeguards, without a claim of SLSA conformance, remote attestation or scientific correctness.

**Revision and invalidation are established concepts.** [W3C PROV-DM](https://www.w3.org/TR/prov-dm/) already represents derivation, revision and invalidation; [PROV constraints](https://www.w3.org/TR/prov-constraints/) distinguish consistent provenance histories from arbitrary records. A structurally valid history does not establish the truth or adequacy of the scientific experiment it describes.

**Stale state and downstream decisions.** [Chao et al., STALE](https://arxiv.org/abs/2605.06527) evaluate implicit invalidation, stale-premise resistance and downstream adaptation. [Nakayashiki, When Stale Constraints Go Unchecked](https://arxiv.org/abs/2608.25553) studies failures to revisit important provenance under a verification budget. Its forced-critical comparison is explicitly an oracle, not an implementable scheduler. NyAI must not use hidden case labels to select decisive evidence during evaluation.

**The missing-edge problem.** [Salas, Change-Provenant Supervision](https://arxiv.org/abs/2609.28574) separates graph-scoped impact triage from independent current-contract revalidation. Its controlled edge-omission tests directly challenge graph-only admission: a recorded graph cannot certify that a load-bearing dependency was not omitted. This is close prior art. NyAI must compare against complete revalidation and treat graph incompleteness as a material limitation, not claim new safety from lineage alone.

**Citations and agent handoffs.** [Gao et al., ALCE](https://arxiv.org/abs/2305.14627) distinguish answer correctness and citation quality. [Hirsch et al., Localizing Faithfulness and Citation Mistakes in Agentic Deep Research](https://arxiv.org/abs/2608.24306) localize failures relative to individual agent inputs. NyAI's resolvable citation IDs establish neither entailment nor adequate support for a conclusion.

**Auditability versus efficacy.** [Nian et al., Auditable Agents](https://arxiv.org/abs/2604.05485) distinguish auditing, auditability and accountability, covering evidence integrity and lifecycle information. Producing inspectable records is therefore an engineering property whose benefit to an actual overseer still requires measurement.

## Chosen direction and claim boundary

The feasible immediate direction is **B: detecting stale or invalidated research conclusions**, using exact, inspectable evaluation artifacts. **C: better overseer decisions from explicit revision records** is the next empirical question. A is necessary infrastructure, but execution and version verification alone are established practice. Combining them does not establish novelty.

The smallest useful question is whether a bounded research-auditing benchmark reveals differences between execution-valid evidence and evidence that still warrants a particular conclusion after changes in scope, artifacts or contrary results. A contribution may be a reproducible stress test and informative failure analysis, including a negative result against a strong baseline. It is not yet a novel general oversight algorithm.

Compare ordinary artifact checks, strong complete current-contract verification, and identical safeguards with explicit warrants/revision records. Add a separate NyAI condition only if its decision mechanism actually differs. Hold observable inputs and budgets comparable; describe extra derived fields as an intervention, not equal presentation. Treat oracle evidence selection, complete source coverage and perfect graph structure as privileged assumptions when used.

Meaningful stress cases include missing execution, a changed dataset split or harness, a passing result cited outside its scope, superseded evidence, a missing dependency edge, contrary reruns and benign irrelevant changes. Charge methods for unnecessary withholding as well as unsupported acceptance. A tie with complete conventional checks is evidence against an incremental decision benefit, not a presentation failure to conceal.

## Limits of the safety interpretation

Reliable evidence binding could help prevent unsupported research results from influencing later safety decisions. This pathway assumes that the recorded evaluations measure relevant properties, the observer remains trusted, adverse evidence is available, and downstream actors respect the gate. It can fail through inadequate tests, missing dependencies, selective experiment reporting, compromised infrastructure or deception outside observable actions. No finite pilot establishes catastrophic-risk reduction, general alignment or mechanistic interpretability.

For future work, freeze task-family holdouts, annotation rules and minimum effects before running confirmatory comparisons. Independent human review and a counterbalanced reviewer study would test whether explicit records improve decisions or effort beyond ordinary logs. Until then, reviewer benefit and generalisation remain hypotheses.
