# Checklists

## Phase Workflow Runner

Use at the start of a non-trivial phase batch so the current phase/stage contract is materialized from repo-local truth instead of recalled from memory.

Suggested commands:

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage full
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage design
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage validate
```

What the runner should give you:

- the current `Phase Delivery Pattern A` step or full sequence
- the default SGC v1 Structural Contract check for non-trivial SGE work
- the default lane plan, including that Orchestrator should stay on the control plane for non-trivial governed batches
- post-C0 Design Agent expectations and the saved design artifact path when implementation follows C0 approval
- the Goal Conformance / Scope Delta check after C0, before Builder work, and before closeout
- relevant `guardrail_checklist.py` commands
- current phase acceptance entry surface and maintained regressions when the phase is already registered
- the human checkpoints that still require explicit review or promotion
- the default Validation Handoff Packet fields for non-trivial tasks
- the default Agent Log requirement for non-trivial governed multi-agent execution, tracked Session / Stage Plan lanes, and triggered Semantic Reviewer lanes, including high-fidelity visible execution trace rather than condensed summary
- the default closeout artifact path and required Chinese headings for non-trivial governed work
- the default closeout language gate: closeout artifacts and final closeout summaries are written in Chinese, English verdict/status labels need Chinese explanation, and `closeout-language` must pass before final completion wording
- the reader-facing explanation rule: compressed conclusions that affect judgment need Chinese meaning, judgment impact, evidence/boundary, and next action
- whether a Semantic Reviewer trigger is visible and how to record escalation or no-escalation
- when Semantic Reviewer starts, the Semantic Architecture Review questions that come before frame or field repair
- when Semantic Reviewer starts, the Frame-First review surfaces that must be checked before artifact-local consistency
- when Semantic Reviewer starts, the dual verdict protocol: Design Freeze Validity plus Implementation Entry Readiness, including minimum safe slice, implementation ladder, next-session map, terminology compression risk, and future-agent misuse scenarios
- the skills and closeout duties that should not be silently skipped
- when `--format template` is used, a copyable command-template runbook ordered by the current phase/stage

Suggested user task pattern:

```text
执行当前治理阶段前，先运行
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage full
本轮显式授权 Codex 按需使用 subagents / delegation / parallel agent work；是否启用由 Multi-Agent Activation Gate 决定。
并把输出作为这轮 governed batch 的执行合同。按 Strategy_Human_AI_Development、Strategy_SGC_Structural_Contract_V1 和 sge-governed-checkpoints 工作：Orchestrator 只做 control-plane，不拥有主 builder lane；C0 批准后自动进入 governed implementation mode，默认拆出 Design、Builder、Validation、Closure lanes；Design Agent 先保存 `Dashboard/Artifacts/<SessionID>_<ShortTopic>_Design.md` / `Dashboard/Artifacts/<StageID>_<ShortTopic>_Design.md`，Builder 按设计边界实施并交付 Validation Handoff Packet；C0 后、Builder 前、Closeout 前运行 Goal Conformance / Scope Delta Gate，把原始 Goal 拆成 must-have ledger，记录 Scope Delta，并让 Validation 同时检查原始 Goal 与 revised design；non-trivial governed multi-agent execution、tracked Session / Stage Plan lanes 和 triggered Semantic Reviewer lanes 默认在 `Dashboard/Agent_Logs/` 记录 Agent Logs；每个 non-trivial 任务都按 SGC v1 检查 claim level、evidence layer、forbidden collapses、SI-1..SI-6 和 completion rule；如果 Builder 偏离设计，closeout 记录 Design Delta；如果出现 semantic-risk trigger，启动 Semantic Reviewer 或记录不启动理由；在 C0 和任何需要的 C1/C3 checkpoint 停下来等我 review；完成前跑 sgc / design / goal-conformance / validation / semantic / closeout / closeout-language guards，创建或更新 `Dashboard/Artifacts/<SessionID>_<ShortTopic>_Closeout.md` / `Dashboard/Artifacts/<StageID>_<ShortTopic>_Closeout.md`，使用中文 closeout 标题并在验证交接包中写入 `Closeout language verdict`，最后明确汇报 KB/Dashboard review 结果。
```

## SGC v1 Structural Contract Checklist

Use for every non-trivial SGE task, proportionally. This is a structural semantic-governance check, not a runtime test, numeric scorecard, or universal output template.

- Canonical truth: `kb/data/strategy/strategy_sgc_structural_contract_v1.json`; rendered reading surface: `kb/docs/strategy/Strategy_SGC_Structural_Contract_V1.md`.
- Trigger: semantic-risk implementation decisions, contract/governance edits, completion or validation claims, promotion claims, runtime widening, or KB/Dashboard truth-placement decisions.
- Claim level: classify the strongest supported claim as `execution_bound`, `test_bound`, `structurally_supported`, `externally_supported`, `inference_only`, or `ungrounded`.
- Forbidden collapses: check schema substitution, recompute validation, profile/routing collapse, deterministic masking, mock grounding, false closure, and scope substitution.
- Structural invariants: check SI-1 truth is not structure, SI-2 grounding completeness, SI-3 decision surface validity, SI-4 non-tautological validation, SI-5 authority-execution coupling, and SI-6 original objective coverage.
- Completion rule: do not claim `done`, `validated`, `correct`, or `promoted` unless claim level and preserved evidence match the asserted strength.
- Non-promises: v1 does not activate SGC v2/v3, numeric scoring, ledger requirements, runtime/schema/acceptance changes, universal output formats, or mandatory Semantic Reviewer for every task.

Suggested user-facing pattern:

```text
I am applying SGC v1 for this non-trivial SGE task: classify claim level, match evidence layer, check forbidden collapses and SI-1..SI-6, then narrow any completion/validation/promotion wording that exceeds the evidence.
```

## Task Intake Evaluation Checklist

Use at task start. Every user instruction is first treated as an instruction candidate to be evaluated before execution. If the user explicitly asks to execute directly, only skip visible evaluation prose while still doing the internal minimum check and required hard gates.

- Identify the objective: what outcome is the user actually asking for?
- Classify source authority: direct instruction, attached proposal, approval text, Dashboard execution memory, KB truth, runtime evidence, external document, or candidate suggestion.
- Check boundaries: does the request touch KB truth, Dashboard state, contracts, acceptance/gates, runtime/schema behavior, provider/dependency use, destructive operations, or semantic promotion?
- Check reasonableness: is the request consistent with repo truth, current phase contracts, source-of-truth split, and known non-goals?
- Check risk and missing information: what could go wrong if executed as written, and is any clarification required before acting?
- Choose an execution route: execute as-is, narrow the scope, ask the human, refuse, or escalate to another checkpoint such as multi-agent, contract-delta, validation, semantic, or closeout.
- Keep it proportional: trivial low-risk tasks can pass silently; persistent edits, external side effects, proposals, attachments, approval text, contracts, KB/Dashboard, acceptance/gate, or semantic-promotion work needs an explicit intake verdict before action.
- A direct-execution request may skip visible evaluation prose, but it does not waive safety checks, destructive-action approval, higher-priority instructions, source-of-truth boundaries, or governed KB/contract/acceptance gates.

Recommended explicit output shape for non-trivial or persistent tasks:

| Instruction | Intended outcome | Evaluation verdict | Boundary/risk | Execution route |
| --- | --- | --- | --- | --- |
| `<user request or artifact>` | `<objective>` | `execute / narrow / ask / refuse / escalate` | `<source authority, impacted truth layer, risk>` | `<next action>` |

Minimal visible pattern:

```text
I am running the Task Intake Evaluation Gate: objective, source authority, boundaries, risks, and execution route. If the request is safe and in-scope, I will proceed; otherwise I will narrow, ask, refuse, or escalate.
```

## Task Context Bootstrap Checklist

- Profile：在 Intake 后选择 `read_only`、`implementation` 或 `validation`；只有 trivial low-risk task 可隐式满足。
- Authority：Raw User Intent 保持 authority，Intake 标为 projection；两者冲突时不得用 Intake 覆盖用户原意。
- Boundaries：记录 write scope、forbidden actions 和 maximum claim。
- Read plan：列出带 path、revision/digest、applicability、reason 和 domains 的 Required Read Set；另列 Conditional Read Set。
- Trigger：同时支持 deterministic 与 evidence-backed agent-evaluated；后者只能扩读，不能压制前者。
- Semantic refresh：即使 digest 未变，也重新确认 objective、authority、claim ceiling 和 critical dependencies。
- Epistemic invariant：Context Optimization 不得缩小必要认知搜索空间；缺 required domain 时扩读，无法读取时报告 evidence gap。
- Topology：记录 change-impact vector，再决定 single thread 或适用 lanes；不得只根据 artifact type 路由。
- Stable references：默认只渲染 path@revision/digest、applicability 与 reason，不复制稳定规则正文。
- Machine gate：非 trivial task 在执行前运行 `context_bootstrap.py validate <packet.json>`；需要下发时使用 `render` 输出紧凑包。

## Multi-Agent Default Checklist

Use before substantial work on a tracked Session, Stage Plan, or any non-trivial governed task.

- Activation trigger: `执行 S-xxx`, `启动 S-xxx`, `execute S-xxx`, `执行 SP-xxx`, equivalent tracked work wording, or any non-trivial governed task that changes KB truth, Dashboard state, acceptance posture, fixtures/tests, runtime/schema behavior, or closeout posture defaults to governed multi-agent mode in this repo.
- Standing user authorization: for future SGE non-trivial governed tasks, AI is explicitly authorized to use subagents / delegation as needed, subject to the Multi-Agent Activation Gate.
- Delegation authorization: AI may decide to start subagents / delegation from the Multi-Agent Activation Gate even when the user has not explicitly asked for subagents; user silence about subagents is not itself a reason to stay single-agent.
- Current-turn tool compatibility: when writing or copying a user-facing execution template that expects governed multi-agent mode to be available, include `本轮显式授权 Codex 按需使用 subagents / delegation / parallel agent work；是否启用由 Multi-Agent Activation Gate 决定。` This exposes the standing authorization in the same turn without bypassing the gate or forcing lanes.
- Post-C0 activation: after C0 approval, the approved scope automatically enters governed implementation mode unless the human explicitly says single-agent / no multi-agent or the task is truly trivial.
- Minimum lanes: start Design Agent, Builder, Validation Agent, and Closure Agent lanes unless the human explicitly asks for single-agent or the task is truly trivial.
- Orchestrator posture: keep the Orchestrator on the control plane where possible instead of owning the dominant builder slice.
- Design boundary: the Design Artifact / Design Handoff is input to Builder and Validation, not implementation approval, and not a Semantic Reviewer substitute.
- Validation boundary: a `Validation Handoff Packet` is input to Validation, not a Validation Agent verdict.
- Exception handling: if a default lane is not started, record `Single-Agent Exception` in the closeout artifact with reason, risk, compensating checks, and whether independent Design or Validation is missing.
- Delta-only lane rule: a narrow read-only reconciliation with no Builder output and no KB/runtime/schema/acceptance/authority/semantic change may use only an independent Validation lane. Record the classifier, snapshot/diff evidence, omitted lanes, risk, and claim impact as `not applicable for delta-only review`; this is not a substitute for an independent verdict or final reconciliation.
- Explicit topology contract: when the Goal requires an independent user-visible execution task, record task/thread id, worktree when applicable, and the task that actually performed Builder work. Creating a task that stops before Builder is not sufficient.
- Topology exception approval: Orchestrator takeover is a Scope Delta and requires a human-approved topology exception with a durable reference. Compensating tests do not convert an unapproved takeover into full Goal conformance.
- Closeout storage: include `Lane 启动与例外` in the Dashboard closeout artifact alongside `设计交接`, `验证交接包`, and `验证结论`.

Suggested user-facing pattern:

```text
I am running the Multi-Agent Activation Gate. Because this is tracked/non-trivial governed work, I may start subagents / delegation based on the task even without a separate subagent request, and I will default to Design, Builder, Validation, and Closure lanes unless there is a recorded Single-Agent Exception.
本轮显式授权 Codex 按需使用 subagents / delegation / parallel agent work；是否启用由 Multi-Agent Activation Gate 决定。
```

## Post-C0 Design Handoff Checklist

Use after C0 has been approved and before dominant Builder implementation begins.

- Authority: state the C0 / Stage Plan / Session scope, non-goals, constraints, and exit criteria the design consumes.
- Artifact path: save the design as `Dashboard/Artifacts/<SessionID>_<ShortTopic>_Design.md` for a tracked session or `Dashboard/Artifacts/<StageID>_<ShortTopic>_Design.md` for a Stage Plan / multi-session batch.
- Required sections: C0 Authority Consumed, Plain-Language Objective, Scope and Non-Goals, Current Architecture Read, Proposed Module/Data/API/Contract Design, Implementation Slices and Ownership, Test and Gate Plan, Risks and Escalation Triggers, Builder Handoff, Validation Focus, Design Delta Policy, Artifact Path.
- Design boundary: Design Agent stays read-mostly or design-doc-only unless explicitly assigned otherwise; it must not implement code, change golden/contract/acceptance posture, or replace Semantic Reviewer.
- Builder handoff: state the smallest safe implementation slices and which files/contracts/tests each slice is expected to touch.
- Validation focus: state the specific claims Validation should verify against the saved design.
- Delta handling: if Builder materially diverges from the design, closeout must include a Design Delta with rationale and whether human, Validation, or Semantic Reviewer review was needed.

Suggested user-facing pattern:

```text
C0 is approved, so I am saving the post-C0 Design Agent artifact before dominant Builder implementation. The design will define module/API/data/contract boundaries, implementation slices, gate/test plan, risks, Builder handoff, and Validation focus.
```

## Goal Conformance / Scope Delta Checklist

Use when executing a Goal, Stage Plan, Session, or approved plan where the original scope could be narrowed, substituted, or validated only against a revised design.

- Timing: run after C0 approval, before Builder implementation starts, and before closeout. The first pass creates the ledger, the Builder-precheck catches substitution before code/doc work dominates, and the closeout pass prevents false completion wording.
- Must-have ledger: split the original user Goal / Stage Plan / approved plan into atomic must-haves before Builder work. For each item record source text or pointer, intended outcome, acceptance/evidence expectation, owner/lane, current status, and linked evidence.
- Process coverage: preserve workflow requirements as atomic must-haves too, including independent visible tasks, lane order, pre-Builder review, final review, and post-closeout reconciliation. Do not reduce the matrix to feature deliverables.
- Scope Delta trigger: create an entry whenever a must-have is removed, narrowed, replaced, reworded into a different deliverable, deferred, or validated through a different authority than the original Goal implied.
- Required Scope Delta fields: original requirement, reason for removal/replacement, revised requirement, impact, whether human approval is required, approval status/reference, and whether it must become a deferred session.
- Approval rule: Builder may propose a Scope Delta, but cannot silently treat it as accepted scope. Human approval is required for material deletion/replacement, semantic narrowing, or any delta that would let a previously required item become unlanded while closeout claims completion.
- Validation rule: Validation must check the original Goal / must-have ledger and the revised design. A validation verdict that only reviews the revised design does not support `done`, `validated`, `SP complete`, or `Goal complete`.
- Closeout rule: include an `Original Plan Coverage Matrix`. Every must-have must be classified as `landed`, `not landed human-approved deferred`, `not landed blocked`, or `not applicable with reason`.
- Completion wording rule: if any original must-have remains not landed without approved deferral, not-applicable rationale, or blocker/termination status, do not write `SP complete`, `Goal complete`, or equivalent full-completion wording. Use partial, blocked, narrowed-pending-approval, or explicit deferred-session wording instead.
- Non-promises: this gate does not activate SGC v2/v3, numeric scoring, runtime behavior, schema behavior, acceptance posture, universal ledger schema, or a new deterministic product/runtime gate. It is a governance/checklist guard for goal-scope honesty.

Must-have ledger shape:

| ID | Original must-have | Source pointer | Intended outcome | Acceptance/evidence expectation | Owner/lane | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `G1` | `<original requirement>` | `<chat / C0 / SP / Session / artifact>` | `<what must be true>` | `<how it will be checked>` | `<lane>` | `pending / landed / delta proposed / not landed human-approved deferred / not landed blocked / not applicable with reason` | `<path / command / verdict>` |

Scope Delta shape:

| Original requirement | Reason for removal/replacement | Revised requirement | Impact | Human approval required? | Approval status/reference | Deferred session required? |
| --- | --- | --- | --- | --- | --- | --- |
| `<must-have ID + text>` | `<why the original item cannot or should not land as written>` | `<what replaces it, or none>` | `<behavioral/governance/user-visible impact>` | `yes / no` | `<approved / pending / rejected + pointer>` | `yes / no + Session ID or proposal>` |

Original Plan Coverage Matrix shape:

| Must-have ID | Original requirement | Final status | Evidence | Approval/deferred reference | Completion impact |
| --- | --- | --- | --- | --- | --- |
| `G1` | `<original requirement>` | `landed / not landed human-approved deferred / not landed blocked / not applicable with reason` | `<path / command / validation verdict>` | `<approval / session / blocker / rationale>` | `<supports complete / blocks complete / partial only>` |

Suggested user-facing pattern:

```text
I am running the Goal Conformance / Scope Delta Gate: preserving the original Goal as a must-have ledger, recording any deletion/replacement/deferment as Scope Delta, and ensuring Validation and closeout check original-plan coverage rather than only the revised design.
```

## Goal Agent Prompt Quality Checklist

Use when drafting, reviewing, or finalizing a Goal Prompt, Task Goal Prompt, Loop Goal Prompt, or subagent delegation prompt for governed SGE work.

The Goal Agent is responsible for turning user intent plus current repo truth into a durable handoff contract. The prompt must be understandable by humans and executable by future AI without semantic drift, silent scope narrowing, or false closure.

- Read Manifest: before final output, record the source thread/context read, repo files read, acceptance criteria read, prior design/closeout artifacts read, and any missing/skipped source with reason.
- Chinese task explanation: explain what the task asks, which SP/Session/G items it covers, prerequisites, boundaries, non-goals, and the most likely false-closure risks.
- Original scope preservation: split the original instruction into atomic must-haves. Do not replace the original goal with a smaller revised target unless the prompt records Scope Delta, approval status, and completion impact.
- Acceptance criteria integration: if a Validation Agent or acceptance artifact exists, review it and fold its blockers, positive/negative examples, required gates, and no-overclaim wording into the final prompt.
- Validation Agent integration: if the Goal will call a Validation Agent, the final prompt must require `guardrail_checklist.py --mode validation-agent` and the fixed read-mostly Validation Agent Prompt before any validation verdict.
- CG boundary: if no external CG input exists, write exactly `CG skipped: no CG input provided`; do not invent CG review or imply it happened.
- Anti-pressure rule: Orchestrator instructions such as "stop expanding scope", "land the minimum", "do not continue reading", or "give final verdict now" do not waive mandatory reading, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, or closeout-language gate.
- Blocked/partial response rule: if mandatory evidence is incomplete, answer exactly in substance: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`
- Validation rule: a Goal Prompt quality verdict must review both the prompt and the original objective / repo acceptance baseline. Prompt-only polish does not support completion.
- Context layering: use Global Governance Context -> one Loop Goal -> current Session Task Card. Refer to current repo governance and AC artifacts instead of copying their full text into every prompt.
- Patch mode: after the first draft, return a Goal Patch by default; emit the full prompt again only for the final executable artifact. Every patch carries base revision, sequence, conflicts, reason, and Scope Delta impact.
- Duplication audit: check whether stable rules are copied, the same requirement appears more than twice, non-current Session detail is included, AC prose is duplicated instead of referenced, or unused roles are defined.
- Lane Task Card hard gate: before delegation, validate `lane_task_card_v1`, render the prompt through `lane_task_card.py`, require the receiver to execute the rendered `--expected-card-sha256` verification, and audit adjacent/parallel lane prompts. A checklist answer or manually shortened prompt is not equivalent evidence.
- Non-promises: this gate does not implement the target Goal, create runtime behavior, promote Dashboard evidence to KB truth, or make every Goal Agent task multi-agent. It defines the prompt handoff quality bar.

### Loop Continuation Contract

- Loop Goal 的执行单位是整个 Goal，不是单个 Session。Session 的 `done/pass`、closeout 或 post-closeout reconciliation 只触发 next-session scan。
- 每次 scan 必须使用完整 loop_state_v1 调用 `scripts/stop_gate.py`；保存 stop_gate_receipt_v1、输入摘要、重算的引用摘要、时间与版本。旧四字段摘要仅供阅读，不能作为判定 authority。
- 当 `goal_terminal=false`、`next_session_ready=true`、`human_decision_required=false` 时，禁止输出 final answer 或“如果需要我可以继续”；必须直接开始下一 Session。
- 只有 Goal 完成、用户明确暂停、真正的人类 authority/destructive decision、Goal 明示资源阈值或相同网络/工具 fingerprint 连续恢复失败达到默认 3 次可以终止当前 Loop 回合；瞬时中断先恢复。
- 普通测试失败、lane card/digest drift、需要创建下一 Session artifact 或可重建 baseline 都由 Orchestrator 自行处理，不得转化为“请回复继续”。
- 人类完成必要决策后，Orchestrator 自动恢复，不再额外索取“继续”。Context compaction 后从 Goal、Dashboard 和最新 closeout 恢复 continuation state。

建议在 Loop Goal 中使用：

```text
Continuous execution contract：本 Goal 默认连续执行整个 Session DAG。任何单个 Session、lane、closeout 或 post-closeout pass 都不是停止条件。Milestone、Session closeout、恢复和 final 前运行核心 Stop Gate，保存最新 receipt。CONTINUE 后直接执行 next_action；invalid 状态自行重建。只有 GOAL_COMPLETE、用户显式暂停、真实人类权限、Goal 明示资源阈值或相同网络/工具 fingerprint 连续失败达到默认 3 次允许暂停。人类决策返回后自动续跑，不再要求“继续”。
```

### 三种消息模板

- `PROGRESS_ONLY`：已完成〈当前工作〉；Stop Gate 为 CONTINUE，继续〈next_action〉。随后执行下一步，不结束回合。
- `DECISION_REQUEST`：需要你决定〈真实权限事项〉；推荐〈选项〉，影响〈范围〉；未决定时〈阻断〉。只在 PAUSE_ALLOWED 使用；有效授权仍覆盖时不得重问。
- `FINAL_CLOSEOUT`：仅在最新 GOAL_COMPLETE receipt 允许时使用最终六问：完成了什么？证据是什么？如何验证？还有什么限制？KB/Dashboard 如何更新？后续是什么？附 receipt 与独立验收源文件链接。中间里程碑不用这套最终模板。

receipt 只证明当前输入与证据绑定；state 或引用文件变化后须重跑。无真实宿主 pre-final hook 时不得声称自动强制阻止模型 final。

Required handoff layers:

1. Global Governance Context：只引用当前 `AGENTS.md`、checkpoint skill 和稳定 KB strategy，不复制正文。
2. Loop Goal：一次保存 mission、original requirement IDs、Session DAG、approval checkpoints、Loop claim ceiling 和 completion rule。
3. Session Task Card：只保存当前 objective、Loop requirement IDs、Delta Read Set、AC pointer、required outputs、maximum claim、当前高风险 forbidden claims 和 termination rule。
4. Final resolved Goal：Builder 前将 base + Goal Patches 确定性解析为完整 artifact，列出 applied patch IDs。Patch-only handoff 无效。
5. Lane delegation：从 Final Goal 派生 machine-valid Task Card；prompt 只引用 card/digest，不重新注入 Final Goal 或 AC 正文。

Compact reusable Goal Agent instruction:

```text
你是 SGE Goal Agent。读取当前 repo governance，但不要复制它。先确认 original objective、Loop requirement IDs、当前 Session、AC pointer 和 claim ceiling。首次输出完整 draft；后续 review 只输出 Goal Patch；最终下发前输出一份 resolved Final Goal。保留 must-have ledger、Scope Delta、Validation Handoff、Semantic triggers、KB/Dashboard review、closeout-language 和 blocked/partial 规则，但通过引用与 ID 复用稳定内容。运行 context-efficiency duplication audit；证据不足时不得 pass/done。
```

详细 Goal Patch、Snapshot 和 Delta Validation 格式见 `references/context-efficient-goal-validation.md`。

Suggested user-facing pattern:

```text
I am running the Goal Agent Prompt Quality Guard: turning the request and repo truth into a durable Goal Prompt handoff contract, with Read Manifest, must-have ledger, validation focus, and anti-pressure completion rules.
```

## Validation Agent Prompt Quality Checklist

Use whenever the current agent is assigned as a Validation Agent for a Goal, Stage Plan, tracked Session, closeout package, builder handoff, or delegated validation thread.

The Validation Agent's responsibility is not to help Builder close faster. Its job is to identify as many evidence-grounded execution problems as possible, translate the work for the human owner, and give Orchestrator high-quality information that improves task execution quality.

- Read-mostly posture: do not edit Builder output unless the human explicitly asks the Validation Agent to repair it.
- Read Manifest: before verdict, record source thread or handoff packet, AGENTS, this skill, Dashboard Session / Stage Plan rows, Current State, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, related design / closeout artifacts, Agent Logs, KB truth, changed files, and gates/tests evidence.
- Baseline and delta: the first round reads the full mandatory baseline. Later rounds read the prior Validation State Snapshot plus deterministic tracked/untracked/renamed/generated inventory, changed files, affected gates, open blockers, and final-state surfaces.
- Rebaseline: reread the full baseline when user instructions, Goal/governance/AC revision, original objective, claim ceiling, authority/truth placement, KB/Dashboard routing, dependencies, topology, threat model, semantic risk, patch consistency, snapshot identity, or final diff scope changes.
- Plain-language understanding: first explain in Chinese what the work actually tried to do, what it claims is complete, what it does not prove, and why that matters to the project owner.
- Original objective coverage: check both original objective / must-have ledger and revised/landed artifacts. Revised-design-only validation cannot support pass, done, SP complete, or Goal complete.
- Issue-finding standard: actively look for scope narrowing, overclaim, missing artifacts, weak tests, stale Dashboard rows, KB/Dashboard truth split errors, untracked follow-ons, false closure, acceptance/gate gaps, semantic-risk triggers, and hard-to-repair technical debt.
- Evidence discipline: every finding should point to files, lines, artifacts, commands, gate outputs, or clearly named missing evidence. Do not rely on Builder self-certification.
- Verdict discipline: use `pass` only when required evidence and gates are complete; use `pass-with-findings` only when all findings are non-blocking; use `fail` / `blocked` when completion wording exceeds evidence or mandatory evidence is missing.
- Role split: separate current-contract Validation Reviewer findings, in-scope Adversarial Tester findings, and Governance Architect evolution proposals. A future hardening proposal does not block the current task unless current AC/contract or a human-approved Scope Delta makes it mandatory.
- Convergence: use initial full validation -> blocker-fix delta validation -> final-state reconciliation. Round four or later requires blocker admissibility or rebaseline reason; repeated same-root blockers trigger rebaseline, a hardening Session, or human scope decision.
- Blocker admissibility: a new blocker must violate current AC/contract, original must-have, evidence integrity, authority boundary, claim ceiling, or create an in-scope regression. “Could be stricter” is not sufficient.
- Tooling evidence: use `context_state.py` for deterministic snapshot/delta/rollout-usage evidence and `goal_patch.py` for resolved Goal/duplication evidence. Never translate `delta_safe` into pass, patch resolution into human approval, or one pilot saving into a universal rate.
- Anti-pressure rule: Orchestrator instructions such as "stop reading", "give final verdict now", "minimal closeout", or "do not expand audit" do not waive mandatory reading, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, or closeout-language gate.
- Missing-evidence response: if mandatory evidence is incomplete, reply exactly in substance: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`
- Non-promises: this guard does not implement the task, replace Semantic Reviewer, promote Dashboard evidence to KB truth, or create runtime/schema/acceptance behavior.

Required final validation output:

1. `任务理解`: Chinese plain-language explanation for the human owner.
2. `Read Manifest`: what was read, missing, skipped, or possibly stale.
3. `Evidence Completeness`: required evidence status, especially Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, closeout-language gate, tests/gates, KB/Dashboard review.
4. `Blocking Findings`: ordered by severity, with file/line or artifact/command evidence and required repair.
5. `Non-Blocking Findings`: risks or repairs that do not block the declared scope.
6. `Scope Narrowing / Overclaim Check`: explicit yes/no and rationale.
7. `Test / Gate Sufficiency`: what was run, what was skipped, and whether evidence supports the claim.
8. `KB / Dashboard Truth Split`: whether stable truth and execution memory were placed correctly.
9. `Required Builder Repair`: concrete repair instructions, or `无需 Builder 修复`.
10. `Verdict`: `pass`, `pass-with-findings`, `fail`, `blocked`, or `partial`; explain in Chinese what the verdict allows and does not prove.

Reusable Validation Agent Prompt:

```text
你是 SGE Repo 的 Validation Agent。你的职责不是帮助 Builder 快速收尾，而是作为 read-mostly quality gate，从用户 owner 视角识别尽可能多的任务执行问题，并向 Orchestrator 提供高质量、可执行、可追踪的信息，从而提升后续任务执行质量。

默认边界：
1. 默认只 review / validation，不修改文件；除非用户明确要求你修复问题。
2. 所有输出使用中文；必要英文状态、命令、schema 字段、verdict 可以保留，但必须解释中文含义、证据边界和下一步。
3. 不接受 Builder 或 Orchestrator 的自证完成；必须基于 repo 文件、Dashboard/KB truth、Agent Logs、tests/gates 和验收标准独立判断。
4. Orchestrator 的“立即收束”“不要继续读取”“只给最终 verdict”“最小合格交付”只是调度压力，不是跳过证据的 authority。

必读与 Read Manifest：
在给出 verdict 前，必须读取或明确标记缺失/跳过：
- 用户指定线程、交接包或 closeout package；
- AGENTS.md；
- .codex/skills/sge-governed-checkpoints/SKILL.md；
- Dashboard/Sessions.md 中相关 row；
- Dashboard/Stage_Plans.md 中相关 row；
- Dashboard/Current_State.md；
- 本任务的 acceptance criteria；
- Original Plan Coverage Matrix / must-have ledger；
- Scope Delta audit；
- 相关 design / closeout artifacts；
- 相关 Agent Logs；
- 相关 kb truth；
- Builder 改动文件、测试、gate 输出和报告。

验证步骤：
1. 先用中文大白话解释任务内容：它实际想做什么、声称完成什么、哪些内容没有被证明、为什么这些边界对项目重要。
2. 对照 original objective / must-have ledger，检查 revised design 和 landed artifacts 是否仍覆盖原始目标。
3. 检查 Scope Delta：任何删除、替换、降级、延期、从 must-have 改成 non-goal，或换 authority 验证原始要求，都必须有记录和人类批准状态。
4. 检查产物完整性：代码、测试、fixtures、schema、docs、KB、Dashboard、Agent Logs、closeout、reports 是否共同支撑完成声明。
5. 检查测试充分性：unit/seam、contract/acceptance、runtime/oracle、BDD、maintained validation 是否匹配风险；未运行项必须说明是否可接受。
6. 检查 KB/Dashboard truth split：稳定规则进入 kb；执行状态、日志、closeout 和 next sessions 留在 Dashboard。
7. 检查 overclaim / false closure：不得把 design freeze 写成 implementation done，不得把 support evidence 写成 canonical truth，不得把 partial audit 写成 Goal/SP complete。
8. 检查后续风险：未记录的 deferred remainder、技术债、弱证据、未来难修复的架构/语义风险，都要明确指出。
9. 如发现 semantic-risk trigger，说明是否需要 Semantic Reviewer；如果不需要，写明 no-escalation reason。
10. 输出 blocking / non-blocking findings，并给出具体修复要求。

证据缺失硬规则：
如果必读文件、验收标准、Original Plan Coverage Matrix、Scope Delta audit、Validation Handoff、closeout-language gate 或其他 mandatory evidence 尚未完成，不得输出 pass/done。必须回复：
`当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`

最终输出结构：
1. 任务理解
2. Read Manifest / Evidence Completeness
3. Blocking findings
4. Non-blocking findings
5. Scope narrowing / overclaim 检查
6. 测试 / gate 充分性
7. KB / Dashboard truth split 检查
8. Required Builder repair
9. Verdict：pass / pass-with-findings / fail / blocked / partial，并解释该 verdict 支持什么、不支持什么
```

Suggested user-facing pattern:

```text
I am applying the fixed Validation Agent Prompt: building the Read Manifest, explaining the task in Chinese, checking original objective coverage and landed evidence, then giving an evidence-bound verdict.
```

## Validation Handoff Checklist

Use before final validation of every non-trivial task. Agent Logs may be default for the task, but the handoff packet remains the concise validation input rather than a verdict.

- Storage: write the packet into the current Dashboard closeout artifact under `## 验证交接包`; use `Dashboard/Artifacts/<SessionID>_<ShortTopic>_Closeout.md` for a tracked session or `Dashboard/Artifacts/<StageID>_<ShortTopic>_Closeout.md` for a Stage Plan / multi-session batch. When Agent Log default applies, copy or link the packet from the relevant `Dashboard/Agent_Logs/` lane log.
- Claimed scope: what actually landed, and whether the scope narrowed.
- Claimed semantic change: whether capability claims, contract meaning, acceptance posture, semantic boundary, or promotion claims changed.
- Explicit non-goals: adjacent capabilities, genericization, provider/dependency changes, runtime widening, or truth promotion that were intentionally excluded.
- Files/artifacts changed: code, tests, fixtures, KB, Dashboard, reports, generated artifacts.
- Gates/tests run: deterministic commands, unit/contract/regression checks, diff checks, and any skipped checks with reasons.
- Evidence produced: reports, schema/lineage output, semantic diff, boundary audit, oracle comparison, or equivalent session record.
- Known risks: weak evidence, technical debt, flake risk, false positive/negative risk, semantic ambiguity, runtime hotspot, or future drift.
- KB/Dashboard impact: whether `kb/`, Dashboard rows, Decisions, Stage Plans, Risks, Exceptions, Quality Metrics, or Agent Logs changed.
- Closeout language verdict: whether `guardrail_checklist.py --mode closeout-language --file <closeout.md>` explicitly passed. Missing, failed, blocked, pending, or not-run verdicts block final completion wording.
- Verdict timing integrity: confirm the final Validation / Semantic evidence read the actual closeout, final Dashboard/KB state, and final diff. A pre-closeout verdict that still lists closure blockers cannot support `done` without an independent post-closeout reconciliation.
- Validation provenance: every non-trivial governed final completion state requires an explicitly linked durable Validation Review or post-closeout reconciliation artifact, even if the closeout omits an `Independent Validation passed` claim. Require one non-conflicting passing verdict, one reviewer/source, and a positive Read Manifest over the actual closeout, final Dashboard/KB state, and final diff. Omitted, duplicate, or conflicting records, Validation Handoff, Semantic Review, green tests, and Orchestrator self-check are not equivalent evidence.
- Multi-session audit completeness: require an Evidence Completeness Matrix for every child Session, including technical must-haves, process must-haves, visible-task topology, reviewer timing, closeout, parent surfaces, and Scope Delta.
- Semantic inconsistency diagnostic when relevant: classify S1-S6, locate L0-L6, map the countermeasure, check whether the repair lives in code / contract / gate / runtime / closeout / KB / prose, and decide the memory layer.

Suggested user-facing pattern:

```text
Before final validation I am preparing the Validation Handoff Packet and will store it in the Dashboard closeout artifact: claimed scope, semantic change, explicit non-goals, changed artifacts, gates run, evidence, known risks, KB/Dashboard impact, and Closeout language verdict.
```

## BDD Sync Checklist

Use when a task adds, removes, renames, or materially changes maintained behavior validation surfaces. BDD is the human-readable behavior layer over maintained deterministic gates; it is not a second pass/fail authority.

- Trigger scan when the task changes a maintained non-unit deterministic gate, shared validator, runtime/contract/matrix gate, phase acceptance gate, runtime-oracle gate, repo/facade/matrix gate, or an enumerable internal case inside such a gate.
- Do not trigger solely for unit / seam test edits. Unit and seam tests remain implementation-level unless the behavior is promoted into a maintained non-unit gate or shared validator.
- If a new behavior is discovered, first add or update the appropriate contract / acceptance / runtime / matrix gate or shared validator, then add or update the BDD scenario that calls that authority.
- If a legacy gate's internal case list changes, update `tests/bdd/support/case_catalog.py` and rerun `python3 tests/bdd/run_bdd_validation.py --list`.
- If the C2/C3 semantic mapping may be affected, rerun `python3 tests/bdd/run_bdd_validation.py --audit-semantic-coverage --strict-semantic-coverage`.
- If closeout claims reader-facing cards landed, persist them under `tests/bdd/readable_cards/<gate>/` or an equivalent tracked path. Output written only to `.sge/reports`, `/tmp`, or another transient report directory proves generation but does not prove durable card sync.
- If BDD text, level, migration batch, authority rule, or coverage rule changes, update `tests/bdd/README.md` and the relevant KB strategy sources / rendered docs.
- In the closeout, record either the BDD files changed and commands run, or the explicit reason no BDD file update was required.

Recommended closeout table:

| Question | Answer | Evidence | Action |
| --- | --- | --- | --- |
| Did this task add or change a maintained non-unit gate? | `yes / no` | `<files or commands>` | `<BDD update or no-op reason>` |
| Did this task add, remove, or rename enumerable legacy-gate cases? | `yes / no` | `<case source>` | `<case_catalog update or no-op reason>` |
| Did C2/C3 semantic coverage need refresh? | `yes / no` | `<audit command>` | `<result>` |

Suggested user-facing pattern:

```text
I am running the BDD Sync Guard: checking whether maintained non-unit gate or case changes require BDD gate-level, case-level, or semantic scenario updates.
```

## Contract Delta Scan Checklist

Use before final closeout when an approved proposal, closeout, reviewed seed, accepted baseline, matrix, contract, or acceptance/gate artifact may contain stable truth that future agents should not need to rediscover from Dashboard prose.

- Trigger scan when the artifact contains or changes stable contract, semantic invariant, artifact semantics, trust/confidence/disposition vocabulary, support/diagnostic disposition, blocking/advisory rule, gate/acceptance semantics, promotion boundary, non-goal boundary, reusable terminology, closure minimum, or future-agent policy.
- Judge the content claim's truth layer, not the artifact's location. A Dashboard artifact is still execution memory; a stable reusable rule inside it may still require KB promotion.
- Do not default to promotion. Classify each actual delta as `promote-to-KB`, `Dashboard-only`, `gate-docs later`, `runtime/tests later`, or `deferred session`.
- `promote-to-KB` means extracting the stable reusable subset into KB JSON with source scope and rendered Markdown. It does not mean copying the whole Dashboard artifact into KB.
- `Dashboard-only` means the item is task evidence, validation result, rationale, current sequencing, or historical explanation that does not define reusable project truth.
- `gate-docs later` means the item should eventually update workflow/checklist/operator docs but does not yet change canonical strategy.
- `runtime/tests later` means the item needs code, schema, validator, runner, fixture, or regression work before it becomes maintained behavior.
- `deferred session` means the work is concrete enough that losing it would create drift or rediscovery cost, so it should be added to `Dashboard/Sessions.md`.
- If no KB update lands, record why no stable truth changed or why the claim remains Dashboard-only evidence.
- If semantic promotion, acceptance posture, gate strictness, or promotion boundary changed, start Semantic Reviewer or record a no-escalation reason.

Recommended closeout table:

| Delta claim | Trigger | Classification | Rationale | Follow-up |
| --- | --- | --- | --- | --- |
| `<claim>` | `<artifact/path + stable wording>` | `promote-to-KB / Dashboard-only / gate-docs later / runtime/tests later / deferred session` | `<why this layer is right>` | `<KB JSON path, Dashboard row, later session, or none>` |

No-trigger line:

```text
KB Contract Delta Scan: no trigger; Dashboard-only execution memory.
```

Suggested user-facing pattern:

```text
Before closeout I am running the Contract Delta Scan: I will classify any stable contract or promotion delta and route it to KB JSON, Dashboard memory, gate docs, runtime/tests, or a deferred session.
```

## Semantic Reviewer Trigger Checklist

Use when a task may need independent semantic governance. Semantic Reviewer is not required for every non-trivial task, but visible triggers need escalation or an explicit no-escalation note.

- Did the task widen a capability claim, pattern family, generic router, or accepted repo/surface boundary?
- Did it involve genericization, semantic promotion, or promotion from candidate/trial/reviewed seed into maintained capability or canonical truth?
- Did it change acceptance posture, gate strictness, oracle/golden semantics, phase calibration status, or major canonical KB truth?
- Did Validation find a mismatch between passing tests and semantic correctness?
- Is there hidden widening, accidental generalization, truth-layer contamination, calibration illusion, runtime-driven contract mutation, or future drift risk?
- If yes, start Semantic Reviewer or record why not in closeout / Stage Plan / session notes.
- If Semantic Reviewer starts, give it evidence and explicit claims, not builder exploratory reasoning or persuasion-style logs.
- When naming semantic failures, use S1-S6 / L0-L6 as bounded SGE reviewer vocabulary; do not treat it as a numeric scorecard, universal science claim, or automatic trigger by itself.

Suggested user-facing pattern:

```text
Before promotion I am scanning for Semantic Reviewer triggers. If this task involves semantic widening, genericization, promotion, acceptance-posture changes, or future drift risk, I will start an independent Semantic Reviewer lane or record why it is not needed.
```

## Semantic Reviewer Frame-First Checklist

Use after Semantic Reviewer is triggered and before artifact-local wording, row consistency, or evidence packaging review.

- Authority level: is the artifact proposal, calibration evidence, reviewed seed, maintained gate, Dashboard execution memory, or canonical KB truth?
- Layer separation: does it mix repo/source/language structure, phase/runtime maturity, semantic capability family, acceptance gates, release claims, or operational readiness as if they were one dimension?
- Core ontology: are nouns such as family, profile, matrix, support, eligible, generalized, claim, route, and disposition formal enough for future agents to reuse without intuition?
- Claim/evidence mapping: does every support or generalization claim point to the right evidence layer, and is diagnostic/profile evidence kept below maintained capability authority?
- Semantic invariants: which role, topology/guard, lineage, rejection honesty, semantic closure, and no-partial-capability invariants must be preserved?
- Failure taxonomy: are overgeneralization, topology collapse, semantic leakage, lineage drift, role collapse, rejection dishonesty, and cross-family contamination represented when the artifact is about generalization?
- Transfer rules: what may transfer within a family, what needs a reviewed subtype/profile, and what cannot cross family boundaries without a fresh C0/A1/A2 path?
- Negative space: which unsupported, deferred, ineligible, or intentionally unmaintained surfaces must remain explicit?
- Future misuse: how could a later builder use this artifact to widen scope or promote candidate evidence silently?
- Promotion boundary: what exact condition would be needed before this artifact can become maintained capability or canonical truth?
- If proposal/contract/gate/Arena/pattern-level/release-claim artifacts lack layer split, semantic family ontology, invariant model, failure taxonomy, or transfer rules, record that as a finding rather than optional polish.

Suggested user-facing pattern:

```text
Semantic Reviewer is running the Frame-First checklist before local consistency review: authority, layer split, ontology nouns, claim/evidence mapping, invariants, failure taxonomy, transfer rules, negative space, future misuse, and promotion boundary.
```

## Semantic Reviewer Protocol v2 / Implementation Entry Readiness Checklist

Use whenever Semantic Reviewer is reviewing a design-freeze, target-only contract, proposal, acceptance posture, release/generalization claim, runtime design, or other artifact that future agents may implement from.

Semantic Reviewer has two roles:

- Boundary Reviewer: protects no-overclaim, authority split, truth placement, scope delta, negative space, and forbidden collapse.
- Evolution Reviewer: checks whether the artifact guides safe implementation rather than leaving the next agent with a large design, many prohibitions, and no minimum executable entry.

Required verdicts:

| Verdict | Allowed values | Meaning |
| --- | --- | --- |
| Design Freeze Validity | `PASS / PASS WITH FINDINGS / FAIL` | Whether current design/target scope is semantically bounded and does not overclaim completion or mutate authority. |
| Implementation Entry Readiness | `PASS / WEAK / FAIL / NOT APPLICABLE` | Whether Builder can safely start from this artifact without redesigning it or rushing into a broad object. |
| Overall Verdict | `PASS / PASS WITH P1 FOLLOW-UP / BLOCKED` | Combined judgment. Gate A pass does not imply Gate B pass. |

Review questions:

1. What exactly may Builder implement next, and what may it not implement next?
2. What is the smallest executable slice that would create a maintained or reviewable closed loop?
3. What input artifacts, KB truth, Dashboard artifacts, schemas, examples, or acceptance criteria does Builder need?
4. What output artifacts, schemas, validators, reports, tests, or Dashboard/KB updates should Builder produce?
5. What acceptance evidence is required for that next slice?
6. What remains explicitly out of scope even after the next slice lands?
7. Is there a next-session map with gap, current design, next implementation session, minimum slice, evidence, and must-not-claim?
8. Can the next session start without reinterpreting or redesigning the entire artifact?

Minimum slice examples:

| Large object | Safer first slice |
| --- | --- |
| Evidence graph | bounded observation graph v1: node/edge/authority-ref/claim-ceiling schema, validator, and negative fixtures |
| Controller | router dry-run v1: route candidate schema, route validator, and no phase execution |
| Planner | DAG candidate validator: nodes/edges/dependencies validation and read-model explanation |
| Executor | single maintained adapter boundary before any broad executor |
| Posture | budget/retry guard minimum and persistent context refs before daemon/console/production readiness |

Implementation ladder requirement:

- Evidence-graph ladder: observation graph schema -> node/edge/authority-ref validator -> append-only observation store -> structural diff observation -> review advisory model -> proof graph read-model.
- Controller ladder: route candidate schema -> route validator -> planner DAG candidate schema -> planner DAG validator -> dry-run read model -> single executor adapter boundary -> first vertical execution slice -> feedback loop slice.
- Execution posture ladder: budget/retry minimum policy -> persistent context minimum refs -> cost/resource observation -> parallel eligibility validator -> operator read surface -> production readiness evidence.

Terminology compression test:

- Simulate a future agent seeing only one Dashboard row, KB title, closeout headline, or status field.
- High-risk words include `done`, `landed`, `active`, `covered`, `complete`, `closed`, `integration`, `support`, `foundation`, and `ready`.
- Prefer `covered-in-design-freeze`, `design-freeze-done`, `target-contract-active`, `mapped-and-bounded`, `support-evidence-only`, and `design-freeze no-overclaim audit`.
- If a risky word appears in a status row/title/headline and can be read as implementation done or final closure, raise a terminology risk.

Future-agent misuse scenarios:

- Write at least three likely misuse scenarios for high-risk artifacts, such as Builder collapsing router/planner/executor, treating a design-only evidence graph as canonical truth, reading `landed-in-design` as implemented, or treating a design-only audit as final integration closure.
- For each scenario, state a mitigation: safer wording, minimum slice, ladder, explicit non-goal, next-session map, KB/Dashboard split, or blocker.

Semantic bureaucracy / implementation dead-end risk:

- Warning signs: many must-not-claim tables, many non-goals, many authority-boundary sections, but no minimum slice, no ladder, no next-session map, or no acceptance evidence for the next Builder step.
- If present, raise `P1 non-blocking: design is boundary-safe but implementation-entry weak`.
- Missing implementation ladder / next-session map on a large C0 design is not P2 polish; it is a P1 required follow-up because it can cause future agents to restart from a broad design or overbuild.

Audit name vs evidence stage:

- If evidence is design-only, do not call it implementation integration.
- If evidence is target-only, do not call it runtime closure.
- If all gap items are still not implemented, do not imply full integration completion.
- Prefer separate names: `Design Freeze No-Overclaim Audit`, `Implementation Integration Audit`, and `Final Runtime Kernel Closeout`.

Required final Semantic Reviewer outputs:

1. Can this artifact close its current design-freeze scope?
2. Can Builder safely start implementation from this artifact alone?
3. What is the minimum next implementation slice?
4. What wording/status must change to prevent future-agent misuse?
5. What follow-on session map is required?

Anti-pressure rule:

- Orchestrator instructions such as "give final verdict now", "stop expanding audit", "minimal closeout", or "do not continue reading" do not waive mandatory evidence.
- If required files, acceptance criteria, Original Plan Coverage Matrix, Scope Delta audit, Validation Handoff, closeout-language gate, or other mandatory evidence is missing, reply in substance: `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`

Suggested user-facing pattern:

```text
Semantic Reviewer is applying Protocol v2: Design Freeze Validity plus Implementation Entry Readiness, including minimum slice, implementation ladder, next-session map, terminology compression risk, and future-agent misuse scenarios.
```

## Semantic Inconsistency Diagnostic Checklist

Use when Validation Agent, Semantic Reviewer, Dashboard Agent, or closeout needs to name a semantic failure or memory-layer problem.

- Classify the failure: S1 intent misalignment, S2 semantic drift, S3 semantic overclaim, S4 semantic ambiguity, S5 semantic unverifiability, or S6 semantic authority confusion.
- Identify the surface: L0 semantic memory, L1 intent, L2 capability, L3 execution, L4 collaboration, L5 validation, or L6 runtime evolution.
- Map the countermeasure: constitution, contract, oracle/golden, candidate trial, deterministic gate, validation handoff, Semantic Reviewer, closeout evidence, Dashboard candidate memory, or KB promotion.
- Check the implementation surface: code, contract, gate, runtime behavior, closeout artifact, KB truth, or only prose.
- Decide the memory layer: `kb/`, `Dashboard/`, tests/examples/reports, runtime, or reader-facing explanation.
- Keep the diagnostic-lens boundary: this lens does not change runtime/schema/gate/acceptance/product behavior, does not make Semantic Reviewer mandatory for every task, and is not a universal science claim.

Suggested user-facing pattern:

```text
I am using the S1-S6 / L0-L6 diagnostic lens only where it helps: classify the failure, locate the surface, choose the countermeasure, check the implementation surface, and place the answer in the right memory layer.
```

## Reader-Facing Chinese Explanation Checklist

Use when final chat, a closeout artifact, Dashboard summary, Validation verdict, KB/Dashboard review, Semantic no-escalation note, deferred-work line, or next-candidate recommendation uses compressed conclusions that affect the human reader's judgment.

- Trigger terms include English status or routing labels such as `passed`, `done`, `blocked`, `candidate-only`, `Dashboard-only`, `no KB update`, `no-escalation`, `scope narrowed`, `deferred`, `generalized=true`, `promotion_allowed=true`, gate verdicts, and bare SP/Session ID lists.
- Explain the conclusion in Chinese: what it means, what judgment it supports, what it does not prove, what evidence or boundary it depends on, and what next action follows.
- In a closeout artifact, add `关键结论中文展开` when compressed conclusions are present.
- In final chat, use a shorter `这意味着什么` paragraph when a full table would be too heavy.
- Keep the rule proportional: do not repeat raw logs, do not translate every technical term mechanically, and preserve exact English only when it is necessary evidence.
- Keep the truth-layer boundary: reader-facing explanation does not promote Dashboard memory into KB truth and does not change runtime/schema/gate/acceptance behavior.

Recommended closeout table:

| 原始结论 | 中文解释 | 判断影响 | 证据/边界 | 下一步 |
| --- | --- | --- | --- | --- |
| `<compressed conclusion>` | `<meaning>` | `<allowed / forbidden inference>` | `<evidence or boundary>` | `<action or no action>` |

Suggested user-facing pattern:

```text
I am expanding compressed conclusions into Chinese explanation: meaning, judgment impact, evidence or boundary, and next action, so the closeout can be understood without replaying the whole task.
```

## Semantic Architecture Review Checklist

Use after Semantic Reviewer is triggered and before trying to fix fields, enums, lifecycle states, evidence packaging, or local consistency.

- Evolution direction: if this proposal keeps evolving for five months or one year, what system shape does it naturally become?
- Truth carrier audit: where is semantic truth being placed: law/contract/invariant/ontology, or case/report/matrix/profile/proposal by accumulation?
- Law / witness / governance split: which parts are semantic law, witness evidence, evaluation result, and governance decision? Are they separate objects or one overloaded object?
- God Object scan: does one artifact carry ontology, runtime refs, evaluation state, lineage law, transfer policy, promotion, release approval, and downstream eligibility at once?
- Semantic bureaucracy scan: is the artifact gaining safety by adding fields, approval states, provenance, and consumer matrices while semantic laws remain vague?
- Half-schema / DSL boundary: does the artifact use formal fields, enums, required values, lifecycle states, or validation language? If yes, is it deliberately prose or a versioned DSL with parser/validator/evolution expectations?
- Invariant law check: are invariants executable or at least reviewable through required roles, nodes, edges, transitions, exclusions, violation examples, or structured reviewer rubric?
- Capability algebra check: are families defined through roles, topology, state transitions, output obligations, lineage constraints, exclusions, and failure modes rather than reviewer intuition?
- Minimality check: would splitting the artifact into semantic law, witness case, evaluation result, and governance promotion reduce complexity and improve semantic clarity?
- Finding posture: God Object, semantic bureaucracy, schema-but-not-schema, label-only invariant, intuition-only family, governance inflation, and misplaced truth carrier are formal findings, not optional polish.

Suggested user-facing pattern:

```text
Semantic Reviewer is running Semantic Architecture Review before field-level repair: truth carrier, law/witness/governance split, complexity trajectory, God Object drift, half-schema DSL boundary, invariant law quality, and capability algebra.
```

## Dashboard Agent Mode Checklist

Use when the user asks for Dashboard Agent work, a full Dashboard refresh, macro next-step recommendations, stale-row audit, or blue-sky direction finding.

- Mode: stay read-mostly unless the human explicitly asks to update the Dashboard.
- Full refresh: use `exploration-dashboard-synthesizer` unless the task is explicitly a narrow follow-up.
- Inputs: read current `Dashboard/` Big Ideas, Stage Plans, Sessions, Risks/Decisions/Quality Metrics where relevant, plus the relevant `kb/` architecture, strategy, acceptance, and phase truth.
- Panorama: state current stage, validation maturity, code/artifact quality, active blockers, and quality-vs-speed tradeoff.
- Next candidates: default to three options: quality/stability, speed/progress, and blue-sky beyond the current Dashboard.
- Dashboard update proposals: list archive / cancel / rewrite / add items with evidence and rationale.
- Stale-state handling: when an existing BI/SP/Session looks outdated, say whether to archive, cancel, or rewrite and why.
- Source split: stable governance truth belongs in `kb/`; execution state, session status, priorities, and candidate memory belong in `Dashboard/`.
- Diagnostic lens: when stale rows, deferred candidates, or memory-layer confusion are the issue, use S1-S6 / L0-L6 as bounded reviewer vocabulary and state the countermeasure / memory layer rather than turning the Dashboard into canonical truth.
- Write boundary: only update Dashboard rows after explicit human approval such as “更新 Dashboard”.

Suggested user-facing pattern:

```text
I am reconstructing the Dashboard/KB panorama in Dashboard Agent mode. I will keep Dashboard changes as proposals unless you ask me to update the Dashboard, and I will give three next-step candidates: quality, speed, and blue-sky.
```

## Oracle Review Checklist

Use when a new golden/oracle fixture is being created or materially changed.

- What exactly is being frozen, and at which path?
- Which boundary choices are non-obvious enough that a human should see them first?
- What is the recommended default, and why?
- Is the current artifact still only a proposal, or has the user explicitly approved it?
- If approval is not yet explicit, do not describe the artifact as frozen.

Suggested user-facing pattern:

```text
I have a draft oracle proposal at <path>. The main choices are <A/B/C>. My current recommendation is <X> because <reason>. Please review this before I freeze it as the maintained oracle.
```

## Closeout Language Checklist

Use after the closeout artifact is written and before final completion wording.

- Run `python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode closeout-language --file Dashboard/Artifacts/<...>_Closeout.md`.
- H1/H2 headings must contain Chinese text. English identifiers such as `KB/Dashboard`, `Lane`, `Scope Delta`, or file/session IDs may remain when the heading still explains the section in Chinese.
- Required closeout headings should use Chinese by default: `关键结论中文展开`, `落地范围`, `原始目标覆盖矩阵`, `范围变更复核`, `Lane 启动与例外`, `设计交接`, `验证交接包`, `验证结论`, `明确非目标`, `证据`, `运行的门禁`, `语义复核`, `延后范围`, `KB/Dashboard 复核`, and `后续候选`.
- English verdict/status/routing labels such as `passed`, `done`, `blocked`, `Dashboard-only`, `promote-to-KB`, `no-escalation`, `Single-Agent Exception`, or `Validation Verdict` must have Chinese explanation in the same closeout section.
- Reader-facing evidence citations in Closeout, final summary, Dashboard parent/row prose, and `验证交接包` explanation must use clickable Markdown links to the exact source artifact; do not print bare SHA-256/hash/digest numbers as the human reader's evidence entry point. Keep exact digests in machine-readable lane cards, manifests, snapshots, JSON, or validation reports, and link to those files instead.
- The `验证交接包` section must include an explicitly passing `Closeout language verdict`.
- Missing, failed, blocked, pending, or not-run `Closeout language verdict`, pure-English H1/H2, or unexplained English verdict/status labels are closeout blockers.
- This gate affects reader-facing closeout and governance evidence only; it does not change runtime behavior, schemas, acceptance posture, or KB truth by itself.

Suggested user-facing pattern:

```text
Before final completion I am running the closeout-language gate against the Dashboard closeout artifact. If headings are pure English, verdict/status labels are not explained in Chinese, or the Validation Handoff lacks Closeout language verdict, I will treat the closeout as blocked.
```

## Closeout Deferred-Scan Checklist

Use before the final summary of any non-trivial task.

- Did I create or update the Dashboard closeout artifact?
- Does the closeout artifact use Chinese headings such as `关键结论中文展开`, `落地范围`, `原始目标覆盖矩阵`, `范围变更复核`, `Lane 启动与例外`, `设计交接`, `验证交接包`, `验证结论`, `明确非目标`, `证据`, `运行的门禁`, `语义复核`, `延后范围`, `KB/Dashboard 复核`, and `后续候选`?
- Is the closeout artifact and final closeout summary written in Chinese by default, with English lane/tool output translated or summarized unless exact English evidence is needed?
- Did I include `关键结论中文展开` when the closeout uses compressed conclusions that affect human judgment?
- Did I run `guardrail_checklist.py --mode closeout-language --file <closeout.md>` and record an explicitly passing result under `Closeout language verdict` in `验证交接包`?
- If closeout-language failed, was blocked, was pending, or was not run, did I avoid final completion wording?
- Does the changed Dashboard row reference the closeout artifact?
- Did any part of the tracked scope land only through narrowing?
- Did I include an `Original Plan Coverage Matrix` when executing a Goal / Stage Plan / approved plan?
- Does that matrix include process must-haves and execution topology, rather than only code/artifact deliverables?
- Is the matrix evidence-complete rather than a keyword index: does every original must-have/AC have its own row, or an explicit grouping rationale with an itemized child list, plus an acceptance predicate, exact source-file link, observed result, status, blocker/exception, timing/topology, claim ceiling, and final parent/Closeout absorption?
- Does each row identify the original requirement, observable acceptance predicate, exact source link, actual result, status, blocker/exception, owner/lane or timing, claim ceiling, and parent/Closeout absorption? If not, treat the OPCM as an index only and block final completion wording.
- If independent Validation is claimed, is the durable final Validation artifact linked and bound to the actual closeout/final state/final diff?
- Does every human-facing evidence citation link to its exact source file instead of exposing a raw SHA-256/hash/digest value, while machine-readable digest binding remains in the card/manifest/snapshot/report?
- If an independent visible Builder task was required, does closeout record the real task ID and any human-approved topology exception?
- Does every original must-have show `landed`, `not landed human-approved deferred`, `not landed blocked`, or `not applicable with reason`?
- If any original must-have remains not landed without approved deferral, not-applicable rationale, or blocker/termination status, did I avoid `SP complete`, `Goal complete`, and equivalent full-completion wording?
- Is there a concrete deferred remainder that should become a follow-on session?
- Did a non-blocking refinement become concrete enough that losing it would create rediscovery cost?
- Did this task change which `SP` / `Sessions` are the best next candidates?
- Did the task intake evaluation change, narrow, reject, or escalate the original instruction, and is that reflected in the closeout?
- Did any approved proposal, closeout, reviewed seed, baseline, matrix, contract, or gate artifact trigger the Contract Delta Scan?
- Did I state the KB review result?
- Did I state the Dashboard review result?

Suggested user-facing pattern:

```text
Before closeout I am creating or updating the Dashboard closeout artifact and doing the deferred/emergent-session scan. If this task left a concrete remainder or surfaced a later candidate, I will record it in Dashboard/Sessions.md instead of leaving it in chat memory.
```

## A1 Adequacy Checklist

Use when an `A1` contract-calibration batch may be ending or being promoted into `A2`.

- Is there a phase-specific prompt, rather than a generic or implicit prompting pattern?
- Are `run1 ... runN` artifacts or equivalent preserved attempts available, rather than only the final successful sample?
- Did the run set include at least one maintained positive shape, one boundary/negative shape, and one rerun after a prompt revision?
- If fewer than 5 effective runs were used, did the human explicitly waive that floor?
- Did the latest two rounds stop surfacing new material failure modes, or are new tensions still appearing?
- If the reviewed seed is stable, can the remaining drift now be restated as deterministic blocking/advisory rules, normalization policy, or explicit exclusions?
- If yes, am I still chasing raw exact provider reproduction out of habit instead of pivoting to `A2` acceptance hardening?
- Have I established intra-model stability before considering a second model?
- If I want a second model, what concrete calibration question will it answer that the current model evidence cannot?
- Is there an adequacy report that separates contract pressure, prompt pressure, golden/oracle pressure, and still-unresolved tensions?
- Has the human had a review window when the phase is new or still unstable?
- If any of these are missing, do not describe `A1` as complete.

Suggested user-facing pattern:

```text
Before treating A1 as complete I am running the adequacy checkpoint. I will verify that we have enough phase-specific prompt/run evidence, preserved failures, and an explicit adequacy report before we promote this batch into A2.
```

Suggested pivot pattern:

```text
The reviewed seed now looks stable and the remaining drift is mostly canonical-field ownership or exactness oscillation. I am switching from prompt micro-tuning to A2 acceptance hardening so we can encode the semantic boundary as a deterministic gate instead of chasing one exact provider rendering.
```

## Mapping The Repeated Failure Modes

| Failure mode | Checklist response |
| --- | --- |
| AI treats a user instruction, attachment, proposal, or approval text as immediate implementation authority | Run the Task Intake Evaluation checklist first: identify objective, source authority, boundaries, risk, and execution route before editing. |
| AI treats `执行 S-xxx` / `执行 SP-xxx` as permission to stay single-agent | Run the Multi-Agent Default checklist and either start Design / Builder / Validation / Closure lanes or record a Single-Agent Exception in the closeout artifact. |
| AI starts post-C0 implementation without a design artifact | Run the Post-C0 Design Handoff checklist and save the design artifact, or record an explicit design-lane exception before Builder implementation dominates. |
| AI substitutes scope, validates only the revised design, or marks an unapproved narrowed Goal as done | Run the Goal Conformance / Scope Delta checklist: create the original must-have ledger, record Scope Delta entries, require approval for material deletion/replacement, and block `SP complete` when any original must-have lacks landed evidence, approved deferral, not-applicable rationale, or blocker/termination status. |
| AI creates a visible task but performs Builder work in the Orchestrator thread | Treat this as a topology Scope Delta. Require task/thread evidence and a human-approved topology exception; otherwise close only as partial/exception-recorded. |
| Closeout claims independent Validation but only links a handoff, Semantic Review, tests, or an Orchestrator summary | Block completion until a durable Validation Review or post-closeout reconciliation binds reviewer/source, Read Manifest, actual closeout, final Dashboard/KB state, and final diff. |
| Closeout exposes raw SHA-256/hash/digest numbers instead of a source link | Replace the human-facing citation with a clickable link to the exact source artifact and explain its evidence boundary in Chinese; retain the digest only in machine-readable evidence where the gate requires it. |
| Final audit maps feature outputs but omits lane order, visible-task topology, reviewer timing, or other process must-haves | Require a multi-session Evidence Completeness Matrix and record omissions as Scope Delta; do not allow `Scope Delta: 无` or audit complete. |
| Goal Agent drafts a prompt from chat momentum, omits mandatory evidence, or accepts Orchestrator pressure to close as pass/done before required reading and gates are complete | Run the Goal Agent Prompt Quality checklist: create a Read Manifest, preserve the original must-have ledger, integrate acceptance criteria, and if evidence is missing answer `当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。` |
| AI drafts a golden and silently treats it as frozen | Run the oracle review checklist and pause for human review unless final semantic choice was explicitly delegated. |
| A concrete refinement is mentioned in closeout but not turned into a session | Run the closeout deferred-scan checklist and add the row in `Dashboard/Sessions.md` during the same task. |
| AI ends `A1` after 1-2 lightly compared runs and claims contract adequacy is good enough | Run the A1 adequacy checklist and block promotion until prompt/run evidence, adequacy reporting, and human review expectations are satisfied. |
| AI keeps tuning prompt wording even though the reviewed seed is stable and the remaining disagreement is only canonical drift | Use the A1 adequacy checklist to trigger the A1 -> A2 pivot and encode the boundary as executable acceptance instead of chasing exact provider phrasing. |
| Validation is expected but receives only a vague final summary | Run the validation handoff checklist and provide the lightweight packet before treating validation as meaningful. |
| Approved Dashboard artifact contains stable contract or promotion rules but closeout says no KB update because the artifact is under Dashboard | Run the Contract Delta Scan and either promote the stable subset into KB JSON, classify it as Dashboard-only evidence with rationale, route it to gate docs or runtime/tests, or add a deferred session. |
| Semantic-risk triggers are visible but no independent review happens | Run the Semantic Reviewer trigger checklist and either start the lane or record a no-escalation reason. |
| Semantic Reviewer accepts the artifact's own frame and only checks wording or table consistency | Run the Semantic Reviewer Frame-First checklist; missing layer split, ontology, invariant model, failure taxonomy, transfer rules, or promotion boundary becomes a finding. |
| Semantic Reviewer keeps adding fields/status/provenance to a flawed object | Run the Semantic Architecture Review checklist; God Object drift, semantic bureaucracy, schema-but-not-schema, misplaced truth carrier, label-only invariant, or intuition-only family becomes a finding. |
| Dashboard Agent advice becomes ordinary backlog sorting or automatic row mutation | Run the Dashboard Agent Mode checklist, rebuild the Dashboard/KB panorama, give three next-step candidates, and keep updates proposal-first until the human approves them. |
| Closeout evidence only appears in the final chat | Create or update the Dashboard closeout artifact and reference it from the changed session or stage row. |
