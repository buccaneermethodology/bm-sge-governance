# Strategy Human AI Development

_Owner: sge-governance-core | Version: v1.0 | Status: active | Updated: 2026-09-02_

## 范式与权威边界

SGE 交付以用户原始意图和冻结合同为起点，以 kb/data 中的稳定 truth、Dashboard 中的执行记忆和独立验证证据分层协作。结构、schema、渲染、测试、验证、批准、Git、发布和生产状态是不同轴。

- 先冻结可观察判定，再开始高语义风险实现。
- Dashboard 不覆盖 canonical KB；派生投影不反向成为 authority。
- 任何 scope 删除、替换、降级或延期都必须显式记录 Scope Delta。

## 人、Agent 与确定性工具的职责

| 角色 | 负责 | 不得替代 |
| --- | --- | --- |
| Human authority | 目标、关键取舍、批准和 destructive/public 决定 | 机器 gate |
| Builder | 在冻结 write scope 内实现 | 独立 Validation 或修改 frozen cases |
| Validation/Semantic reviewer | 从 durable inputs 重算验收与语义边界 | producer 自报终态 |
| Deterministic tool | 结构、schema、diff、引用和失败指纹 | semantic oracle |
| LLM runner | 有授权的外部观察 | canonical truth 或人类批准 |

## Intake、Context 与 Goal 完整性

- [ ] 保留 Raw User Intent 为 authority，Intake 只作 projection。
- [ ] Context Bootstrap 覆盖 authority、claim ceiling、critical dependencies 与 epistemic search space。
- [ ] 原始 must-have、流程条款、OPCM 与 Scope Delta 同时进入 Validation Handoff。
- [ ] 只验证修订设计不能支撑原始 Goal 完成。

## 多角色协作与交接

非平凡工作按 change impact 启动必要 lanes。授权必须来自当前用户、仓库或有效 Goal，不能从来源项目继承。

- delegation 使用 digest-bound lane card 和最小 Delta Read Set。
- 独立 reviewer 读取实际产物和最终 diff；日志记录可见事件，不导出私有推理。
- 同一执行体切换角色时必须声明并保留 independence exception。

## 验证与关闭

- schema-valid、trial pass 或 producer status 不等于 semantic acceptance。
- Validation Handoff 说明任务声称什么、不证明什么、证据层和已知风险。
- 最终 closeout 使用中文解释英文 verdict/status 的含义、影响、边界和下一步。
- 只有 completion rule 的全部谓词同时成立，才允许 done/complete。

## 自动化边界

自动化只能在合同、authority routing、失败指纹和恢复边界冻结后扩大。自动化 runner 证明执行行为，不自动证明语义正确、公共就绪或生产成熟。

## Claim Ceiling

本策略只定义 repo-local Human-AI 治理协作的稳定边界；不启用产品 runtime、provider、公共发布、数值评分或普遍适用性主张。

## Source Scope

- `AGENTS.md`
- `.codex/skills/sge-governed-checkpoints/SKILL.md`
- `Dashboard/Rules.md`
- `Dashboard/Methodology.md`
- `Dashboard/Artifacts/Stage-Plan-SP-001/SP001_S013_SourceAdjudication.md`
- `kb/data/strategy/sge_strategy_source_manifest_v1.json`
