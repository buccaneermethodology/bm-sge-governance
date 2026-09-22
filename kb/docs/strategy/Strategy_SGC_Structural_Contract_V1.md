# Strategy SGC Structural Contract V1

_Owner: sge-core | Version: v1.1 | Status: active | Updated: 2026-07-01_

## Authority And Purpose

SGC v1 is the active structural semantic-governance contract for AI coding implementation decisions that carry semantic-risk impact.

For non-trivial SGE tasks, SGC v1 is a default proportional structural-governance check before implementation, validation, completion, promotion, or truth-placement claims are relied on.

Its purpose is to prevent semantic collapse into structural substitution, false validation through deterministic recomputation, ungrounded implementation decisions, scope substitution, executionless completion claims, and completion hallucination.

This document promotes only the stable structural subset from the draft SGC material. It does not promote broad v2/v3 output formats, numeric scoring surfaces, universal ledger requirements, runtime behavior, schema behavior, acceptance posture, provider usage, CLI behavior, or product capability claims.

- Authority layer: canonical KB strategy truth for SGE agent coding governance.
- Execution layer: Dashboard sessions and closeouts record task state and evidence; they do not override this contract.
- Implementation layer: tests, runtime output, reports, and source inspection can provide evidence for a claim, but do not become semantic law unless separately promoted.

## Applicability

| Surface | SGC v1 Applies When | SGC v1 Does Not Apply As |
| --- | --- | --- |
| Non-trivial SGE task | The task changes durable repo state, KB truth, Dashboard state, contracts, acceptance/gates, runtime/schema behavior, semantic-risk implementation decisions, or completion/promotion claims. | A mandatory ceremony for trivial read-only commands, low-risk chat, or purely mechanical formatting with no semantic-risk claim. |
| AI coding implementation decision | The decision changes or claims contract meaning, semantic boundary, implementation scope, completion status, validation status, promotion status, runtime widening, or KB/Dashboard truth placement. | A blanket template for every ordinary response, trivial read-only command, or low-risk chat answer. |
| Completion or validation claim | The agent says work is `done`, `validated`, `correct`, `promoted`, or otherwise ready for downstream reliance. | A substitute for running the appropriate deterministic gates or preserving closeout evidence. |
| Contract or governance edit | The edit defines durable terminology, forbidden patterns, claim levels, or future-agent policy. | Automatic approval to change runtime behavior, acceptance posture, provider use, schemas, or product capability claims. |
| Future v2/v3 ideas | They may be cited as future design pressure or deferred layers. | Active requirements in v1; they impose no current output-format, score, graph, or ledger obligation. |
| Goal, Stage Plan, or tracked Session execution | The agent claims that an original user Goal, Stage Plan, or tracked Session is complete, revised, narrowed, deferred, blocked, or replaced. | Permission to silently substitute a smaller or easier revised target for the original objective, or to validate only the revised target while claiming the original target is done. |

## Claim Levels

| Claim Level | Meaning | Allowed Claim Strength |
| --- | --- | --- |
| execution_bound | The claim is supported by observed runtime, command, system, or simulation execution and the relevant environment/context is known. | May support execution-reality claims when evidence and scope match the statement. |
| test_bound | The claim is supported by deterministic tests, gates, regressions, or validators that directly cover the asserted behavior. | May support validation claims for the tested contract boundary, not broader correctness. |
| structurally_supported | The claim is supported by AST, CFG, graph, schema, static inspection, or other structural evidence. | May support structural or design claims; must not be called semantic truth by itself. |
| externally_supported | The claim is supported by cited external verification, authoritative documentation, or human-provided evidence. | May support source-bound claims; must name authority and freshness limits when relevant. |
| inference_only | The claim is reasoned from patterns, probabilities, model judgment, or indirect evidence. | May support candidate guidance or risk hypotheses; must not be promoted as validated truth. |
| ungrounded | No adequate supporting evidence is available or the evidence layer does not match the claim. | Must not support done, validated, correct, promoted, or broad capability claims. |

## Forbidden Collapses

| Pattern | Forbidden Move | Required Handling |
| --- | --- | --- |
| Schema substitution | Treating field additions, schema conformance, or structured shape as semantic modeling by itself. | State the semantic gap; add oracle, contract, validation, or review evidence before semantic claims. |
| Recompute validation | Calling regenerated expected output a validation result. | Use independent deterministic gates, oracle comparison, runtime observation, or preserved evidence. |
| Profile or routing collapse | Reducing semantic grounding to routing rules, profiles, labels, or pattern selection. | Keep routing/profile evidence below semantic authority unless separately validated. |
| Deterministic masking | Converting uncertainty into labels, enums, lattices, or scores without preserving unresolved risk. | Expose uncertainty, contradiction risk, unsupported cases, and follow-up route. |
| Mock grounding | Treating lineage JSON, evidence IDs, or provenance-shaped fields as grounded evidence when they lack execution, source, or structural basis. | Identify the missing grounding layer and block truth or promotion claims until repaired. |
| False closure | Declaring work complete, validated, correct, promoted, or ready when evidence only supports a weaker claim. | Narrow the claim, run the missing gate, ask for review, or record deferred remainder. |
| Scope substitution | Replacing the original user Goal, Stage Plan, or tracked Session objective with a smaller, easier, or differently named target, then using evidence for the revised target to claim the original target is complete. | Preserve an original-scope ledger, record every Scope Delta explicitly, require human approval or blocker status for material narrowing, and keep unlanded original items as deferred sessions or blockers before any completion claim. |

## Goal Conformance And Scope Delta Gate

For any non-trivial Goal, Stage Plan, or tracked Session execution, the agent must preserve the original objective as an auditable coverage surface. A revised design may narrow or stage the work, but it does not replace the original objective unless the human explicitly approves the scope change or the closeout records a blocker/termination condition.

The gate runs at three points by default: after C0 or initial design, before dominant Builder implementation, and before closeout. Each run compares the current execution target against the original Goal or Stage Plan rather than only against the newest revised design.

- Create or reference a Goal Scope Ledger for non-trivial Goals: requirement, current status, evidence, landed/not-landed disposition, unresolved blocker or defer reason, and owning Session or Stage Plan row.
- Mark any deleted, renamed, replaced, downgraded, postponed, or newly excluded original must-have as a Scope Delta.
- A Scope Delta must state the original requirement, why it cannot or should not land now, what replaces it, what capability or evidence is lost, whether human approval is required, and where the deferred item or blocker is tracked.
- Validation must check both whether the implementation satisfies the revised design and whether the revised design still satisfies the original Goal. The second check cannot be omitted by handing Validation only the diff or final implementation notes.
- Closeout must include an Original Plan Coverage Matrix for non-trivial Goals and Stage Plans. Each original item is classified as landed, not landed human-approved deferred, not landed blocked, or not applicable with reason.
- If any original must-have remains not landed without explicit human-approved deferral, not applicable rationale, or blocker/termination status, the Stage Plan or Goal must not be marked complete. Valid statuses include partial-done, done-for-approved-subset, blocked-on-scope-decision, or needs-human-scope-approval.
- This gate does not activate SGC v2/v3, numeric scoring, universal ledger formats, runtime behavior, schema behavior, or acceptance-posture changes. It is a completion-claim and scope-integrity control.

## Structural Invariants

| Invariant | Review Question | Blocking Failure |
| --- | --- | --- |
| SI-1 Truth is not structure | Does the evidence prove meaning, or only shape, field presence, route, or label? | A semantic truth claim relies only on structure. |
| SI-2 Grounding completeness | Does the claim name the evidence layer that actually supports it? | The claim has no matching execution, test, structural, external, or reviewed source support. |
| SI-3 Decision surface validity | Is the decision recorded in the right layer: KB truth, Dashboard memory, tests/reports, runtime behavior, or reader-facing explanation? | A lower-authority artifact is treated as canonical law or a KB contract is left only in chat/Dashboard. |
| SI-4 Non-tautological validation | Is validation independent from the generator or implementation being judged? | The same mechanism creates the output and declares it valid without independent gate/evidence. |
| SI-5 Authority-execution coupling | Does the claimed completion or promotion level match executed gates and preserved evidence? | A `done`, `validated`, `correct`, or `promoted` claim exceeds the evidence level. |
| SI-6 Original objective coverage | Does the completion claim account for the original user Goal, Stage Plan, or tracked Session requirements, not only the revised implementation slice? | A narrower target is treated as the original target without explicit Scope Delta, human-approved deferral, not-applicable rationale, or blocker status. |

## Completion Rule

An agent must not declare `done`, `validated`, `correct`, or `promoted` unless the claim level and preserved evidence match the asserted strength.

If the strongest support is `structurally_supported`, the agent may claim structural consistency or design alignment, but must not claim semantic correctness. If the strongest support is `inference_only`, the agent may propose, recommend, or flag risk, but must not claim validation. If evidence is `ungrounded`, the agent must mark the decision invalid for truth or promotion purposes.

For Goals, Stage Plans, and tracked Sessions, completion also requires original-objective coverage. Evidence for a narrowed slice can close that slice, but it cannot close the original objective unless every original must-have is landed, explicitly human-approved for deferral, not applicable with reason, or blocked by a stated termination condition.

For non-trivial SGE work, completion claims must still follow the existing closeout, Validation Handoff Packet, Contract Delta Scan, KB/Dashboard review, and Semantic Reviewer trigger rules.

- Run the SGC v1 check before final closeout of non-trivial SGE work and before relying on implementation, validation, promotion, or truth-placement claims.
- Use narrow language when evidence is narrow.
- Name explicit non-goals when adjacent capability claims are tempting.
- Preserve deferred remainder in Dashboard when losing it would create rediscovery cost.
- Before closeout, compare the original Goal Scope Ledger against the landed scope and block `done` wording when unapproved must-have items remain not landed.
- Record no-escalation rationale when semantic-risk triggers are visible but Semantic Reviewer is not started.

## Future Layers

| Layer | Future Intent | Current v1 Authority |
| --- | --- | --- |
| SGC v2 Semantic Integrity Layer | May later define adversarial semantic checks, contradiction analysis, and traceable semantic decision surfaces. | Future only. It imposes no active numeric score, mandatory adversarial block, or universal decision-surface format in v1. |
| SGC v3 Execution Binding Layer | May later define execution-binding graphs, counterfactual robustness, or a semantic execution ledger for high-risk claims. | Future only. It imposes no active graph, ledger, counterfactual-test, or every-decision recording requirement in v1. |

## Non-Promises

- This contract does not make Semantic Reviewer mandatory for every task.
- This contract does not replace Validation Agent, deterministic gates, BDD, contract tests, or maintained validation runners.
- This contract does not create a numeric semantic scorecard or universal validity score.
- This contract does not change runtime behavior, schema shape, acceptance posture, provider strategy, CLI behavior, KG source set, or product capability claims.
- This contract does not allow root-level drafts, Dashboard artifacts, runtime reports, or generated projections to override KB JSON truth.

## Source Scope

- `AGENTS.md`
- `Dashboard/Methodology.md`
- `Dashboard/Rules.md`
- `Dashboard/Sessions.md`
- `kb/data/strategy/strategy_human_ai_development.json`
- `kb/data/strategy/strategy_semantic_surface_engineering.json`
- `kb/data/strategy/strategy_kb_promotion_and_source_policy.json`
- `Dashboard/Artifacts/Stage-Plan-SP-001/SP001_SGEGovernanceMigration_LoopGoal.md`

## Related Docs

- `sge-strategy-human-ai-development`
- `sge-strategy-semantic-surface-engineering`
- `sge-strategy-kb-promotion-and-source-policy`
