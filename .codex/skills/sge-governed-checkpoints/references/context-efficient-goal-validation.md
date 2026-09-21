# Context-Efficient Goal and Validation Protocol

## Purpose

在不跳过 Original Plan Coverage、Scope Delta、独立 Validation、Semantic trigger、closeout-language 或 KB/Dashboard review 的前提下，减少稳定上下文重复注入、Goal 全文重写和多轮 Validation 全量重读。

## Task Bootstrap Profiles

每个任务在 Intake 后选择一个启动 profile：`read_only`、`implementation` 或 `validation`。Raw User Intent 始终是 authority；Intake 只是 projection。非 trivial task 使用 `context_bootstrap_v1` packet，并在执行前校验：

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/context_bootstrap.py validate <packet.json>
python3 .codex/skills/sge-governed-checkpoints/scripts/context_bootstrap.py render <packet.json>
```

| Profile | Required focus | Omit by default |
| --- | --- | --- |
| read_only | read scope、write exclusions、evidence-gap action、output claim | Builder flow、实现规则、完整 closeout 正文 |
| implementation | write scope、contract/AC refs、affected gates、Validation entry | 无关历史 Session、完整 Agent Logs、相邻 lane 背景 |
| validation | original objective、claim ceiling、AC、actual diff、final state | Builder reasoning、重复治理正文、完整历史日志 |

所有 profile 都必须声明 Required Read Set、Conditional Read Set、Semantic Refresh、required epistemic domains、change-impact vector 和 topology。deterministic trigger 不得被 Agent 关闭；evidence-backed agent-evaluated trigger 只能扩读。即使 digest unchanged，也要重新确认 objective、authority、claim ceiling 和 critical dependencies。topology 由 change impact 决定，不只看 artifact type。

核心不变量：Context Optimization 可以删除重复文本与不适用内容，但不得缩小完成当前任务所必需的 epistemic search space。缺少 required domain 时必须扩读；无法取得证据时报告 evidence gap，不得用 profile 较窄或 token 成本作为跳过理由。稳定规则在 renderer 中只保留 path@revision/digest、applicability 与 reason。

`context_bootstrap.py validate` 只验证 packet 的结构、authority role、触发器、semantic refresh、影响向量与认知域覆盖声明；它不验证文件存在、revision/digest 真实性、用户授权、读取是否真的发生或最终任务质量。需要 digest-bound delegation 时继续使用 `lane_task_card.py`；最终质量仍由实际读取、测试和独立 Validation 证明。

## Three-Layer Goal Context

| Layer | Stores | Must not repeat |
| --- | --- | --- |
| Global Governance Context | 当前 `AGENTS.md`、checkpoint skill、稳定 KB strategy | 不复制进每个 Goal |
| Loop Goal | mission、original requirement IDs、Session DAG、approval checkpoints、Loop claim ceiling、completion rule | 不展开每个 Session AC/实现细节 |
| Session Task Card | 当前 objective、Loop requirement IDs、Delta Read Set、AC pointer、outputs、maximum claim | 不携带其他 Session 的完整上下文 |

Builder 前必须解析出一份完整 Final Session Goal。引用和 patch 用于减少重复，不允许让 Builder 自己拼猜 authority。

## Machine-Valid Lane Task Card

每个 non-trivial Design、Builder、Validation、Semantic 或 Closure lane 在 delegation 前必须有 `lane_task_card_v1`。Task Card 保存 source digests、baseline/delta mode、snapshot、Delta Read Set、AC IDs、write scope、required outputs、maximum claim、forbidden-claim refs、topology 和 rebaseline reference；不复制稳定文档正文。

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/lane_task_card.py validate <card.json> --repo .
python3 .codex/skills/sge-governed-checkpoints/scripts/lane_task_card.py render <card.json> --repo . --output /tmp/lane-prompt.txt
python3 .codex/skills/sge-governed-checkpoints/scripts/lane_task_card.py audit <audit-manifest.json> --repo . --output <report.json>
```

Rules:

- Orchestrator 下发 renderer 输出，不手写全文 lane prompt；renderer 不展开 Goal/AC/governance 内容。接收 Agent 先执行 renderer 中的 `--expected-card-sha256` 命令，避免委派后 card 被整体替换但内部仍自洽。
- `delta` card 必须绑定可定位 snapshot；source digest 漂移、路径越界、Builder 空 write scope 或 `fork_context=true` 必须 fail closed。
- 多个相邻/并行 lane 下发前运行 duplication audit：稳定 source 的长连续局部复制（包括首尾裁剪或插入空行重排）和跨 lane exact repeated block 是 blocker，near duplicate 是 advisory。
- 不设置统一字符或 token 上限。短提示仍可能错误，长提示也可能有必要；门禁判断的是重复 authority、delta provenance 和执行边界。
- 首轮可用 `full_baseline`；后续 lane 默认复用 baseline/snapshot，只读 card 指定 delta。命中 rebaseline trigger 时显式切回 full baseline 并记录原因。

## Goal Patch

```yaml
goal_patch:
  base_goal_id: S-XXX-goal
  base_revision: <commit-or-content-digest>
  sequence: 2
  target_section: fixed_roles
  replacement_ref: <inline-small-delta-or-artifact-path>
  reason: replace external threads with subagents
  scope_delta: none
  conflicts_with: []
```

Rules:

- Draft review 默认只输出 patch；首次 draft 和最终 executable artifact 才输出全文。
- Patch sequence 必须连续；同 section 多 patch 按 sequence 应用，冲突必须由 Goal Agent 显式解决。
- Original must-have identity、human approval authority、claim ceiling、completion rule 的修改必须走 Scope Delta / approval，不能作为普通 patch 隐藏。
- Final Goal 必须列出 base revision 和 applied patch IDs；Builder 不接受 patch-only handoff。

## Core and Delta Read Sets

- `Core Read Set` 在 Loop 或首轮 Validation 中定义一次：original objective、active contract、AC、Loop ledger、claim ceiling、truth placement。
- `Delta Read Set` 只列当前 changed files、受影响 gates、open blockers、final-state surfaces 和新增证据。
- 共享上下文包必须带 `context_id`、`revision`、source paths 和 invalidation triggers；引用失效时 rebaseline。
- 普通进度只输出 `Read Manifest: core reused / delta read / missing`；完整明细留在正式 Validation/closeout artifact。

## Validation State Snapshot

```yaml
validation_state:
  snapshot_id: S-XXX-val-r1
  parent_snapshot: null
  repo: <absolute-or-repo-id>
  worktree: <path>
  baseline_commit: <sha>
  dirty_state_digest: <digest>
  tracked_changed: []
  untracked: []
  renamed: []
  generated_surfaces: []
  critical_file_hashes: {}
  goal_ref: <path@revision>
  acceptance_ref: <path@revision>
  claim_ceiling_ref: <path@revision>
  validated_scope: []
  known_blockers: []
  last_verdict: blocked
  reviewer_source: <thread-or-subagent-id>
  created_at: <iso8601>
  reopen_triggers: []
```

Snapshot 可以放在 closeout 的短 section 中；只有预计多轮修补时才需要独立 artifact。changed inventory 必须来自 `git status` / `git diff` /生成物扫描，不只依赖 Builder handoff。

## Rebaseline Triggers

命中任一项即重新读取完整 baseline：

- 用户新增或覆盖指令；Goal、AGENTS、checkpoint 或 AC revision 变化。
- Original objective、claim ceiling、approval authority、truth placement、KB/Dashboard routing、依赖或 execution topology 变化。
- Threat model 或 semantic-risk 等级变化。
- Goal Patch base/sequence 冲突，或 Final Goal 无法确定性解析。
- Baseline commit/worktree/hash 不可定位；snapshot 缺失、过期或来源不明。
- 出现未纳入 snapshot 的 untracked、renamed、generated surface。
- Final diff 超出 Delta Read Set，或受影响 gates 无法确定性推导。

## Validation Role Split

| Role | Question | Output authority |
| --- | --- | --- |
| Validation Reviewer | 当前合同是否满足？ | pass/fail/blocker |
| Adversarial Tester | 当前 threat scope 是否存在明显 bypass？ | attack findings；只在当前 scope 内阻断 |
| Governance Architect | 规则未来是否应扩大？ | evolution proposal；默认不阻断当前任务 |

同一 Agent 可以承担多个角色，但必须分段输出，不能把 evolution proposal 自动升级为 current blocker。

## Adversarial Levels

- Level 1 Contract Boundary：empty、missing、wrong type、invalid enum、required evidence。默认必检。
- Level 2 Semantic Abuse：fake provenance、false approval、hidden overclaim、authority substitution。语义/治理任务默认必检。
- Level 3 Security Hardening：path traversal、parser ambiguity、injection、resource exhaustion。只有 AC、threat model 或高风险触发时才阻断；否则登记 hardening follow-on。

## Blocker Admissibility and Convergence

新 finding 只有在违反当前 AC/合同、original must-have、evidence integrity、authority boundary、claim ceiling 或造成 in-scope regression 时才是 blocker。

默认流程：initial full validation -> blocker-fix delta validation -> final-state reconciliation。第四轮及以后必须写 blocker admissibility 或 rebaseline reason。连续两个 delta round 从同一根因产生新 blocker时，停止微补丁，升级为 rebaseline、独立 hardening Session 或人类 scope 决策。

当 AC 全覆盖、已知 blocker 关闭、final-state reconciliation 无新 admissible blocker，剩余 finding 仅为 enhancement/future hardening 时，允许 `pass-with-findings`。这不是固定三轮上限，也不允许用 token 成本跳过 mandatory evidence。

## Lane and Output Proportionality

- 新设计、实现、KB truth、runtime/schema、acceptance 或 semantic widening：使用适用的 Design/Builder/Validation/Closure lanes。
- 窄 read-only delta reconciliation：可只使用独立 Validation lane；其他 lane 标 `not applicable for delta-only review`，记录判定者、snapshot/diff、风险和 claim impact。
- 独立 Validation verdict、final reconciliation 或必要 closeout 不得由 no-op 替代。
- 工作更新只写新增信息；正式 artifact 才展开完整 manifest、evidence matrix 和中文边界。
- Agent Log 记录时间、动作、新证据、状态变化和引用。高保真意味着 delta 可追踪，不意味着复制稳定上下文、raw tool output 或 closeout 全文。

## Maintained Tooling

- `scripts/context_state.py collect`：从 git-observed facts、versioned semantic declarations 和 explicit generated registry 建立 snapshot。三种 authority 不得互相猜测。
- `scripts/context_state.py compare`：只在 snapshot 结构完整、semantic refs 未变、generated registry 完整、final drift 全部进入 Delta Read Set 时返回 `delta_safe`；该状态不是 Validation verdict。
- `scripts/context_state.py usage`：只接受 fresh single-turn、matching terminal task、单调 token events 的 rollout；输出 model-reported usage、prompt/tool payload derived metrics 和 source digest。
- `scripts/goal_patch.py`：验证 canonical Goal/patch、source-verified human-owned Codex thread user-message approval provenance，或显式配置 trusted root 下的 provider-neutral `approval_receipt_v1`、immutable Goal identity、protected claim carriers、deterministic resolution 和 Markdown round-trip。receipt 只是外部 Agent/平台交付的绑定凭证，不是脚本自行生成的批准，也不等于通用身份认证或外部签名；没有可验证来源时必须 fail closed。
- `scripts/goal_patch.py audit-duplication`：exact stable copy 是 blocker，near duplicate 是 advisory；exact blocker 不允许用无 authority suppression 消失。
- `scripts/lane_task_card.py validate/render/audit`：验证 lane contract、生成最小 delegation prompt，并对实际 prompt artifact/rollout user message 做重复审计。它不执行 lane、不授予 human approval，也不把低重复率翻译成质量通过。
- `scripts/context_bootstrap.py validate/render`：校验 profile packet 的结构与 fail-closed 不变量，并生成不复制稳定规则正文的启动提示。它不验证路径/digest 真实性、不证明读取已发生、不授予 authority，也不输出质量 verdict。

Token 对照试验必须采用 fresh independent arms、AB/BA counterbalance、相同 model/effort/base-instructions/environment、frozen oracle 和每臂独立质量通过。报告 `input/cached/uncached/output/reasoning/total`，但 reasoning 不重复加入 provider total。Payload bytes 单独标为 derived metric。
