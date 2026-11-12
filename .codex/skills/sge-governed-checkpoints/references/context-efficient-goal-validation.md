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

默认流程：initial full validation -> blocker-fix delta validation -> final-state reconciliation。实际轮次上限由适用的 Goal、AC、AGENTS 或明确用户决定约束；若工件最多三轮，执行到第三轮后必须停止该工件的 review/validation，并记录 blocker 与未完成 AC。只有适用的 authority 明确允许超过三轮时，第四轮及以后才可启动，且必须写 blocker admissibility 或 rebaseline reason。此通用收敛建议不授权突破更严格的工件预算。连续两个 delta round 从同一根因产生新 blocker 时，停止微补丁，升级为 rebaseline、独立 hardening Session 或人类 scope 决策；仍不得重置或突破当前工件预算。

当 AC 全覆盖、已知 blocker 关闭、final-state reconciliation 无新 admissible blocker，剩余 finding 仅为 enhancement/future hardening 时，允许 `pass-with-findings`。此处描述的是可接受的最终 verdict，不是 review 轮次授权：任何当前 Goal、AC、AGENTS 或明确用户决定设定的工件级累计轮次上限优先；若上限为三轮，第四轮不得以 `pass-with-findings`、rebaseline、revision、card 或新 cycle 为由启动。不得用 token 成本跳过 mandatory evidence。

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

## 按文件状态保全与增量复核

本节在任务将修改、删除或覆盖文件时按需读取。稳定原则以 [上下文策略只读阅读投影](readers/context-layering.md#按状态保全与按职责复核)（唯一 canonical 仍在发行 source 仓 `kb/data/strategy/strategy_context_layering_v1.json`；[来源记录](readers/projection-sources.json)） 的 `preservation-and-review` 为准；本节提供操作解释和合成示例。它沿用前述 Validation State Snapshot、Core/Delta Read Sets 和 Rebaseline Triggers，不另建一套评审制度，也不豁免既有独立 Validation、实体引用、冻结输入及关闭门禁。

### 分清保全、输出与阅读

保全回答“写前状态以后能否恢复”，可以由工具复制必要原件或绑定可靠固定版本；工具输出回答“这次返回什么给模型”，默认只返回位置、数量、校验结果和异常；阅读回答“评审者为本次判断需要理解什么”，按有效基线、影响范围与职责选择。工具在磁盘复制文件而只返回摘要，不会因此把整份内容自动注入模型；模型重新生成、工具全文返回和重复读取才会增加相应上下文。已可靠保存内容不等于该全文输出，也不等于该跳过必要阅读。

需要比较收益时，分别陈述保存字节量、重复保存字节量、工具输出字节量、重复阅读量和有来源的实际 token 用量；没有真实日志时 token 及费用收益保持未知。字节指标不能直接转换成真实 token，不能用“字节数除以四”证明收益。本节不新增强制收益报告或额外评审轮次；既有强制 gates 继续执行。

### 修改前选择表

选择前确认受影响路径、文件类型、提交/暂存区/工作区各版本、保留期限及交付环境。下表中的“保全”包括必要原件及足以重建状态的记录，并非复制整个仓库。

| 文件状态或边界 | 默认方式与必须记录的内容 | 不满足条件时及禁止误用 |
| --- | --- | --- |
| 干净且已提交 | 内容确与固定 commit/blob 的原始字节相同；确认该版本在约定保留与交付环境可取回，并有所需对象、文件类型、权限及外部依赖。条件满足可免额外备份 | 只有提交号不能证明可恢复；对象丢失、错摘要、checkout 字节转换或依赖不足时保存必要原件；实体门禁仍需实体文件 |
| 已跟踪但未提交 | 分别记录 commit、index、worktree；保存实际写前未提交版本及恢复所需元数据 | HEAD 不能冒充用户写前内容；普通文本 diff 不是所有类型的通用备份 |
| 部分暂存 | index 与 worktree 分别保全，记录路径、类型/模式和各自版本；恢复核对 cached diff 与 unstaged diff | 只存 worktree 并记 dirty 会丢失暂存边界；不能假定复制 .git/index 可在另一仓库通用恢复 |
| 未跟踪且即将改动 | 写前保存一次必要原件，记录未跟踪状态 | 不以 Git 未跟踪为由漏项，不把它误加成已跟踪历史 |
| 被忽略且明确受影响 | 即使常规 status 不展示，也纳入受影响清单并保存必要原件 | 未受影响的忽略内容不因本表而全量收集；敏感真实内容不应进入示例或全文工具输出 |
| 原先不存在的新文件 | 显式记录 absent；恢复后该路径仍不存在 | 空文件是存在的内容，不能冒充 absent；真实工作区删除恢复须先排除后续用户写入 |
| 只读检查、不改文件 | 无需写前备份；需要固定审查对象时依现有合同绑定版本 | 不以只读名义放松审查对象身份与必要阅读 |
| 二进制 | 保留精确字节与所需类型/元数据，核对读取转换 | 不把普通文本补丁描述成二进制完整恢复保证 |
| 符号链接 | 保存链接本身类型、目标字符串及所需目标依赖；明确是否纳入目标，不盲目跟随链接 | 链接目标的文件字节不能替代链接本身；目标不可交付时不声称完整恢复 |
| 权限与可执行位 | 保存平台适用的模式、可执行位及实际需要的其他元数据，恢复后核对 | Git 通常不保留所有 ACL/扩展属性；超出保证时保存必要原件/元数据并报告范围 |
| 重命名或删除 | 记录旧/新路径、存在状态及 index/worktree 关系，保留内容和恢复所需对象 | 内容相同不足以证明路径关系与暂存状态恢复 |
| 内容被 A/B 任务复用 | 内容可只存一份，但 A/B 分别保留来源、用途、绑定版本、评审关系及存储保留/交付条件 | 不依赖另一任务随时可清理的临时材料；合同要求独立实体则继续提供 |
| 现有实体引用接口 | 按门禁提供合规工作区实体文件；Git 身份可以作为另列来源记录 | 不向 path-only 字段填 commit:path/blob，不用工作区外共享目录绕过路径限制 |
| 第二轮与新独立评审者 | 原 Reviewer 仅在有效基线和影响/职责覆盖下复用；新 Reviewer 建立足够阅读基础 | hash 相同不是理解相同，不自动免除语义刷新、原始目标检查或独立判断 |
| 已冻结输入与历史包 | 保留冻结版本、来源和评审绑定；沿用旧路径、摘要与 receipt 的原有语义 | 当前同名路径最新内容不能替换旧输入；不追溯重写历史证据或自动清理 |

固定 Git 引用还应考虑 LFS 实体、submodule 固定版本、链接目标、attributes/filter 和交付时可获得的外部依赖；commit/blob 身份不自动包含这些内容。无法保证约定环境精确恢复时，在修改前回退到必要原件与元数据保全；若写前已丢失且无可靠来源，应报告缺口，不能把修改后文件称作原件。“基线＋补丁”仅在完整覆盖相关状态且经隔离恢复核对时作为可选方式，不设为默认，不新建通用工具。

### 一个贯穿保存、修改与复核的合成故事

以下都是虚构内容，在临时 Git 仓库进行；不复制产品源码，不恢复真实用户工作区，也不提供跨仓库通用备份保证。文档故事描述预期行为；任务中实际合成执行和独立人工判断由各自证据另行证明。

**首次修改前判断。** 操作者要改 clean.txt、dirty.txt、partial.txt、draft.txt、ignored.tmp，并创建 new.txt。clean.txt 已提交，内容为 `mode=safe\n`；dirty.txt 工作区为用户未提交的 `owner=user\n`；partial.txt 的提交、暂存区和工作区分别为 `threshold=1\n`、`threshold=2\n`、`threshold=3\n`。draft.txt 为未跟踪的 `draft=user\n`，明确受影响的忽略文件 ignored.tmp 为 `secret=synthetic\n`；new.txt 原先不存在。这里的 `\n` 表示 LF 字节，不是把反斜杠文本存进配置。

**保存或引用。** 在这个有明确生命周期的隔离仓库内，先固定 clean.txt 的 commit/blob，读取原始字节并核对；保留恢复需要的 Git 对象与元数据，确认在此次实验保留环境可取回，因此可以省去额外内容副本。对 dirty.txt 保全工作区用户内容；对 partial.txt 分别保全 index 的版本2与 worktree 的版本3，并记录提交版本1。draft.txt、ignored.tmp 保存必要原件及其未跟踪/忽略身份；new.txt 只记录 absent。工具返回保全位置、引用位置、5个既存受影响文件及1个不存在路径的数量、校验结果和异常摘要，不全文输出配置。该摘要不能代替评审阅读；新建文件的 absent 记录不能算一份空文件备份。

实验可在**同一个临时仓库**保存并恢复原始 .git/index，其正确性依赖该仓库相同对象库与相关元数据仍在；它只用于隔离案例，不能推广成“复制 index 即可跨仓恢复”。需要跨环境交付时，应保留可取回对象、各路径的 index/worktree 内容及模式、存在性和关系，并证明目标环境可恢复；不能证明就保存必要原件，不能仅交一个 index 文件。二进制、指向 target.txt 的链接、模式0755的脚本及 old.txt→renamed.txt 暂存重命名在同一实验中分别保留精确字节、链接字符串、模式与路径/暂存关系；普通文本补丁不足以涵盖这些保证。

**修改与绑定。** Builder 修改上述虚构配置并创建新文件，修改结果绑定本轮版本。任务 A 的恢复用途和任务 B 的复核用途可以引用同一份可靠内容，各自仍记录来源、用途、绑定版本和评审关系；存储不放在可能随任务 A 清理的临时目录。若现有门禁要求实体文件，仍在合规工作区实体化并核对，不将 Git 对象字符串写入实体路径字段。冻结 expected 仍绑定旧输入，不随 Builder 新内容改变；旧历史包、摘要和 receipt 不被重新解释。

**同一 Reviewer 第二轮。** Reviewer 已有有效首轮基线时，先确认目标、authority、claim ceiling 和关键依赖，再按前述 snapshot/Delta Read Set 读取本轮改动、受影响调用链、未解决问题及最终状态；必要域缺口触发扩读。保全文件不必重新复制或全文输出。命中前述任一 rebaseline trigger 就重新建立相应完整基础；指纹未变也要做语义刷新，不能由工具摘要推导“无需阅读”。

**新独立 Reviewer 接手。** 新 Reviewer 没有原 Reviewer 的理解基础，读取原始要求、合同/AC、有效基线、实际 diff、必要源材料与最终状态，建立足够的独立阅读基础。可以复用已保全的内容和可验证引用，但不能仅接收“hash没变”或前任结论就声称独立通过。读取范围仍由职责与影响决定，并非机械全读所有历史目录。

**隔离恢复核对。** 在同一临时实验仓库恢复 clean.txt 原始字节；恢复 dirty.txt 的用户工作区内容；恢复 partial.txt 的 index=2、worktree=3，分别比较 cached/unstaged diff；恢复未跟踪与受影响忽略原件；移除实验新建的 new.txt 以恢复 absent。核对特殊文件字节、链接、0755和重命名暂存关系。另以缺对象、错误摘要和真实 CRLF checkout 转换尝试固定引用，均先拒绝可恢复声明，再从预先保全原件恢复并核对 LF 字节。任何环境、fixture、导入或路径故障均记 error（无法判定），不能当可信 RED 或成功恢复；固定案例成功也只支持合成样本，不证明产品验收或通用自动恢复。

这个故事的检查点是状态和阅读责任都不丢：内容在磁盘保全、工具只出摘要、Reviewer读取必要材料是三个分别决定的动作。它不承诺 token、费用或时间收益，不启动对象库、历史清理、安装或发布任务。
