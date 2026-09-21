---
name: sge-governed-checkpoints
description: Use for non-trivial SGE tasks that risk skipping default multi-agent activation, validation handoff, semantic-risk escalation, human oracle review, adequacy review, Dashboard Agent proposal-mode, or deferred follow-on/dashboard closeout updates. Applies especially to tracked Session/Stage Plan execution, golden/oracle authoring, contract calibration, Dashboard refresh, scope narrowing, semantic promotion, and final closeout.
---

# SGE Governed Checkpoints

Use this repo-local skill when SGE work is substantial enough that a missed checkpoint would create drift or rediscovery cost.

Read [references/checklists.md](references/checklists.md) first when you need the concrete prompts or output shape. For Goal layering、Goal Patch、Validation State Snapshot、Delta Validation、rebaseline triggers、adversarial levels 和 convergence rules，读取 [references/context-efficient-goal-validation.md](references/context-efficient-goal-validation.md)。

`goal_patch.py` 默认验证 Codex 的 user-message provenance；非 Codex Agent 必须提供平台交付的 `approval_receipt_v1`，并通过 `--approval-source-root` 显式指定平台管理的 trusted root。项目内 Agent 自己写出的普通文件不能作为人类批准来源；缺少可验证 receipt 时保持 blocked。

## Core Intent

ERBE specification-first acceptance is the pre-Builder contract layer for Goals
with terminal predicates, state machines, authority routing, acceptance posture,
promotion/write boundaries, or high semantic risk. Use the Dashboard ERBE Contract/Cases artifact and the
Goal Agent tooling to classify applicability, freeze Contract/Cases, verify
trusted RED, lock Builder writes, and require same-identity GREEN plus
independent validation. Existing BDD readable cards remain projection-only.

This skill exists to prevent repeated execution mistakes:

1. starting a non-trivial phase batch without first materializing the current phase/stage workflow contract
1. treating tracked Session / Stage Plan execution as single-agent by default instead of starting governed Design / Builder / Validation / Closure lanes
1. freezing a new golden/oracle fixture before the human has reviewed the proposal
2. leaving concrete deferred follow-ons or next candidates in chat memory instead of recording them in `Dashboard/Sessions.md`
3. ending `A1` contract-adequacy calibration too early with thin prompt/run evidence and no explicit adequacy report
4. continuing prompt micro-tuning after the live problem has already shifted into executable acceptance hardening
5. treating Validation Agent as default without giving it a structured handoff packet
6. seeing semantic-risk triggers but forgetting to start Semantic Reviewer or record why it was not started
7. leaving Validation Handoff, gates, non-goals, semantic no-escalation, or deferred remainder only in the final chat instead of a Dashboard closeout artifact
8. treating a Dashboard Agent proposal as an approved Dashboard update, or giving next-step advice without a full Dashboard/KB panorama
9. letting Semantic Reviewer accept an artifact's own frame and only check local consistency instead of reviewing authority, layers, ontology, invariants, failure taxonomy, and transfer rules first
10. letting Semantic Reviewer keep hardening a flawed artifact frame with more fields/status/provenance instead of challenging truth carrier placement, God Object drift, semantic bureaucracy, half-schema DSL drift, and long-term complexity trajectory
11. seeing a semantic failure but failing to classify it with the canonical SGE S1-S6 taxonomy, locate the L0-L6 surface, choose the countermeasure, and decide whether the repair belongs in code, contract, gate, runtime, closeout, KB, Dashboard memory, or prose
12. approving a proposal, closeout, reviewed seed, matrix, baseline, or gate artifact that contains stable contract or promotion deltas, then closing the task without deciding whether the stable subset belongs in KB JSON, Dashboard memory, gate docs, runtime/tests, or a deferred session
13. treating a user instruction, attachment, proposal, or approval text as immediate implementation authority without first checking objective, source authority, repo boundaries, risks, and execution route
14. starting post-C0 implementation without a saved Design Agent artifact that turns the approved scope into module/API/data/contract/test slices for Builder and Validation
15. leaving compressed English/status/gate/KB/Dashboard conclusions unexplained in final chat or closeout artifacts, forcing the human reader to infer the meaning, judgment impact, boundary, and next action from shorthand
16. changing maintained non-unit behavior validation surfaces without checking whether BDD gate-level, case-level, or semantic Requirements-by-Example cards must be updated
17. executing or closing a non-trivial SGE task without applying SGC v1 Structural Contract to claim/evidence strength, forbidden collapses, structural invariants, and completion wording
18. substituting, narrowing, or validating a revised scope during Goal / Stage Plan execution without first preserving the original Goal must-haves, recording Scope Delta entries, getting required human approval, and checking Original Plan coverage before any `done` / `SP complete` claim
19. leaving closeout artifacts with pure-English H1/H2 headings, unexplained English verdict/status labels, or no `Closeout language verdict`, which makes the Chinese closeout rule non-executable
20. drafting Goal prompts as loose summaries instead of durable handoff contracts, or letting Orchestrator pressure skip mandatory reading, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, or closeout-language gate
21. letting Semantic Reviewer stay a no-overclaim gatekeeper instead of also reviewing implementation-entry semantics: minimum safe slice, implementation ladder, next-session map, future-agent terminology compression, and whether the design guides safe implementation rather than only forbidding bad claims
22. rebuilding the full project/Loop/Session/Validation context in every lane or repair round instead of reusing a versioned baseline and validating the delta
23. rewriting a multi-thousand-word Goal after every review comment instead of applying a traceable Goal Patch and emitting one final resolved Goal
24. letting Validation mix current-contract review, adversarial hardening, governance architecture, and implementation debugging until every possible improvement becomes a blocker
25. repeating full Read Manifests, closeout explanations, raw tool output, and stable background in progress updates or Agent Logs rather than preserving high-fidelity deltas and references
26. manually composing adjacent lane prompts that repeat Goal、governance、AC 和 source background instead of validating a machine-readable Lane Task Card and rendering a short digest-bound delegation prompt

## When To Trigger

Trigger this skill when any of the following is true:

- a non-trivial SGE task needs the default SGC v1 structural-governance check before implementation claims, validation claims, promotion claims, or closeout
- a non-trivial task needs final validation and therefore a `Validation Handoff Packet`
- the current agent is acting as a Validation Agent for a Goal, Stage Plan, tracked Session, closeout package, builder handoff, or delegated validation thread
- the user asks to execute or start a tracked Session or Stage Plan, such as `执行 S-xxx`, `启动 S-xxx`, `execute S-xxx`, or `执行 SP-xxx`
- the work is executing a Goal, Stage Plan, or original user plan where scope substitution, scope narrowing, revised-design-only validation, or an `SP complete` claim could hide unlanded must-haves
- the user asks to draft, review, refine, or finalize a Goal Prompt, Task Goal Prompt, Loop Goal Prompt, or subagent delegation prompt for governed SGE work
- a Loop Goal or multi-Session Stage Plan is active and a Session closeout could be mistaken for the end of the execution turn
- a Goal is being revised after review, or a Validation/repair loop reaches a second round and should switch from full baseline loading to Goal Patch / Validation State Snapshot / Delta Validation
- C0 has been approved and the approved scope is moving into implementation
- a task may trigger Semantic Reviewer because it involves capability widening, genericization, semantic promotion, acceptance posture/gate strictness change, oracle/golden freeze, phase calibration promotion, major canonical KB truth change, hidden widening, accidental generalization, or future drift risk
- the user asks for Dashboard Agent work, a Dashboard refresh, macro next-step guidance, stale Dashboard audit, or blue-sky direction finding
- a non-trivial phase batch is starting and you need the current phase/stage runbook
- a task adds, removes, renames, or materially changes a maintained non-unit deterministic gate, shared validator, runtime/contract/matrix gate, or an enumerable case inside such a gate
- a new golden/oracle fixture is about to be created or materially revised
- a phase is in `C0/A1/A2` calibration
- a tracked session is being closed through scope narrowing
- the task is starting and the request, attachment, proposal, approval text, or command may need source-authority, boundary, risk, or execution-route evaluation before action
- an approved proposal, closeout, reviewed seed, accepted baseline, matrix, contract, or acceptance/gate artifact may change stable contract meaning, artifact semantics, trust/disposition vocabulary, blocking/advisory logic, promotion boundary, non-goal boundary, or reusable terminology
- the task is non-trivial and is approaching final closeout
- a closeout artifact is being written, validated, or used for final completion wording and needs the executable `closeout-language` gate
- final chat, a closeout artifact, Dashboard summary, or validation/closure verdict uses compressed conclusions that affect human judgment, such as English status terms, boolean flags, gate verdicts, KB/Dashboard routing labels, semantic-risk labels, scope narrowing, deferred sessions, no-escalation notes, or next-candidate shorthand

## Workflow

1. If the task is workflow-governed, materialize the current generic workflow contract first:

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage full
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage design
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage validate
```

   - use `--stage full` for a complete governed batch
   - use `--stage intake`, `design`, `implement`, `validate`, or `closeout` for a narrower task
   - use `--format summary` for only the explanation layer, `--format template` for only the copyable command-template runbook, or keep the default `both`
   - the runner prints the current stage contract, relevant guardrail commands, acceptance posture entry surfaces, maintained regression commands, recommended skills, closeout obligations, and now also a stage-aware command-template runbook
2. Decide which checkpoint matters now.
   - `intake-evaluation`: a user instruction needs the default evaluate-before-execute gate
   - `sgc`: a non-trivial SGE task needs the SGC v1 structural-governance check for claim/evidence alignment and forbidden collapses
   - `multi-agent`: tracked or non-trivial governed work may otherwise collapse into one agent
   - `design`: post-C0 implementation needs a saved Design Agent artifact before dominant Builder work
   - `goal-conformance`: Goal / Stage Plan execution needs original must-have coverage, Scope Delta approval, and validation against the original Goal rather than only the revised design
   - `goal-agent`: Goal Prompt drafting / review needs a durable handoff contract with read manifest, scope ledger, validation focus, and anti-pressure completion rules
   - `loop-continuation`: an active Loop must automatically cross ready Session boundaries and stop only at Goal completion or an explicit termination condition
   - `validation-agent`: a Validation Agent needs the fixed read-mostly prompt, required evidence manifest, original-objective review, and anti-pressure verdict rules
   - `context-bootstrap`: every task needs a profile-specific startup packet that preserves Raw User Intent authority and the required epistemic search space
   - `context-efficiency`: Goal/Validation work needs layered context, Goal Patch, Validation State Snapshot, Delta Validation, rebaseline triggers, blocker admissibility, or convergence control
   - `lane-task-card`: a non-trivial lane is about to be delegated and needs fail-closed source/delta/topology validation, compact prompt rendering, and adjacent-lane duplication audit
   - `oracle`: a new golden/oracle is being proposed
   - `adequacy`: an `A1` calibration batch may be ending or being promoted too early
   - `validation`: a non-trivial task needs a lightweight Validation Handoff Packet before final validation
   - `bdd-sync`: a maintained non-unit behavior validation surface may need BDD gate/case/semantic scenario synchronization
   - `contract-delta`: an approved artifact may contain stable contract or promotion deltas that need KB/Dashboard/gate/runtime routing
   - `semantic`: a task may need Semantic Reviewer or an explicit no-escalation note
   - `dashboard-agent`: the user is asking for a Dashboard Agent refresh, strategic next-step report, or Dashboard update proposal
   - `reader-explanation`: a final answer or closeout needs Chinese explanation for compressed conclusions
   - `closeout`: the task is nearing final summary
   - `closeout-language`: a Dashboard closeout artifact needs executable Chinese-heading and English-verdict explanation validation before final completion wording
   - `semantic-diagnostic`: a Validation Agent, Semantic Reviewer, Dashboard Agent, or closeout needs to name the semantic failure class and memory layer
   - `all`: multiple checkpoints are relevant in the same task
3. Run the deterministic checklist helper if useful:

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode intake-evaluation
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode sgc
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode multi-agent
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode design
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode lane-task-card
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode goal-conformance
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode goal-agent
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode loop-continuation
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode validation-agent
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode context-bootstrap
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode context-efficiency
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode oracle
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode adequacy
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode validation
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode bdd-sync
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode contract-delta
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode semantic
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode semantic-diagnostic
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode reader-explanation
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode closeout
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode closeout-language --file Dashboard/Artifacts/<...>_Closeout.md
```

Context-efficiency tooling：

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/context_state.py collect --help
python3 .codex/skills/sge-governed-checkpoints/scripts/context_state.py compare --help
python3 .codex/skills/sge-governed-checkpoints/scripts/context_state.py usage <fresh-single-turn-rollout.jsonl>
python3 .codex/skills/sge-governed-checkpoints/scripts/goal_patch.py validate-goal <goal.json>
python3 .codex/skills/sge-governed-checkpoints/scripts/goal_patch.py resolve <goal.json> <patch.json>...
python3 .codex/skills/sge-governed-checkpoints/scripts/goal_patch.py audit-duplication <audit-input.json>
python3 .codex/skills/sge-governed-checkpoints/scripts/context_bootstrap.py validate <packet.json>
python3 Dashboard/tools/sge/s002_erbe_acceptance.py
python3 .codex/skills/sge-governed-checkpoints/scripts/context_bootstrap.py render <packet.json>
```

这些工具只提供 deterministic evidence。`context_bootstrap.py validate` 只验证 packet 结构与声明，不验证引用 path/digest 真实性、读取已发生或任务质量；`delta_safe` 不等于 Validation pass，resolved Goal 不等于 Scope Delta 获批，token reduction 不等于费用或普遍节省规律。

1. For `intake-evaluation` work, evaluate the instruction candidate before execution by default.
   - default every user instruction to evaluate-then-execute; if the user explicitly asks to execute directly, only skip visible evaluation prose while still doing the internal minimum check and required hard gates
   - minimum check: objective, source authority, repo/KB/Dashboard boundary, material risks or missing information, and execution route
   - keep it proportional: trivial low-risk tasks can pass silently, but persistent edits, external side effects, proposals, attachments, approval text, contracts, KB/Dashboard, acceptance/gate, or semantic-promotion work needs an explicit intake verdict before action
   - direct-execution requests may skip visible evaluation prose, but they do not bypass safety, destructive-action approval, higher-priority instructions, source-of-truth boundaries, or governed KB/contract/acceptance gates
   - choose one route: execute as-is, narrow, ask, refuse, or escalate to another checkpoint such as multi-agent, contract-delta, validation, semantic, or closeout
2. For `sgc` work, apply SGC v1 Structural Contract proportionally on non-trivial SGE tasks.
   - use `kb/data/strategy/strategy_sgc_structural_contract_v1.json` as canonical truth and the rendered Markdown for reading
   - trigger on semantic-risk implementation decisions, contract/governance edits, completion or validation claims, promotion claims, runtime widening, or KB/Dashboard truth-placement decisions
   - classify the strongest claim level: `execution_bound`, `test_bound`, `structurally_supported`, `externally_supported`, `inference_only`, or `ungrounded`
   - check forbidden collapses: schema substitution, recompute validation, profile/routing collapse, deterministic masking, mock grounding, and false closure
   - check structural invariants SI-1 through SI-6, especially whether the completion or promotion claim exceeds evidence and whether the original objective is still covered
   - narrow or block `done`, `validated`, `correct`, or `promoted` wording when evidence only supports a weaker claim
   - do not activate SGC v2/v3, numeric scoring, universal output formats, ledger requirements, runtime behavior changes, schema changes, or acceptance posture changes through this v1 check
3. For `multi-agent` work, treat tracked Session / Stage Plan execution and non-trivial governed work as governed multi-agent by default.
   - standing user authorization applies to future SGE non-trivial governed tasks: AI is explicitly authorized to use subagents / delegation as needed, subject to the Multi-Agent Activation Gate
   - AI may decide to start subagents / delegation from the Multi-Agent Activation Gate even when the user has not explicitly asked for subagents
   - after C0 approval, automatically enter governed implementation mode for the approved scope unless the user explicitly says single-agent / no multi-agent or the task is truly trivial
   - start Design Agent, Builder, Validation Agent, and Closure Agent lanes before substantial work unless the user explicitly says single-agent or the task is truly trivial
   - keep Orchestrator on the control plane where possible
   - remember that a Design Artifact / Design Handoff is input to Builder and Validation, not implementation approval or Semantic Reviewer replacement
   - remember that a Validation Handoff Packet is input to Validation, not a Validation Agent verdict
   - if a default lane is not started, record a `Single-Agent Exception` in the closeout artifact with reason, risk, compensating checks, and whether independent design or validation is missing; user silence about subagents is not by itself a valid reason
   - when the Goal explicitly requires an independent user-visible execution task, record the task/thread id, worktree when applicable, and where Builder actually ran; a placeholder task that stops before Builder does not satisfy the requirement
   - Orchestrator takeover of an explicitly independent Builder task is a topology Scope Delta; require a human-approved topology exception with a durable approval reference before full conformance can be claimed, and do not let compensating tests retroactively erase the delta
4. For `design` work, prepare and save the post-C0 Design Agent artifact.
   - run this after C0 approval and before the dominant Builder lane starts implementation
   - store it by default as `Dashboard/Artifacts/<SessionID>_<ShortTopic>_Design.md` for a tracked session or `Dashboard/Artifacts/<StageID>_<ShortTopic>_Design.md` for a Stage Plan / multi-session batch
   - include C0 authority consumed, plain-language objective, scope and non-goals, current architecture read, proposed module/data/API/contract design, implementation slices and ownership, test and gate plan, risks and escalation triggers, Builder handoff, Validation focus, design delta policy, and artifact path
   - keep the lane design-doc-only unless explicitly assigned otherwise; do not implement code, change golden/contract/acceptance posture, or replace Semantic Reviewer
   - if Builder materially diverges from the saved design, require a Design Delta in the closeout with rationale and whether human, Validation, or Semantic Reviewer review was needed
5. For `goal-conformance` work, preserve the original Goal and prevent unapproved scope substitution.
   - run after C0 approval, before Builder implementation starts, and again before closeout
   - split the original user Goal / Stage Plan / approved plan into a must-have ledger before dominant Builder work; each item needs source text or pointer, intended outcome, acceptance evidence, owner/lane, and status
   - if any original must-have is deleted, narrowed, replaced, or deferred, record a Scope Delta entry with: original requirement, reason for removal/replacement, revised requirement, impact, whether human approval is required, approval status/reference, and whether a deferred session is required
   - require human approval before marking an unapproved deletion/replacement as accepted scope; silence, Builder convenience, or Validation-only acceptance of a revised design is not approval
   - instruct Validation to check both the revised design and the original Goal / must-have ledger; validation that only verifies the revised design cannot support `done`, `validated`, or `SP complete`
   - closeout must include an `Original Plan Coverage Matrix` that maps every must-have to `landed`, `not landed human-approved deferred`, `not landed blocked`, or `not applicable with reason`
   - include process must-haves in that matrix, including required visible tasks, lane ordering, pre-Builder review, independent final review, and post-closeout reconciliation; feature-only coverage is incomplete coverage
   - if any original must-have remains not landed without approved deferral, not-applicable rationale, or blocker/termination status, do not write `SP complete`, `Goal complete`, or equivalent full-completion wording; close as partial, blocked, narrowed pending approval, or with explicit deferred sessions
   - this gate is a governance/checklist guard only; it does not activate SGC v2/v3, numeric scoring, ledger-as-schema requirements, runtime behavior changes, schema changes, or acceptance-posture changes
6. For `goal-agent` work, turn the user's intent and repo truth into a durable execution prompt.
   - treat the Goal Prompt as a handoff contract for later AI and human readers, not as a chat summary or implementation artifact
   - read the requested thread/context, current repo governance, Dashboard row/stage plan, acceptance criteria, related design/closeout, and KB truth needed for the specific Goal; record a Read Manifest with read, missing, skipped, and stale-risk items
   - first explain the task in Chinese: what it asks, covered G/SP/Session items, prerequisites, boundaries, non-goals, and false-closure risks
   - preserve the original scope as a must-have ledger, including acceptance/evidence expectation and required validation surface
   - include default execution configuration, mandatory reading, required outputs, must-have ledger, non-goals, forbidden claims, CG status, governance workflow, validation handoff, Semantic Reviewer triggers, closeout-language gate, KB/Dashboard review, termination conditions, and allowed/forbidden closeout wording
   - if the Goal will call a Validation Agent, require `guardrail_checklist.py --mode validation-agent` and the fixed read-mostly Validation Agent Prompt before any validation verdict
   - if no external CG input exists, record exactly `CG skipped: no CG input provided`; do not infer or invent a CG review
   - never let "stop expanding scope", "land the minimum", "give final verdict now", or similar Orchestrator pressure waive mandatory evidence or gates
   - if mandatory evidence is incomplete, the valid response is: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`
7. For `validation-agent` work, apply the fixed Validation Agent prompt before giving a verdict.
   - default to read-mostly; do not repair Builder output unless the human explicitly assigns repair work
   - build a Read Manifest before verdict: source thread or handoff packet, `AGENTS.md`, this skill, Dashboard rows / Stage Plan, Current State, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, related design / closeout artifacts, Agent Logs, KB truth, changed files, and gates/tests evidence
   - first explain the task in plain Chinese for the human owner: what it tried to do, what it claims, what it does not prove, and where the main risk is
   - check both original objective coverage and revised/landed artifacts; revised-design-only validation cannot support pass/done/SP complete/Goal complete
   - identify as many evidence-grounded quality issues as useful: scope narrowing, overclaim, missing artifacts, weak tests, stale Dashboard rows, KB/Dashboard truth split errors, untracked follow-ons, false closure, acceptance/gate gaps, semantic-risk triggers, and hard-to-repair technical debt
   - separate blocking findings, non-blocking findings, open questions, required Builder repair, and verdict
   - before accepting an `Independent Validation passed` claim, locate a durable Validation Review or post-closeout reconciliation artifact and verify reviewer/source, Read Manifest, actual closeout binding, final Dashboard/KB state, and final diff; handoff packets and Semantic Review are not substitutes
   - if Orchestrator asks to immediately converge before required evidence is complete, answer exactly in substance: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`
8. For `context-bootstrap` work, construct the profile-specific packet before task execution.
   - classify the task as `read_only`, `implementation`, or `validation`; trivial low-risk tasks may use an implicit equivalent packet
   - preserve Raw User Intent as authority and mark Intake only as projection
   - declare boundaries, Required/Conditional Read Sets, Semantic Refresh, required epistemic domains, change impact, and topology
   - support both deterministic and evidence-backed agent-evaluated triggers; agent judgment may expand reads but never suppress a deterministic trigger
   - refresh objective, authority, claim ceiling, and critical dependencies even when source digests are unchanged
   - base topology on change impact, not artifact type alone; render stable rules as path@revision/digest plus applicability and reason
   - if a required epistemic domain is missing, expand reads or report an evidence gap; never trade required search space for token savings
9. For `context-efficiency` work, compress by reference and delta without weakening evidence.
   - use Global Governance Context -> Loop Goal -> current Session Task Card; do not paste stable governance, all Session history, or full AC into every prompt
   - use Goal Patch after review and emit one fully resolved Final Goal before Builder; patches carry base revision, sequence, conflicts, reason, and Scope Delta impact
   - first Validation establishes a complete baseline; later rounds use Validation State Snapshot plus deterministic tracked/untracked/renamed/generated inventory and Delta Read Set
   - rebaseline on user/Goal/governance/AC/authority/claim/truth/topology/threat/snapshot changes or when final diff exceeds the declared delta
   - separate Validation Reviewer, Adversarial Tester, and Governance Architect outputs; future hardening is not a blocker unless current AC/contract or approved Scope Delta makes it one
   - use initial validation -> blocker-fix delta validation -> final-state reconciliation as the default convergence path; repeated same-root blockers trigger rebaseline/hardening/human scope decision instead of an unbounded micro-patch loop
   - allow a single independent Validation lane only for narrow read-only delta reconciliation; implementation or semantic/authority changes still require applicable lanes
   - keep working updates and Agent Logs delta-first; formal Validation/closeout artifacts retain the full durable evidence
10. For `validation` work, prepare a concise `Validation Handoff Packet`.
   - store it by default in the task's Dashboard closeout artifact under a `验证交接包` section
   - when Agent Log default applies, copy or link the handoff packet from the relevant `Dashboard/Agent_Logs/` lane log
   - claimed scope
   - claimed semantic change
   - explicit non-goals
   - files/artifacts changed
   - gates/tests run
   - evidence produced
   - known risks
   - KB/Dashboard impact
   - `Closeout language verdict`: whether `closeout-language` explicitly passed; missing, failed, blocked, pending, or not-run verdicts block final completion wording
   - when semantic failure or memory-layer risk is relevant, classify S1-S6, identify L0-L6, map the countermeasure, check whether the repair is implemented as code / contract / gate / runtime / closeout / KB / prose, and decide the correct memory layer
11. For `bdd-sync` work, check whether behavior-contract changes require BDD updates.
   - trigger when the task adds, removes, renames, or materially changes a maintained non-unit deterministic gate, shared validator, runtime/contract/matrix gate, phase acceptance gate, runtime-oracle gate, repo/facade/matrix gate, or an enumerable internal case inside such a gate
   - do not trigger only because a unit or seam test changed; unit/seam tests remain implementation-level unless they are promoted into a maintained non-unit gate or shared validator
   - if a new behavior is discovered, first add or update the appropriate contract/acceptance/runtime/matrix gate or shared validator, then add or update the BDD scenario that delegates to that authority
   - if a legacy gate's internal case list changes, update `tests/bdd/support/case_catalog.py` and rerun `python3 tests/bdd/run_bdd_validation.py --list`
   - if C2/C3 mapping may be affected, rerun `python3 tests/bdd/run_bdd_validation.py --audit-semantic-coverage --strict-semantic-coverage`
   - if closeout claims reader-facing cards landed, write them to `tests/bdd/readable_cards/<gate>/` (for example with `--report-dir tests/bdd/readable_cards/<gate>`); `.sge/reports` or `/tmp` output is transient validation evidence, not a durable card artifact
   - if BDD text, level, migration batch, authority rule, or coverage rule changes, update `tests/bdd/README.md` and the relevant KB strategy surfaces
   - record either the BDD files changed and commands run, or the explicit reason BDD did not need a file update
12. For `contract-delta` work, scan approved artifacts for stable truth deltas before closeout.
   - trigger on approved proposals, closeouts, reviewed seeds, accepted baselines, matrices, contracts, or acceptance/gate artifacts when they contain stable contract, semantic, trust/disposition, blocking/advisory, promotion, non-goal, or terminology claims
   - review the content claim's truth layer instead of the artifact's filesystem location
   - classify each actual delta as `promote-to-KB`, `Dashboard-only`, `gate-docs later`, `runtime/tests later`, or `deferred session`
   - use the short table shape: Delta claim | Trigger | Classification | Rationale | Follow-up
   - `promote-to-KB` means extract the stable reusable subset into KB JSON with source scope, then render Markdown; it does not mean copying the whole Dashboard artifact
   - if no KB update lands, record why no stable truth changed or why the claim remains Dashboard-only evidence
   - if follow-up is concrete and out of scope, add or update a bounded Dashboard session instead of leaving it in closeout prose
13. For `semantic` work, scan whether a Semantic Reviewer lane is required.
   - start it when requested by the human or Stage Plan
   - start it when Orchestrator/Validation records semantic-risk escalation
   - if a trigger exists but the lane is not started, record why in closeout or the relevant Dashboard row
   - when Semantic Reviewer starts, require two verdicts: `Design Freeze Validity` for boundary/truth/scope/overclaim and `Implementation Entry Readiness` for safe next implementation entry
   - `Design Freeze Validity` checks whether the artifact stays inside design/target-only authority, avoids runtime implementation claims, preserves KB/Dashboard/derived-evidence/human authority split, blocks false closure, blocks unapproved Scope Delta, and separates current implementation status from target design
   - `Implementation Entry Readiness` checks what Builder may implement next, the smallest executable slice, required input artifacts, required output artifacts, acceptance evidence, explicit non-goals, next-session map, and whether the next session can start without redesigning the whole artifact
   - for large design objects, require an implementation ladder; examples include evidence graph -> validator -> append-only observation store -> structural diff observation -> review advisory model, controller route candidate -> route validator -> planner DAG -> single adapter -> first bounded slice, and execution posture budget/retry minimum -> persistent context refs -> cost/resource observation -> parallel eligibility -> operator surface
   - run a terminology compression test on status/title/row/closeout words such as `done`, `landed`, `active`, `covered`, `complete`, `closed`, `integration`, `support`, `foundation`, and `ready`; prefer safer wording such as `covered-in-design-freeze`, `design-freeze-done`, `target-contract-active`, `mapped-and-bounded`, and `support-evidence-only`
   - write at least three future-agent misuse scenarios for high-risk artifacts and state mitigations
   - if the artifact mostly says what not to claim but lacks positive implementation entry, raise at least P1 follow-up for semantic bureaucracy / implementation dead-end risk
   - if Orchestrator asks to immediately converge before required evidence is complete, answer in substance: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`
   - if Semantic Reviewer starts, require Frame-First Review before artifact-local consistency:
     - authority level, layer separation, core ontology nouns, and claim/evidence mapping
     - semantic invariants, generalization failure taxonomy, and cross-family transfer rules
     - negative space, likely future misuse, and promotion boundary
   - before field-level fixes, require Semantic Architecture Review:
     - truth carrier audit: semantic law, witness evidence, evaluation result, governance decision, or accidental mix
     - object responsibility audit: whether the artifact is becoming a God Object or semantic bureaucracy
     - complexity trajectory: what this artifact becomes after repeated extensions
     - half-schema / DSL boundary: whether formal fields need parser, validator, versioning, and evolution rules
     - law quality: whether invariants and capability families have executable or reviewable semantics rather than labels or intuition
   - use the S1-S6 semantic inconsistency taxonomy and L0-L6 diagnostic alignment surfaces as SGE reviewer vocabulary when naming issues, not as a numeric scorecard or universal science claim
14. For `semantic-diagnostic` work, apply the bounded diagnostic lens.
   - classify the failure: S1 intent misalignment, S2 semantic drift, S3 semantic overclaim, S4 semantic ambiguity, S5 semantic unverifiability, or S6 semantic authority confusion
   - identify the surface: L0 semantic memory, L1 intent, L2 capability, L3 execution, L4 collaboration, L5 validation, or L6 runtime evolution
   - map the countermeasure: constitution, contract, oracle/golden, candidate trial, deterministic gate, validation handoff, Semantic Reviewer, closeout evidence, Dashboard candidate memory, or KB promotion
   - check the implementation surface: code, contract, gate, runtime behavior, closeout artifact, KB truth, or only prose
   - decide the memory layer: `kb/`, `Dashboard/`, tests/examples/reports, runtime, or reader-facing explanation
   - preserve the taxonomy boundary: the taxonomy is canonical vocabulary and a diagnostic lens; it does not change runtime/schema/gate/acceptance/product policy, does not make Semantic Reviewer mandatory for every task, and is not a universal science claim
   - examples: promotion provenance repair is mainly a truth-layer issue; hardcoded path tracking is mainly an authority/validation issue until a scoped hardening task promotes it into contract/gate/runtime work
15. For `reader-explanation` work, expand compressed conclusions for the human reader.
   - trigger on user-facing final answers, Dashboard closeouts, closeout-style summaries, validation verdicts, KB/Dashboard review lines, next-candidate recommendations, or semantic no-escalation notes when they use shorthand that affects judgment
   - common triggers include `passed`, `done`, `blocked`, `candidate-only`, `Dashboard-only`, `no KB update`, `no-escalation`, `scope narrowed`, `deferred`, `generalized=true`, `promotion_allowed=true`, gate verdicts, and bare session/SP ID lists
   - explain in Chinese what the conclusion means, what it allows the reader to infer, what it does not prove, what evidence or boundary it depends on, and what next action follows
   - in closeout artifacts, add `关键结论中文展开` when compressed conclusions are present; in final chat, use a shorter `这意味着什么` paragraph when a full table would be too heavy
   - keep the explanation proportional: do not repeat raw logs, do not translate every technical term mechanically, and preserve exact English only when it is necessary evidence
   - remember that explanation is not truth promotion: stable rules still belong in `kb/`, execution memory belongs in `Dashboard/`, and reader-facing prose does not change runtime/schema/gate/acceptance behavior by itself
16. For `dashboard-agent` work, keep the mode strategic and proposal-first.
   - use `exploration-dashboard-synthesizer` for a full refresh or first report
   - read the current Dashboard surface and relevant `kb/` truth before judging next steps
   - default to three next-step candidates: quality/stability, speed/progress, and blue-sky
   - list archive / cancel / rewrite / add proposals with evidence
   - do not write Dashboard rows unless the human explicitly asks for a Dashboard update
17. For `oracle` work, treat the first artifact as a proposal, not frozen truth.
   - summarize what the proposed oracle is trying to encode
   - call out any non-obvious wording/taxonomy/boundary choices
   - give the human a short review window before treating it as frozen
   - only skip that pause if the human explicitly delegates the semantic choice
18. For `closeout` work, run an explicit deferred scan.
   - create or update `Dashboard/Artifacts/<SessionID>_<ShortTopic>_Closeout.md` for a tracked session, or `Dashboard/Artifacts/<StageID>_<ShortTopic>_Closeout.md` for a Stage Plan / multi-session batch
   - use Chinese closeout headings by default: `关键结论中文展开`, `落地范围`, `原始目标覆盖矩阵`, `范围变更复核`, `Lane 启动与例外`, `设计交接`, `验证交接包`, `验证结论`, `明确非目标`, `证据`, `运行的门禁`, `语义复核`, `延后范围`, `KB/Dashboard 复核`, and `后续候选`
   - write the closeout artifact and final closeout summary in Chinese by default; translate or summarize English lane/tool evidence into Chinese unless exact English is necessary evidence
   - when compressed conclusions are present, include `关键结论中文展开` with original conclusion, Chinese meaning, judgment impact, evidence/boundary, and next action
   - in reader-facing Closeout, final summary, Dashboard parent/row prose, and `验证交接包` explanation, cite the exact source artifact with a clickable Markdown link instead of printing a bare SHA-256/hash/digest value; keep machine-required digests only in lane cards, manifests, snapshots, JSON, or validation evidence and link to those files from the Closeout
   - after the artifact exists, run `guardrail_checklist.py --mode closeout-language --file <closeout.md>` and block final completion wording on failure
   - ensure the final Validation / Semantic evidence actually covers the closeout, final Dashboard/KB state, and final diff; a verdict written before those surfaces existed, especially one that still lists closure blockers, requires an independent post-closeout reconciliation before `done`
   - before any non-trivial governed closeout enters a final completion state, link the durable final Validation Review or reconciliation artifact even if the closeout omits an explicit Validation claim; require one non-conflicting passing verdict, one reviewer/source, and a positive Read Manifest over the actual closeout, final Dashboard/KB state, and final diff
   - reject omitted, duplicate, or conflicting verdict/reviewer/read records; do not cite only a Validation Handoff, tests, Semantic Review, or Orchestrator summary
   - for multi-session final audits, add an Evidence Completeness Matrix covering each Session's technical scope, process must-haves, visible-task topology, final reviewer timing, closeout, parent surfaces, and Scope Delta
   - treat the Original Plan Coverage Matrix as an evidence matrix, not a keyword index: every original must-have/AC needs a row or an explicit grouping rationale with itemized child rows; each row must contain the original requirement, observable acceptance predicate, exact source-file Markdown link, observed result, status, blocker/exception, owner/lane or timing, claim ceiling, and parent/Closeout absorption state. A matrix missing these fields cannot support `done`, `Goal complete`, or final `PASS`
   - reference the closeout artifact from the changed Dashboard row
   - run the `contract-delta` scan when approved artifacts contain contract, semantic, trust/disposition, blocking/advisory, promotion, non-goal, or reusable terminology claims
   - ask whether any scope was intentionally narrowed
   - ask whether any concrete refinement or later candidate became visible
   - if yes, record it in `Dashboard/Sessions.md` even when it is only `P2`
   - if no, say so explicitly in the final summary
19. For `closeout-language` work, run the executable language gate against the closeout artifact.
   - require a concrete closeout file path; without a file, the helper only prints the checklist and cannot support completion
   - fail closeout on pure-English H1/H2 headings such as `## Validation Verdict` or `## Landed Scope`
   - fail closeout on English verdict/status/routing labels such as `pass`, `blocked`, `done`, `Dashboard-only`, or `promote-to-KB` when the line or section lacks Chinese explanation
   - skip fenced code blocks so commands, paths, schema fields, and exact evidence can remain intact when the surrounding prose explains them
   - require an explicitly passing `Closeout language verdict` inside `验证交接包`; a failed, blocked, pending, or not-run verdict is still a closeout blocker
   - require reader-facing evidence citations to use clickable source-file links rather than bare SHA-256/hash/digest numbers; exact digests remain valid in machine-readable evidence files and are not a substitute for a human-readable source link in Closeout
20. For `adequacy` work, do not let `A1` end on vibes.
   - require a phase-specific prompt rather than generic prompting
   - require preserved `run1 ... runN` evidence rather than only a final success case
   - default to at least 5 effective runs unless the human explicitly waives that floor
   - require at least one maintained positive shape, one boundary/negative shape, and one prompt-revision rerun
   - require an explicit adequacy report: what failed, what changed, what is still unresolved, and whether the pressure points point at contract, prompt, or golden/oracle
   - if the newest runs are still surfacing new material failure modes, do not present `A1` as complete
   - if the reviewed seed is stable and the remaining drift can be rewritten as deterministic blocking/advisory rules, allowed normalization, or explicit exclusions, pivot from prompt micro-tuning into `A2` acceptance hardening
   - second-model trials are optional calibration evidence, not a default escalation; use them only after intra-model stability is understood and only when the extra model can answer a concrete calibration question
   - on new or unstable phases, give the human a short adequacy review window before treating `A1` as ready for `A2`
21. After the checklist, still perform the normal KB/Dashboard review.

## Hard Stops

- Do not present a newly drafted oracle as already frozen if the user has not reviewed or approved it.
- Do not execute a user instruction, attachment, proposal, or approval text as authoritative implementation work before at least a proportional intake evaluation has checked objective, authority, boundaries, risks, and route.
- Do not treat a user request for direct execution as a waiver of safety checks, destructive-action approval, higher-priority instructions, source-of-truth boundaries, or governed KB/contract/acceptance gates.
- Do not treat `执行 S-xxx`, `启动 S-xxx`, `execute S-xxx`, or `执行 SP-xxx` as single-agent by default in this repo.
- Do not start dominant post-C0 Builder implementation without either a saved Design Agent artifact or a recorded exception explaining why design was skipped.
- Do not start dominant Builder work after C0 without a Goal / original-plan must-have ledger when the task is executing a Goal, Stage Plan, or approved plan.
- Do not let Builder replace or narrow original Goal must-haves without a Scope Delta entry and required human approval.
- Do not let Validation claim readiness by checking only the revised design when the original Goal contained must-haves that may have been removed, substituted, or deferred.
- Do not write `SP complete`, `Goal complete`, or equivalent full-completion wording when an original must-have remains not landed without approved deferral, not-applicable rationale, or blocker/termination status.
- Do not finalize a Goal Prompt without a Read Manifest, Chinese task explanation, must-have ledger, non-goals, forbidden claims, validation focus, Semantic Reviewer triggers, closeout-language gate, KB/Dashboard review, termination conditions, and allowed/forbidden closeout wording.
- Do not let Orchestrator pressure for "minimal" or "immediate" closure waive required Goal Agent or Validation Agent evidence and gates; if evidence is missing, answer `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`
- Do not rely on notes, chat memory, or “we can remember this later” for a concrete deferred follow-on.
- Do not present `A1` as complete when there is no phase-specific prompt, no adequacy report, no preserved failed attempts, or only 1-2 lightly compared runs without explicit human waiver.
- Do not keep iterating prompt wording as the default move once the reviewed seed is stable and the remaining disagreement is only canonical-field or exactness oscillation that deterministic acceptance can absorb.
- Do not skip the `Validation Handoff Packet` for non-trivial work; Agent Logs are default for non-trivial governed multi-agent execution, tracked Session / Stage Plan lanes, and triggered Semantic Reviewer lanes, but the handoff packet remains validation input rather than a verdict.
- Do not change maintained non-unit behavior gates or their enumerable cases without either updating the corresponding BDD layer or recording why no BDD file update is required.
- Do not treat Design Artifact / Design Handoff as optional polish on post-C0 implementation work; it is the default implementation boundary for Builder and review input for Validation.
- Do not treat Semantic Reviewer as either always-on or irrelevant; it is a triggered governance lane, and visible semantic-risk triggers need either escalation or an explicit no-escalation note.
- Do not use S1-S6 / L0-L6 as a numeric scorecard, universal science claim, or hidden policy change. It is reviewer vocabulary for selecting the right stabilizing surface.
- Do not conclude "no KB update" solely because the source artifact is under `Dashboard/` when its approved content defines stable contract, semantic, trust/disposition, gate, promotion, non-goal, or terminology truth.
- Do not promote an approved Dashboard artifact wholesale into KB; promote only the reviewed stable subset through KB JSON source, or record why it stays Dashboard-only.
- Do not let Semantic Reviewer pass a proposal, contract, gate, Arena, pattern-level artifact, or release/generalization claim only because local wording is conservative when ontology layers, semantic family definitions, invariants, failure taxonomy, or transfer rules are missing.
- Do not let Semantic Reviewer give a full pass only because no-overclaim / no-truth-contamination is satisfied; for design or target-freeze artifacts it must also review implementation-entry readiness, minimum safe slice, implementation ladder, next-session map, future-agent terminology compression, and likely misuse scenarios.
- Do not let a large architecture object such as an evidence graph, controller, planner, executor, posture, or production readiness move from design freeze toward implementation without either a minimum executable slice and ladder or a P1 follow-up that blocks broad implementation start.
- Do not let Orchestrator pressure for "final verdict now" make Semantic Reviewer skip mandatory files, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, or closeout-language gate; missing mandatory evidence means blocked/partial, not pass/done.
- Do not repair a God Object by adding more governance metadata; first decide whether semantic law, witness evidence, evaluation result, and governance decision belong in separate artifacts.
- Do not let case cards, matrix rows, profile samples, or reports become semantic truth carriers by accumulation; they are usually witnesses unless a later promotion explicitly moves law/ontology/invariant truth into `kb/`.
- Do not let Dashboard Agent mode silently become implementation work or automatic Dashboard mutation; it is proposal-first unless the human explicitly approves an update.
- Do not treat the final chat response as the only durable closeout for non-trivial governed work; use the Dashboard closeout artifact unless the task is truly trivial or intentionally single-message.
- Do not compress Agent Logs into retrospective summaries when visible working notes, tool actions, gate outcomes, repairs, and final outputs can be preserved as a high-fidelity visible execution trace. Use the current Session Agent Log as the detail reference; still do not claim to export model-private chain-of-thought.
- Do not leave task closeout artifacts or final closeout summaries in English by default; SGE task closeouts should be Chinese unless exact English evidence is required.
- Do not leave compressed status, gate, KB/Dashboard routing, semantic-risk, scope, deferred-work, or next-candidate conclusions unexplained when the human needs the meaning for judgment. Chinese output still fails the rule if it only repeats shorthand without explaining impact, boundary, and next action.
- Do not claim final completion for a non-trivial governed task if `closeout-language` was not run on the closeout artifact, failed on pure-English H1/H2 headings or unexplained English verdict/status labels, or the `验证交接包` lacks an explicitly passing `Closeout language verdict`.

## Output Expectation

Your user-visible progress update should make the checkpoint explicit:

- `phase workflow`: say you are materializing the current phase/stage workflow contract before substantial work
- `intake-evaluation`: say you are evaluating the request's objective, authority, boundaries, risks, and execution route before acting when the task is non-trivial or persistent
- `multi-agent`: say you are running the Multi-Agent Activation Gate and defaulting tracked/non-trivial governed work to Design / Builder / Validation / Closure lanes unless an exception is recorded
- `design`: say you are saving the post-C0 Design Agent artifact before dominant Builder implementation, or recording an explicit exception
- `goal-agent`: say you are turning the request and repo truth into a durable Goal Prompt handoff contract, with Read Manifest, must-have ledger, validation focus, and anti-pressure completion rules
- `validation-agent`: say you are applying the fixed Validation Agent prompt, building the Read Manifest, and checking original objective coverage plus landed evidence before verdict
- `oracle`: say you are drafting a proposal for review before freeze
- `adequacy`: say you are checking whether `A1` has enough prompt/run evidence and adequacy reporting before promotion
- `validation`: say you are preparing the lightweight Validation Handoff Packet before final validation
- `bdd-sync`: say you are checking whether maintained non-unit gate or case changes require BDD gate/case/semantic scenario updates
- `contract-delta`: say you are scanning approved artifacts for stable contract or promotion deltas and routing each delta to KB, Dashboard, gate docs, runtime/tests, or a deferred session
- `semantic`: say you are scanning for Semantic Reviewer triggers and, when triggered, applying Protocol v2 with Design Freeze Validity plus Implementation Entry Readiness before field-level consistency
- `semantic-diagnostic`: say you are classifying S1-S6, locating L0-L6, mapping the countermeasure, checking implementation surface, and deciding the memory layer without turning the taxonomy into a scorecard or policy change
- `reader-explanation`: say you are expanding compressed conclusions into Chinese meaning, judgment impact, evidence/boundary, and next action
- `dashboard-agent`: say you are reconstructing the Dashboard/KB panorama and keeping Dashboard updates proposal-first unless asked to write them
- `closeout`: say you are creating or updating the Dashboard closeout artifact and doing the deferred/emergent-session scan before final closeout
- `closeout-language`: say you are running the executable Chinese closeout-language gate against the closeout artifact before final completion wording

Keep the checkpoint wording short, but do not skip it.
