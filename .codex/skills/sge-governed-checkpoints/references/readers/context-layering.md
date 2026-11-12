> 本文件是随 Skill 分发的只读阅读投影，唯一 canonical 规范仍位于发行 source 仓的 kb/data/。不得直接编辑本投影或将其作为目标项目的独立真源；项目既有 authority 不由此变更。来源与精确派生映射见 [来源记录](projection-sources.json)。

# Strategy: Context layering and measurement v1

_Owner: SGE governance | Version: 1.1.0 | Status: active | Updated: 2026-11-10_

## Three context layers

- The kernel retains triggers, invariants, hard stops, authority, claim, truth split, and continuation rules.
- Task recipes contain the short executable sequence, required outputs, and gates for the selected task.
- Detailed references contain explanations, templates, taxonomy, and special cases and are read only after deterministic or evidence-backed expansion triggers.
- Unknown or conflicting triggers expand reads or rebaseline; they never silently omit required domains.

## Measurement law

- Measure every frozen fixture three times using UTF-8 bytes, default and conditional reads, repeated blocks, and G01 through G12 coverage.
- Coverage validates structural kernel rows, trigger/applicability terms, reachable executable recipes, fallback identity, dangling routes, and default-read cycles; labels alone are not coverage.
- Material improvement requires bytes or reads to decrease beyond noise, conditional rereads not to fully rebound, and exact coverage preservation.
- Bytes divided by four is a derived comparison metric, never provider token usage, billing, or universal cost evidence.

## 按状态保全与按职责复核

- 保全确保受影响文件写前状态可恢复；工具输出决定哪些内容进入上下文；评审阅读由有效基线、变更影响和评审责任决定。可靠保存不等于默认全文输出或每轮重读，复制字节不等于实际 token 用量。
- 按文件状态选择方式：干净已提交内容可复用可靠固定版本；未提交内容分别保全提交、暂存区与工作区状态，部分暂存不能合并成 dirty 标记；未跟踪和受影响忽略文件保存必要原件，新文件记录原先不存在；特殊文件保留类型、权限、路径关系等恢复元数据。
- 可靠固定引用必须身份固定、在明确的保留与交付环境可取回、原始字节校验一致，并具备恢复所需对象、元数据及外部依赖；提交号或摘要本身不足以保证恢复。引用失效、内容不符、字节转换或依赖不足时，先保存必要原件，不依赖未经证明的引用。
- 内容可复用，各任务仍分别保留来源、用途、绑定版本及评审关系，且不得依赖可能随其他任务清理的临时材料。现有合同要求独立实体文件或工作区内路径时继续提供，不把 Git 对象写入文件路径字段，不借外部共享目录绕过限制。
- 同一 Reviewer 后续复核沿用现有 snapshot、Delta Read Set 与 rebaseline 协议；新接手的独立 Reviewer 必须建立足够阅读基础。指纹相同不替代语义刷新或独立判断，不缩减必要认知域和既有门禁。
- 冻结输入和历史证据保持原版本绑定；不因当前内容相同、路径同名或轻量化而自动改写历史路径、摘要、评审与 receipt。操作表、恢复边界及贯穿示例按需读取 checkpoint 详细参考中的“按文件状态保全与增量复核”，不在 kernel 展开。

## Source Scope

- `AGENTS.md`
- `.codex/skills/sge-governed-checkpoints/SKILL.md`
- `.codex/skills/sge-governed-checkpoints/references/context-routing-manifest-v1.json`
- `.codex/skills/sge-governed-checkpoints/references/context-efficient-goal-validation.md`
- `.codex/skills/sge-governed-checkpoints/references/recipes/design-and-builder.md`
