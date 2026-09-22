---
name: sge-governed-checkpoints
description: Govern non-trivial SGE work with intake, context bootstrap, specification-first acceptance, validation, semantic review, Dashboard closeout, and Loop continuation.
---

# SGE Governed Checkpoints Kernel

本文件是默认读取 kernel。它只保存路由、不可违反的 invariants 与 hard stops。具体执行顺序读取命中的 `references/recipes/`；完整模板与解释按证据触发读取 `references/checklists.md` 或 `references/context-efficient-goal-validation.md`。未知或冲突 trigger 必须扩读，不能静默省略所需认知域。

## Source of truth 与声明边界

- 原始用户意图是 authority；Intake、Goal、card、receipt 都是 projection，不得替换或缩小它。
- `kb/data/` 是稳定 canonical truth，生成 Markdown 是 reader projection，`Dashboard/` 是 execution memory，tests/fixtures 是 witness。
- schema、prompt、card、Design、RED、GREEN、自检与 handoff 都不是独立 Validation 或最终完成证据。
- 声明强度不得超过证据。禁止 schema substitution、recompute validation collapse、profile/routing collapse、deterministic masking、mock grounding、scope substitution 与 false closure。
- 默认不证明 cross-Agent consistency/compatibility、release、production readiness 或 provider cost。

## G01-G12 Hard-gate routing

| ID | Gate | 触发条件 | Recipe / 条件扩读 |
| --- | --- | --- | --- |
| G01 | Task Intake | 每个请求；持久编辑、外部 artifact、contract/KB/Dashboard 必须显式 | `references/recipes/intake-and-first-task.md`；复杂判断扩读 checklists |
| G02 | Context Bootstrap | Intake 后按 read_only/implementation/validation 构造 packet | intake recipe；Goal/Validation 扩读 context protocol |
| G03 | ERBE specification-first | 终态谓词、状态机、authority、acceptance/promotion/write 边界或高语义风险 | `references/recipes/design-and-builder.md` |
| G04 | SGC v1 | non-trivial completion/validation/promotion/runtime widening/truth placement 前 | 所有 non-trivial recipes；canonical SGC KB |
| G05 | Goal Conformance | Goal、Stage Plan、tracked Session 或 approved plan | `references/recipes/goal-and-loop.md` |
| G06 | Loop Continuation | `/goal`、Loop Goal 或多 Session Stage Plan | goal recipe |
| G07 | Goal Agent Quality | 起草、review、patch、finalize Goal Prompt | goal recipe；patch 细则扩读 context protocol |
| G08 | Context Efficiency / Delta Validation | 分层上下文、修复轮、snapshot、delta 或 rebaseline | `references/recipes/delta-validation.md` |
| G09 | Validation Agent Quality | 独立 Validation verdict 前 | `references/recipes/validation.md`；固定 prompt 扩读 checklists |
| G10 | Semantic Reviewer Quality | semantic-risk 或 Goal 明示 pre/final review | `references/recipes/semantic-review.md` |
| G11 | Multi-Agent / Lane Card | tracked/non-trivial work与所有 non-trivial 委派 | design recipe；card 细则扩读 context protocol |
| G12 | Closeout / KB-Dashboard / BDD | tracked closeout、stable truth、maintained gate 或 final claim | `references/recipes/closeout.md` |

Machine mapping：`references/context-routing-manifest-v1.json`。G01..G12 必须精确覆盖；removed trigger、dangling recipe、default-read cycle 或 coverage regression 均 fail closed。

## 不可违反的 execution invariants

1. 每个请求先做 proportional Intake，再构造 profile-specific Context Bootstrap；digest 未变化也要 refresh objective、authority、claim ceiling 与 critical dependencies。
2. Context Optimization 只减少重复读取，不得缩小完成任务所需的 epistemic search space。required domain 缺失时扩读或报告 evidence gap。
3. 高语义风险 Goal 在 Builder 前冻结 machine-readable Contract/Cases、axes、predicates、invariants、counterexamples、forbidden collapses、oracle、write exclusions 与 claim ceiling。
4. 可信 RED 必须是 contract valid、execution ok，并按预期 fingerprint 失败。GREEN 复用同一 frozen case identity；Builder 不得修改 frozen assets。
5. 原始 must-have 与流程条款进入 ledger；删除、替换、改名、降级、延期、换 authority 或 non-goal 化都属于 Scope Delta，未获人类批准不得关闭原分母。
6. non-trivial lane 委派前必须 validate `lane_task_card_v1`，再由 renderer 生成 prompt。接收端复验 expected digest；source drift、缺 write scope、`fork_context=true` 或稳定大段重复均 fail closed。
7. tracked/non-trivial 工作按影响启用 Design、Builder、Validation、Closure；Semantic 与 Dashboard lanes 按 trigger。未启用应工作的 lane 记录 Single-Agent Exception；用户沉默不是授权。
8. Design 只提供实现输入。Validation read-mostly，并同时检查 landed package 与 original objective；除非人类明确授权，不替 Builder 修复。
9. 首轮 Validation 建 full baseline；后续用 snapshot + Delta Read Set。用户/Goal/governance/AC/authority/claim/truth/topology/threat/snapshot 或 inventory 变化触发 rebaseline。
10. Validator 判断当前合同，Adversarial Tester 查当前 threat scope，Governance Architect 提未来 hardening；“还能更严格”不是无限 blocker。
11. stable law 写入 KB JSON；state、blocker、decision、closeout evidence 与 concrete follow-on 写入 Dashboard。两者不得互相冒充。
12. maintained non-unit gate/case 变化执行 BDD Sync；reader cards 保存在 `tests/bdd/readable_cards/`，临时 report 不算 landed evidence。

## Hard stops

- Goal 缺失或冲突不得启动 governed Builder；用 `scripts/first_task_router.py`。
- required capability unavailable/unknown 时 blocked；optional unavailable 使用显式 core fallback；用 `scripts/capability_preflight.py`。
- lane no-output/card drift/execution failure 不得静默 takeover；actual topology append-only，独立 Builder takeover 需可定位人类批准；用 `scripts/lane_lifecycle.py`。
- `completed` 不等于 `evidence_bound`；pre-closeout Validation 不得冒充 final-state binding。
- receipt 只索引并重算 durable refs；self-report、handoff 或绿测不替代 Validation；用 `scripts/conformance_receipt.py`。
- closeout H1/H2 必须中文，英文 verdict/status 必须中文解释；未通过 closeout-language gate 不得声明完成。
- final pass 必须有唯一独立 reviewer/source 的 durable review，覆盖实际 closeout、最终 KB/Dashboard、完整 diff 与 post-closeout reconciliation。
- 只有必须由人类行使 authority、destructive/external write、未批准 Scope Delta、同一恢复条件连续失败超过阈值或用户暂停时，未终止 Loop 才能停。

证据不完整时：`当前不能声明完成；缺失证据为：...；可选收束状态只能是 blocked/partial，不能是 pass/done。`

## Loop continuation

每个 Session closeout 记录 `goal_terminal`、`next_session`、`next_session_ready`、`human_decision_required`。当 Goal 未终止、下一 Session ready 且无需人类决定时，Session boundary 不是停止点；同一回合自动进入下一 Session。恢复或 context compaction 后，从 Goal、Dashboard 与最近 closeout 找到第一个 ready 且未完成 Session。

## Recipe selector 与 conditional reads

- 首任务分类/bootstrap：`references/recipes/intake-and-first-task.md`
- Goal、Goal Patch、Stage Plan/Loop：`references/recipes/goal-and-loop.md`
- Design、Builder、ERBE/lifecycle：`references/recipes/design-and-builder.md`
- 独立 Validation：`references/recipes/validation.md`
- delta repair/reconciliation：`references/recipes/delta-validation.md`
- Semantic Review：`references/recipes/semantic-review.md`
- Closeout、KB/Dashboard、BDD：`references/recipes/closeout.md`
- core-only 初始 KB：`references/initial-kb-bootstrap.md`

只读命中的 recipe。需要固定 prompt/template、完整 output shape、semantic taxonomy 或特殊 approval wording时扩读 `references/checklists.md`。需要 Goal Patch resolution、Validation State Snapshot、Delta Read Set/rebaseline、lane-card/prompt/duplication audit 或 convergence 轮次管理时扩读 `references/context-efficient-goal-validation.md`。

`goal_patch.py` 默认验证 Codex 的 user-message provenance；非 Codex Agent 必须提供平台交付的 `approval_receipt_v1`，并通过 `--approval-source-root` 显式指定平台管理的 trusted root。项目内 Agent 自己写出的普通文件不能作为人类批准来源；缺少可验证 receipt 时保持 blocked。

## Deterministic entry points

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode <mode>
python3 .codex/skills/sge-governed-checkpoints/scripts/context_bootstrap.py validate <packet.json>
python3 .codex/skills/sge-governed-checkpoints/scripts/lane_task_card.py validate <card.json> --repo . --expected-card-sha256 <sha256>
python3 .codex/skills/sge-governed-checkpoints/scripts/lane_task_card.py render <card.json> --repo . --expected-card-sha256 <sha256>
python3 .codex/skills/sge-governed-checkpoints/scripts/task_classifier.py <task-facts.json>
python3 .codex/skills/sge-governed-checkpoints/scripts/topology_gate.py plan <classification.json>
python3 .codex/skills/sge-governed-checkpoints/scripts/topology_gate.py evaluate-series <topology-snapshots.json>
python3 .codex/skills/sge-governed-checkpoints/scripts/managed_activation.py activation <activation-facts.json>
```

工具只提供 deterministic evidence，不自动证明 task quality、authority、语义正确、独立 Validation 或完成。

v1.1 路由只读取通用任务事实。硬触发优先；事实缺失或冲突时 `unknown` 并 fail closed。lane plan 不是实际执行证据，必须在 `pre_builder`、`pre_validation`、`pre_closeout`、`final` 四个 checkpoint 从 identity、capability、lifecycle 与 durable output 重算。安装记录不能替代宿主 capability；缺 capability 时仅允许已存在且可定位的 topology exception，否则阻断。
