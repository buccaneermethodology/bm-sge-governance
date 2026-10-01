#!/usr/bin/env python3
"""Print short governance checklists for SGE checkpoint-sensitive work."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MULTI_AGENT_LINES = [
    "Multi-Agent Default Guard",
    "- In this repo, tracked Session / Stage Plan execution and non-trivial governed work default to governed multi-agent mode.",
    "- Standing user authorization applies to future SGE non-trivial governed tasks: AI is explicitly authorized to use subagents / delegation as needed, subject to the Multi-Agent Activation Gate.",
    "- Current-turn tool compatibility: repo-provided execution templates should include `本轮显式授权 Codex 按需使用 subagents / delegation / parallel agent work；是否启用由 Multi-Agent Activation Gate 决定。` when governed multi-agent mode should be available.",
    "- AI may decide to start subagents / delegation from the Multi-Agent Activation Gate even when the user has not explicitly asked for subagents.",
    "- Treat `execute/start S-xxx` or `execute/start SP-xxx` as sufficient authorization for Design Agent, Builder, Validation Agent, and Closure Agent lanes unless the human says single-agent.",
    "- After C0 approval, automatically enter governed implementation mode for the approved scope unless the human says single-agent / no multi-agent or the task is truly trivial.",
    "- User silence about subagents is not itself a valid Single-Agent Exception reason.",
    "- Run this gate before substantial work, not only during final closeout.",
    "- A Design Artifact / Design Handoff is input to Builder and Validation, not implementation approval or a Semantic Reviewer substitute.",
    "- A Validation Handoff Packet is input to Validation, not a Validation Agent verdict.",
    "- If a default lane is not started, record Single-Agent Exception in the closeout artifact with reason, risk, compensating checks, and whether independent Design or Validation is missing.",
]

DESIGN_LINES = [
    "Design Agent Guard",
    "- For post-C0 implementation or non-trivial governed batches, save a Design Agent artifact before dominant Builder work unless there is a recorded exception.",
    "- Default path: Dashboard/Artifacts/<SessionID>_<ShortTopic>_Design.md or Dashboard/Artifacts/<StageID>_<ShortTopic>_Design.md.",
    "- Include objective, scope/non-goals, current architecture read, module/data/API/contract design, implementation slices, test/gate plan, risks, Builder handoff, Validation focus, and design delta policy.",
    "- Design handoff is not implementation approval, a Validation verdict, or a Semantic Reviewer substitute.",
    "- If Builder materially diverges from the design, record the Design Delta in closeout with rationale and review needs.",
]

INTAKE_EVALUATION_LINES = [
    "Task Intake Evaluation Guard",
    "- Default every user request to evaluate-then-execute; if the user explicitly asks to execute directly, only skip visible evaluation prose while still doing the internal minimum check and required hard gates.",
    "- Minimum check: objective, source authority, repo/KB/Dashboard boundary, material risks or missing information, and action decision.",
    "- Keep it proportional: trivial low-risk commands can use a very light implicit check; non-trivial repo, proposal, approval, contract, KB, Dashboard, acceptance/gate, or semantic-promotion work needs an explicit evaluation verdict before edits.",
    "- Direct-execution requests do not bypass safety, destructive-action approval, higher-priority instructions, source-of-truth boundaries, or high-risk contract/KB/acceptance checks.",
    "- If an artifact asks to evaluate reasonableness, do not treat it as implementation approval until the evaluation verdict is stated.",
]

SGC_LINES = [
    "SGC v1 Structural Contract Guard",
    "- Use for every non-trivial SGE task, proportionally, when the task makes or changes semantic-risk implementation, validation, completion, promotion, runtime-widening, or KB/Dashboard truth-placement claims.",
    "- Canonical truth: kb/data/strategy/strategy_sgc_structural_contract_v1.json; rendered reading surface: kb/docs/strategy/Strategy_SGC_Structural_Contract_V1.md.",
    "- Classify the strongest claim level: execution_bound, test_bound, structurally_supported, externally_supported, inference_only, or ungrounded.",
    "- Check forbidden collapses: schema substitution, recompute validation, profile/routing collapse, deterministic masking, mock grounding, false closure, and scope substitution.",
    "- Check SI-1..SI-6: truth is not structure, grounding completeness, decision surface validity, non-tautological validation, authority-execution coupling, and original objective coverage.",
    "- Use the separate goal-conformance guard to materialize the original Goal ledger, Scope Delta entries, and Original Plan Coverage Matrix.",
    "- Do not claim done, validated, correct, or promoted unless claim level and preserved evidence match the asserted strength.",
    "- Do not activate SGC v2/v3, numeric scores, universal output formats, ledger requirements, runtime/schema/acceptance changes, or mandatory Semantic Reviewer through this v1 guard.",
]

ERBE_LINES = [
    "ERBE Specification-First Acceptance Guard",
    "- Classify Goal applicability as required, proportional, not_applicable, or blocked_oracle before dominant Builder work.",
    "- Freeze machine-readable Contract/Cases, state axes, predicates, invariants, counterexamples, forbidden collapses, oracle owner, write exclusions, and claim ceiling.",
    "- Trusted RED requires contract valid, execution ok, and the expected semantic failure fingerprint; environment/fixture/import/path errors are error, not RED.",
    "- GREEN must reuse the same frozen identity as RED and be independently recomputed from durable inputs; producer terminal status is not validation evidence.",
    "- Builder cannot write frozen Contract/Cases/expected/RED evidence/claim ceiling; revisions require Contract Patch + Scope Delta + re-RED.",
    "- Current BDD readable cards are projection-only and do not become ERBE or pass/fail authority.",
]

ORACLE_LINES = [
    "Oracle Review Guard",
    "- Draft first, freeze later: the first AI-authored oracle is a proposal.",
    "- Summarize the boundary choices that are non-obvious or semantically costly.",
    "- State the recommended default and why.",
    "- Ask for human review or approval unless that final semantic choice was explicitly delegated.",
    "- Do not describe the artifact as frozen before that checkpoint is satisfied.",
]

ADEQUACY_LINES = [
    "A1 Adequacy Guard",
    "- Do not end A1 without a phase-specific prompt and preserved run1...runN evidence.",
    "- Default to at least 5 effective runs unless the human explicitly waives that floor.",
    "- Cover at least one maintained positive shape, one boundary/negative shape, and one prompt-revision rerun.",
    "- Preserve failed attempts and an oracle-comparison summary; do not keep only the final success sample.",
    "- Produce an adequacy report: what points at contract, prompt, golden/oracle, and what is still unresolved.",
    "- If new material failure modes are still appearing, A1 is not complete yet.",
    "- On new or unstable phases, give the human an adequacy review window before promoting to A2.",
]

DESIGN_LINES = [
    "Post-C0 Design Handoff Guard",
    "- Run this after C0 approval and before the dominant Builder lane starts implementation.",
    "- Save the design artifact as Dashboard/Artifacts/<SessionID>_<ShortTopic>_Design.md for a tracked session or Dashboard/Artifacts/<StageID>_<ShortTopic>_Design.md for a Stage Plan / multi-session batch.",
    "- Include C0 Authority Consumed, Plain-Language Objective, Scope and Non-Goals, Current Architecture Read, Proposed Module/Data/API/Contract Design, Implementation Slices and Ownership, Test and Gate Plan, Risks and Escalation Triggers, Builder Handoff, Validation Focus, Design Delta Policy, and Artifact Path.",
    "- Keep the Design Agent read-mostly or design-doc-only unless explicitly assigned otherwise.",
    "- Do not let the Design Agent implement code, change golden/contract/acceptance posture, or replace Semantic Reviewer.",
    "- If Builder materially diverges from the saved design, require a Design Delta in closeout with rationale and whether human, Validation, or Semantic Reviewer review was needed.",
]

GOAL_CONFORMANCE_LINES = [
    "Goal Conformance / Scope Delta Guard",
    "- Use when executing a Goal, Stage Plan, Session, or approved plan where original scope could be narrowed, substituted, or validated only against a revised design.",
    "- Run after C0 approval, before Builder implementation starts, and before closeout.",
    "- Before dominant Builder work, split the original Goal / Stage Plan / approved plan into a must-have ledger: source pointer, intended outcome, acceptance/evidence expectation, owner/lane, status, and evidence.",
    "- Create a Scope Delta entry whenever an original must-have is deleted, narrowed, replaced, reworded into a different deliverable, deferred, or validated through a different authority.",
    "- Scope Delta fields: original requirement; reason for removal/replacement; revised requirement; impact; whether human approval is required; approval status/reference; whether a deferred session is required.",
    "- Material deletion/replacement, semantic narrowing, or any delta that would let an unlanded original must-have coexist with a completion claim requires human approval.",
    "- Validation must check both the original Goal / must-have ledger and the revised design; revised-design-only validation cannot support done, validated, SP complete, or Goal complete.",
    "- Closeout must include an Original Plan Coverage Matrix with every must-have marked landed, not landed human-approved deferred, not landed blocked, or not applicable with reason.",
    "- If an original must-have remains not landed without approved deferral, not-applicable rationale, or blocker/termination status, do not write SP complete, Goal complete, or equivalent full-completion wording.",
    "- This guard does not activate SGC v2/v3, numeric scores, runtime behavior, schema behavior, acceptance posture changes, universal ledger schema, or a new deterministic runtime gate.",
]

GOAL_AGENT_LINES = [
    "Goal Agent Prompt Quality Guard",
    "- Use when drafting, reviewing, or finalizing a Task Goal Prompt / Loop Goal Prompt / subagent delegation prompt for governed SGE work.",
    "- The Goal Agent's output is a handoff contract, not implementation evidence. It must prevent semantic misunderstanding, task drift, scope narrowing, and false closure in the later execution thread.",
    "- Build a Read Manifest before the final prompt: source thread pages read, required repo files read, acceptance criteria read, prior design/closeout artifacts read, and any deliberately skipped source with reason.",
    "- Translate and explain the task in Chinese before writing the prompt: what it asks, covered G/SP/Session items, prerequisites, non-goals, authority boundaries, and likely false-closure risks.",
    "- Preserve original scope as a must-have ledger. Do not auto-shrink the task to a smaller, easier deliverable unless the prompt explicitly records Scope Delta, approval status, and completion impact.",
    "- Final prompts must include: default configuration, mandatory reading list, required outputs, must-have ledger, non-goals, forbidden claims, CG status, governance workflow, validation handoff, Semantic Reviewer triggers, closeout-language gate, KB/Dashboard review, termination conditions, and allowed/forbidden closeout wording.",
    "- Final prompts that involve a Validation Agent must require `guardrail_checklist.py --mode validation-agent` and the fixed read-mostly Validation Agent Prompt before any validation verdict.",
    "- If no external CG input was provided, record exactly `CG skipped: no CG input provided`; do not invent CG review.",
    "- Quality pressure overrides speed pressure. Orchestrator requests to stop expanding scope, land minimal artifacts, or immediately give a verdict do not waive mandatory reading, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, or closeout-language gate.",
    "- If mandatory evidence is incomplete, the only valid convergence is blocked or partial. Reply: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`",
    "- Validation of a Goal Prompt must review both the prompt and the original objective / repo acceptance baseline; prompt-only polish cannot support a quality verdict.",
]

LOOP_CONTINUATION_LINES = [
    "Loop Continuation Guard",
    "- A Loop Goal ends only when its completion rule or an explicit termination condition is reached; a Session/lane/closeout boundary is not a Loop stop condition.",
    "- After every Session closeout, record goal_terminal, next_session, next_session_ready, and human_decision_required.",
    "- If goal_terminal=false, next_session_ready=true, and human_decision_required=false, do not send a final answer; immediately enter the next Session intake/card/lane workflow in the same execution turn.",
    "- Do not ask the user to type continue merely because one bounded Session passed, a safe checkpoint was reached, or the next Session artifacts have not yet been created.",
    "- Pause only for Goal completion, explicit user stop, a genuine human-authority/destructive decision, an explicit token/context/budget threshold, network/tool interruption, or more than three consecutive recovery failures.",
    "- Ordinary gate/test failure, card or digest drift, a rebuildable baseline, or missing next-Session artifacts must be repaired or materialized by the Orchestrator when within scope; they are not human continuation decisions.",
    "- When a human decision is genuinely required, ask once with recommendation and impact. After the decision arrives, resume the Loop automatically without requiring an additional continue message.",
    "- After context compaction or task resume, reconstruct continuation state from the Loop Goal, Dashboard rows, and latest closeout/reconciliation, then continue the first unfinished ready Session.",
]

VALIDATION_AGENT_LINES = [
    "Validation Agent Quality Guard",
    "- Use whenever this agent is assigned as a Validation Agent for a Goal, Stage Plan, tracked Session, closeout package, builder handoff, or delegated validation thread.",
    "- Default posture is read-mostly. Do not fix Builder output unless the human explicitly asks the Validation Agent to repair it.",
    "- Build a Read Manifest before verdict: source thread or handoff packet, AGENTS, SGC skill, Dashboard Session/Stage Plan rows, Current State, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, related design/closeout artifacts, Agent Logs, KB truth, changed files, and gates/tests evidence.",
    "- First translate the work into plain Chinese for the human owner: what the task actually tried to do, what it claims is done, what it does not prove, and where the main risk is.",
    "- Review both the original objective and the revised/landed artifacts. Revised-design-only validation cannot support pass, done, SP complete, or Goal complete.",
    "- Look for as many useful quality issues as evidence supports: scope narrowing, overclaim, missing artifacts, weak tests, stale Dashboard rows, KB/Dashboard truth split errors, untracked follow-ons, false closure, acceptance/gate gaps, semantic-risk triggers, and technical debt that may become hard to repair later.",
    "- Findings should be evidence-grounded with file/line references or exact artifact/command references. Separate blocking findings, non-blocking findings, open questions, and required Builder repair.",
    "- Verdict must be evidence-bound: pass only when required evidence and gates are complete; pass-with-findings only when findings are non-blocking; fail/block when completion wording exceeds evidence or mandatory evidence is missing.",
    "- A final verdict must cover the actual closeout, final Dashboard/KB state, and final diff. A verdict produced before those surfaces existed, especially one that still lists closure blockers, requires an independent post-closeout reconciliation before done.",
    "- Orchestrator pressure is not authority. Requests to immediately converge, stop reading, or just give a final verdict do not waive mandatory files, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, or closeout-language gate.",
    "- If mandatory evidence is incomplete, reply: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`",
    "- Non-promises: this guard does not implement the task, replace Semantic Reviewer, promote Dashboard evidence to KB truth, or create runtime/schema/acceptance behavior.",
]

CONTEXT_EFFICIENCY_LINES = [
    "Context Efficiency / Delta Validation Guard",
    "- Use three layers: repo governance by reference, one Loop Goal with original-scope IDs and Session DAG, and one current Session Task Card with only Delta Read Set / AC pointer / outputs / maximum claim.",
    "- Do not paste AGENTS, the whole Loop history, every Session plan, or full Acceptance Criteria into each Session prompt.",
    "- Revise Goal drafts with Goal Patch by default; emit the full prompt only for the first draft and final executable artifact.",
    "- First Validation round establishes the baseline. Later rounds consume a Validation State Snapshot and inspect only changed files, affected gates, open blockers, and final-state surfaces.",
    "- Rebaseline when user instructions, Goal/governance/AC revision, original objective, claim ceiling, authority/truth placement, KB/Dashboard routing, dependencies, execution topology, threat model, semantic risk, patch consistency, or snapshot identity/inventory changes.",
    "- Snapshot identity must cover repo/worktree, baseline commit, dirty-state digest, tracked/untracked/renamed/generated inventory, critical hashes, parent snapshot, reviewer, and time; do not trust Builder changed-file claims alone.",
    "- Goal Patch needs base revision, sequence, target, replacement, reason, Scope Delta impact, and conflicts; Builder receives only the fully resolved Final Goal.",
    "- Separate roles: Validation Reviewer decides current-contract pass/fail; Adversarial Tester probes the accepted threat scope; Governance Architect proposes future rule evolution.",
    "- A new hardening idea outside the current AC/contract is a follow-on unless a human-approved Scope Delta brings it into the current task.",
    "- Default convergence: initial validation -> blocker-fix delta validation -> final-state reconciliation. Round four or later requires blocker admissibility or rebaseline reason; repeated same-root blockers trigger rebaseline, hardening session, or human scope decision.",
    "- A blocker must violate the current AC/contract, original must-have, evidence integrity, authority boundary, claim ceiling, or create an in-scope regression. Future hardening is not automatically a current blocker.",
    "- Narrow read-only delta reconciliation may use one independent Validation lane; implementation or semantic/authority changes still require the applicable governed lanes.",
    "- Working updates and Agent Logs should record deltas and references; full manifests and explanations belong in formal Validation/closeout artifacts.",
]

CONTEXT_BOOTSTRAP_LINES = [
    "Task Context Bootstrap Guard",
    "- Classify each post-Intake task as read_only, implementation, or validation; only trivial low-risk tasks may use an implicit equivalent packet.",
    "- Raw User Intent remains authority and Intake remains a projection; never replace or narrow the original intent through Intake.",
    "- Declare boundaries, Required Read Set, Conditional Read Set, Semantic Refresh, required epistemic domains, change impact, and topology.",
    "- Support deterministic and evidence-backed agent-evaluated triggers; agent judgment may expand reads but cannot suppress a deterministic trigger.",
    "- Refresh objective, authority, claim ceiling, and critical dependencies even when digests are unchanged.",
    "- Context optimization may remove repetition but must not shrink the epistemic search space required to complete the task; expand reads or report an evidence gap.",
    "- Derive topology from change impact, not artifact type alone; render stable rules as path@revision/digest with applicability and reason.",
    "- Validate non-trivial packets with context_bootstrap.py before execution; the printed checklist is not validation evidence.",
]

LANE_TASK_CARD_LINES = [
    "Lane Task Card Delegation Guard",
    "- Before delegating a non-trivial lane, create and validate a lane_task_card_v1 artifact; this printed checklist is not validation evidence.",
    "- Render the delegation prompt with lane_task_card.py render and require the receiver to run its --expected-card-sha256 command. Do not manually paste Goal, governance, acceptance criteria, or adjacent-lane background into the prompt.",
    "- Builder cards require explicit write scope; delta cards require a verified parent snapshot; source digest drift and fork_context=true fail closed.",
    "- Audit adjacent or parallel lane prompts. Stable-source long copies and cross-lane exact repeated blocks are blockers; near duplicates are advisory.",
    "- Do not replace semantic duplication checks with a fixed prompt-length or token cap.",
]

CALLOUT_LINES = [
    "Closeout Deferred-Scan Guard",
    "- Implementation Delta: 所有 Goal closeout 声明实际行为适用性；适用时写模块前后行为、仓库提交/完整固定快照、真实证据、Goal/AC 影响、未覆盖边界与独立验收状态。",
    "- 混合状态分列，快照含 tracked/untracked/add/delete/rename 清单与内容；对象变化重新绑定，多 Session 父面汇总。参阅 references/implementation-delta-template.md 与 references/implementation-delta-examples.md。",
    "- 本输出仅是提醒清单，不自动检测 Implementation Delta 遗漏；表格、提交、自检、测试与语言检查均不替代独立审查。",
    "- Create or update the Dashboard closeout artifact for non-trivial governed work.",
    "- Use Dashboard/Artifacts/<SessionID>_<ShortTopic>_Closeout.md for a tracked session or Dashboard/Artifacts/<StageID>_<ShortTopic>_Closeout.md for a Stage Plan / multi-session batch.",
    "- Include Chinese headings by default: 关键结论中文展开, 落地范围, 原始目标覆盖矩阵, 范围变更复核, Lane 启动与例外, 设计交接, 验证交接包, 验证结论, 明确非目标, 证据, 运行的门禁, 语义复核, 延后范围, KB/Dashboard 复核, and 后续候选.",
    "- Write the closeout artifact and final closeout summary in Chinese by default; translate or summarize English lane/tool evidence unless exact wording is necessary evidence.",
    "- Add '关键结论中文展开' when compressed conclusions affect human judgment.",
    "- Run closeout-language with the closeout file and treat any failure as a closeout blocker.",
    "- Confirm final Validation / Semantic evidence covers the actual closeout, final Dashboard/KB state, and final diff; pre-closeout verdicts with unresolved closure blockers cannot support done without post-closeout reconciliation.",
    "- Reference the closeout artifact from the changed Dashboard row.",
    "- Check whether any scope was intentionally narrowed.",
    "- For Goal / Stage Plan / approved-plan execution, include Original Plan Coverage Matrix and block SP complete / Goal complete wording if any original must-have remains not landed without approved deferral, not-applicable rationale, or blocker/termination status.",
    "- Check whether any concrete deferred remainder or refinement emerged.",
    "- If a concrete later candidate would be costly to rediscover, add it to Dashboard/Sessions.md now.",
    "- Include next candidate SP / Sessions with topic, why now, and why ahead of nearby alternatives.",
    "- Run the KB Contract Delta Scan when approved artifacts contain contract, semantic, trust/disposition, blocking/advisory, promotion, or non-goal claims.",
    "- State the KB review result and the Dashboard review result explicitly.",
]

CLOSEOUT_LANGUAGE_LINES = [
    "Closeout Language Guard",
    "- Use for every non-trivial Dashboard closeout artifact before final completion wording.",
    "- Run with a file: python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode closeout-language --file Dashboard/Artifacts/<...>_Closeout.md",
    "- H1/H2 headings must contain Chinese text; English identifiers may remain only when the heading also explains the section in Chinese.",
    "- English verdict/status/routing labels such as passed, done, blocked, Dashboard-only, promote-to-KB, Single-Agent Exception, Validation Verdict, Gates Run, or Next Candidates must be accompanied by Chinese explanation in the same closeout section.",
    "- The Validation Handoff Packet must include an explicitly passing Closeout language verdict; missing, failed, blocked, pending, or not-run verdicts block final completion.",
]

VALIDATION_LINES = [
    "Validation Handoff Guard",
    "- For every non-trivial task, prepare a lightweight Validation Handoff Packet before final validation.",
    "- Store the packet in the Dashboard closeout artifact under '验证交接包' by default.",
    "- Include original objective coverage when a Goal/Stage Plan/tracked Session is involved, claimed scope, Scope Delta if any, claimed semantic change, explicit non-goals, files/artifacts changed, gates/tests run, evidence produced, known risks, and KB/Dashboard impact.",
    "- Include Closeout language verdict: whether the closeout-language gate explicitly passed; missing, failed, blocked, pending, or not-run verdicts block final completion.",
    "- Treat this packet as default validation input, not as a Validation verdict; when Agent Log default applies, copy or link it from the relevant lane log.",
    "- When semantic failure or memory-layer risk is relevant, use the S1-S6 / L0-L6 diagnostic lens: classify failure, locate surface, map countermeasure, check implementation surface, and decide memory layer.",
    "- Validation should return a verdict, blocking/non-blocking issues, evidence reviewed, gates run or missing, KB/Dashboard review, suggested revisions, and whether Semantic Reviewer escalation is needed.",
    "- Do not claim final promotion or closeout if the Validation verdict is missing for a non-trivial governed batch.",
]

BDD_SYNC_LINES = [
    "BDD Sync Guard",
    "- Use when a task adds, removes, renames, or materially changes a maintained non-unit deterministic gate, shared validator, runtime/contract/matrix gate, phase acceptance gate, runtime-oracle gate, repo/facade/matrix gate, or enumerable internal case inside such a gate.",
    "- Do not trigger solely for unit / seam test edits; those remain implementation-level unless promoted into a maintained non-unit gate or shared validator.",
    "- If a new behavior is discovered, first add or update the appropriate contract / acceptance / runtime / matrix gate or shared validator, then add or update the BDD scenario that calls that authority.",
    "- If a legacy gate's internal case list changes, update tests/bdd/support/case_catalog.py and rerun python3 tests/bdd/run_bdd_validation.py --list.",
    "- If C2/C3 semantic mapping may be affected, rerun python3 tests/bdd/run_bdd_validation.py --audit-semantic-coverage --strict-semantic-coverage.",
    "- If closeout claims readable cards landed, persist them under tests/bdd/readable_cards/<gate>/ (or an equivalent tracked path); .sge/reports or /tmp output is transient and does not prove durable card sync.",
    "- If BDD text, level, migration batch, authority rule, or coverage rule changes, update tests/bdd/README.md and the relevant KB strategy sources / rendered docs.",
    "- In closeout, record either the BDD files changed and commands run, or the explicit reason no BDD file update was required.",
]

CONTRACT_DELTA_LINES = [
    "KB Contract Delta Scan Guard",
    "- Use when an approved proposal, closeout, reviewed seed, matrix, contract, or acceptance/gate artifact changes stable phase/module contract, artifact semantics, trust/disposition vocabulary, blocking/advisory rule, promotion boundary, or non-goal boundary.",
    "- Review the content claim's truth layer, not only the artifact's filesystem location.",
    "- Classify each actual delta as promote-to-KB, Dashboard-only, gate-docs later, runtime/tests later, or deferred session.",
    "- Promote-to-KB means extracting the stable reusable subset into KB JSON with source scope; it does not mean copying the whole Dashboard artifact.",
    "- If no KB update is needed, record why no stable truth changed or why the delta remains Dashboard-only evidence.",
    "- Keep the scan short: Delta claim | Trigger | Classification | Rationale | Follow-up.",
]

SEMANTIC_LINES = [
    "Semantic Reviewer Trigger Guard",
    "- Semantic Reviewer is not mandatory for every non-trivial task by default.",
    "- Start Semantic Reviewer when the human requests it, the Stage Plan requires it, or Orchestrator/Validation records a semantic-risk escalation.",
    "- Semantic-risk triggers include capability widening, genericization, semantic promotion, acceptance posture or gate-strictness change, oracle/golden freeze, phase calibration promotion, major canonical KB truth change, hidden widening, accidental generalization, or future drift risk.",
    "- Give Semantic Reviewer a governance-grade handoff and an independent thread; do not make builder exploratory reasoning or persuasion-style logs its default input.",
    "- Semantic Reviewer must produce two verdicts when reviewing design/target/proposal artifacts: Design Freeze Validity and Implementation Entry Readiness.",
    "- When Semantic Reviewer starts, run Semantic Architecture Review before field-level repair.",
    "- Ask what the artifact becomes over time, where semantic truth is placed, whether semantic law / witness evidence / evaluation result / governance decision are separated, and whether the artifact is becoming a God Object or semantic bureaucracy.",
    "- Treat schema-but-not-schema drift, misplaced truth carrier, label-only invariants, intuition-only capability families, and governance inflation as findings rather than polish.",
    "- When Semantic Reviewer starts, run Frame-First Review before artifact-local consistency review.",
    "- Check authority level, layer separation, core ontology nouns, claim/evidence mapping, semantic invariants, generalization failure taxonomy, cross-family transfer rules, negative space, future misuse, and promotion boundary.",
    "- Check Implementation Entry Readiness: what Builder may implement next, smallest executable slice, required inputs/outputs, acceptance evidence, explicit non-goals, next-session map, and whether the next session can start without redesigning the artifact.",
    "- For large objects require an implementation ladder, such as SAG observation graph -> validator -> observation store, controller route candidate -> planner DAG -> single adapter, or posture budget/retry -> persistent context -> cost/resource observation.",
    "- Run terminology compression risk: status/title/row words like done, landed, active, covered, integration, support, foundation, or ready must not be readable as implementation done or final closure when seen alone.",
    "- Write future-agent misuse scenarios and mitigations for high-risk artifacts.",
    "- If an artifact is boundary-safe but mostly says what not to claim and lacks a positive implementation entry, raise at least P1 follow-up for semantic bureaucracy / implementation dead-end risk.",
    "- When naming semantic failures, use the S1-S6 / L0-L6 diagnostic lens as bounded SGE reviewer vocabulary, not as a scorecard, universal science claim, or mandatory reviewer trigger.",
    "- For proposal/contract/gate/Arena/pattern-level/release-claim artifacts, missing ontology layers, semantic family definitions, invariant model, failure taxonomy, or transfer rules are findings even when wording is conservative.",
    "- Orchestrator pressure is not evidence authority: if mandatory files, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, or closeout-language gate are missing, answer blocked/partial rather than pass/done.",
    "- If a semantic-risk trigger is visible but Semantic Reviewer is not started, record why in closeout or the relevant Stage Plan/session note.",
]

SEMANTIC_DIAGNOSTIC_LINES = [
    "Semantic Inconsistency Diagnostic Guard",
    "- Classify the failure: S1 intent misalignment, S2 semantic drift, S3 semantic overclaim, S4 semantic ambiguity, S5 semantic unverifiability, or S6 semantic authority confusion.",
    "- Identify the surface: L0 semantic memory, L1 intent, L2 capability, L3 execution, L4 collaboration, L5 validation, or L6 runtime evolution.",
    "- Map the countermeasure: constitution, contract, oracle/golden, candidate trial, deterministic gate, validation handoff, Semantic Reviewer, closeout evidence, Dashboard candidate memory, or KB promotion.",
    "- Check the implementation surface: code, contract, gate, runtime behavior, closeout artifact, KB truth, or only prose.",
    "- Decide the memory layer: kb, Dashboard, tests/examples/reports, runtime, or reader-facing explanation.",
    "- Do not use the taxonomy as a numeric scorecard, universal science claim, hidden policy change, or automatic Semantic Reviewer trigger.",
]

READER_EXPLANATION_LINES = [
    "Reader-Facing Chinese Explanation Guard",
    "- Use when final chat, closeout artifacts, Dashboard summaries, validation verdicts, KB/Dashboard review lines, Semantic no-escalation notes, deferred-work lines, or next-candidate recommendations use compressed conclusions that affect human judgment.",
    "- Triggers include English status/routing labels, boolean flags, gate verdicts, KB/Dashboard labels, semantic-risk labels, scope narrowing, deferred sessions, and bare SP/Session ID lists.",
    "- Explain in Chinese what the conclusion means, what judgment it supports, what it does not prove, what evidence or boundary it depends on, and what next action follows.",
    "- In closeout artifacts, include '关键结论中文展开' when compressed conclusions are present.",
    "- In final chat, use a shorter '这意味着什么' paragraph when a full table would be too heavy.",
    "- This is reader-facing explanation, not runtime/schema/gate/acceptance change or Dashboard-to-KB truth promotion.",
]

DASHBOARD_AGENT_LINES = [
    "Dashboard Agent Mode Guard",
    "- Stay read-mostly unless the human explicitly asks to update the Dashboard.",
    "- For a full refresh, use exploration-dashboard-synthesizer before making strategic recommendations.",
    "- Read Dashboard Big Ideas, Stage Plans, Sessions, Risks/Decisions/Quality Metrics where relevant, plus relevant kb truth.",
    "- When diagnosing stale rows, deferred candidates, or memory-layer confusion, use S1-S6 / L0-L6 as bounded reviewer vocabulary: name failure class, surface, countermeasure, implementation surface, and memory layer.",
    "- Default next-step guidance to three candidates: quality/stability, speed/progress, and blue-sky.",
    "- List archive / cancel / rewrite / add proposals with evidence and rationale.",
    "- Do not treat Dashboard update proposals as execution commitments before human approval.",
]


def _print_block(lines: list[str]) -> None:
    for line in lines:
        print(line)


HEADING_RE = re.compile(r"^(#{1,2})\s+(.+?)\s*$")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
ENGLISH_STATUS_RE = re.compile(
    r"(?i)"
    r"\b("
    r"landed scope|explicit non-goals|validation handoff packet|validation verdict|"
    r"gates run|next candidates|single-agent exception|scope delta|"
    r"passed|pass-with-findings|pass|failed|fail|blocked|pending|done|complete|"
    r"deferred|validated|dashboard-only|promote-to-kb|no-escalation"
    r")\b"
)
CLOSEOUT_LANGUAGE_VERDICT_RE = re.compile(r"(?i)closeout language verdict[`*_\s]*[:：]")
CLOSEOUT_LANGUAGE_VERDICT_PASS_RE = re.compile(r"(?i)(通过|\bpass(?:ed)?\b)")
CLOSEOUT_LANGUAGE_VERDICT_FAIL_RE = re.compile(
    r"(?i)(未通过|不通过|失败|未运行|尚未运行|缺失|待回填|待最终回填|待独立|"
    r"\bfail(?:ed)?\b|\bblocked\b|\bpending\b|\bnot\s+run\b|\bmissing\b)"
)


def _is_ignorable_language_line(stripped: str) -> bool:
    return (
        not stripped
        or stripped.startswith("| ---")
        or stripped.startswith("<!--")
        or stripped.startswith("::")
    )


def _closeout_language_violations(path: Path) -> list[str]:
    violations: list[str] = []
    in_fence = False
    has_closeout_language_verdict = False
    has_passing_closeout_language_verdict = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or _is_ignorable_language_line(stripped):
            continue

        if CLOSEOUT_LANGUAGE_VERDICT_RE.search(stripped):
            has_closeout_language_verdict = True
            if CLOSEOUT_LANGUAGE_VERDICT_FAIL_RE.search(stripped):
                violations.append(
                    f"{path}:{lineno}: Closeout language verdict must be passing before final completion: {stripped}"
                )
            elif CLOSEOUT_LANGUAGE_VERDICT_PASS_RE.search(stripped):
                has_passing_closeout_language_verdict = True
            else:
                violations.append(
                    f"{path}:{lineno}: Closeout language verdict must explicitly say the gate passed: {stripped}"
                )

        heading_match = HEADING_RE.match(stripped)
        if heading_match and not CJK_RE.search(heading_match.group(2)):
            violations.append(
                f"{path}:{lineno}: H1/H2 heading must include Chinese explanation: {heading_match.group(2)}"
            )
            continue

        if ENGLISH_STATUS_RE.search(stripped) and not CJK_RE.search(stripped):
            violations.append(
                f"{path}:{lineno}: English verdict/status label needs Chinese explanation: {stripped}"
            )

    if not has_closeout_language_verdict:
        violations.append(
            f"{path}: Validation Handoff must include `Closeout language verdict`."
        )
    elif not has_passing_closeout_language_verdict:
        violations.append(
            f"{path}: Validation Handoff `Closeout language verdict` must be an explicit passing verdict."
        )
    return violations


def _check_closeout_language(path: Path) -> None:
    if not path.exists():
        print(f"Closeout language check failed: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    violations = _closeout_language_violations(path)
    if violations:
        print("Closeout language check failed:")
        for violation in violations:
            print(f"- {violation}")
        sys.exit(1)
    print(f"Closeout language check passed: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=(
            "intake-evaluation",
            "sgc",
            "erbe",
            "multi-agent",
            "design",
            "goal-conformance",
            "goal-agent",
            "loop-continuation",
            "validation-agent",
            "context-bootstrap",
            "context-efficiency",
            "lane-task-card",
            "oracle",
            "adequacy",
            "validation",
            "bdd-sync",
            "contract-delta",
            "semantic",
            "semantic-diagnostic",
            "reader-explanation",
            "dashboard-agent",
            "closeout",
            "closeout-language",
            "all",
        ),
        default="all",
        help="Which checklist to print.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Closeout markdown file to scan when --mode closeout-language is used.",
    )
    args = parser.parse_args()

    if args.file is not None and args.mode != "closeout-language":
        parser.error("--file only applies to --mode closeout-language")

    if args.mode == "closeout-language" and args.file is not None:
        _check_closeout_language(args.file)
        return

    if args.mode in {"intake-evaluation", "all"}:
        _print_block(INTAKE_EVALUATION_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"sgc", "all"}:
        _print_block(SGC_LINES)
    if args.mode in {"erbe", "all"}:
        _print_block(ERBE_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"multi-agent", "all"}:
        _print_block(MULTI_AGENT_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"design", "all"}:
        _print_block(DESIGN_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"goal-conformance", "all"}:
        _print_block(GOAL_CONFORMANCE_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"goal-agent", "all"}:
        _print_block(GOAL_AGENT_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"loop-continuation", "all"}:
        _print_block(LOOP_CONTINUATION_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"validation-agent", "all"}:
        _print_block(VALIDATION_AGENT_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"context-bootstrap", "all"}:
        _print_block(CONTEXT_BOOTSTRAP_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"context-efficiency", "all"}:
        _print_block(CONTEXT_EFFICIENCY_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"lane-task-card", "all"}:
        _print_block(LANE_TASK_CARD_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"oracle", "all"}:
        _print_block(ORACLE_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"adequacy", "all"}:
        _print_block(ADEQUACY_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"validation", "all"}:
        _print_block(VALIDATION_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"bdd-sync", "all"}:
        _print_block(BDD_SYNC_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"contract-delta", "all"}:
        _print_block(CONTRACT_DELTA_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"semantic", "all"}:
        _print_block(SEMANTIC_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"semantic-diagnostic", "all"}:
        _print_block(SEMANTIC_DIAGNOSTIC_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"reader-explanation", "all"}:
        _print_block(READER_EXPLANATION_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"dashboard-agent", "all"}:
        _print_block(DASHBOARD_AGENT_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"closeout", "all"}:
        _print_block(CALLOUT_LINES)
        if args.mode == "all":
            print()
    if args.mode in {"closeout-language", "all"}:
        _print_block(CLOSEOUT_LANGUAGE_LINES)


if __name__ == "__main__":
    main()
