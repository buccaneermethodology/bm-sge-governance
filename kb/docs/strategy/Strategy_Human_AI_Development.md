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

## 实现变更追溯与验收边界

所有 Goal closeout 必须声明 Implementation Delta 适用性。按实际行为影响判断：runtime、工具、配置、脚本、schema、Provider 路由等改变行为均适用，不能按扩展名豁免。适用时使用中文标题“实现变更（Implementation Delta）”，按可独立解释和验证的变更项记录。纯文档或导航可标 not_applicable（不适用），但必须说明未发生代码行为变化的依据；其他治理审查仍须执行。

每项必须包含六字段：①模块与行为：链接实际源文件，解释前后行为，不能只有文件清单；②Git 与定位：所属仓库、已提交部分对应提交，未提交部分明确标注并链接基线、固定快照与文件清单；③验证证据：逐项关联实际测试结果、运行收据或独立审查，并说明支持范围，未运行、失败、缺失与失效如实记录；④目标影响：关联原 Goal must-have/AC 编号并解释如何支持目标，提交不是达成；⑤未覆盖边界：剩余缺口、未验证场景与 claim ceiling，无已知缺口也限定适用范围；⑥独立性：区分提交、Builder 自检、测试与独立验收，链接独立 verdict 或明确尚无。

未提交验收允许固定快照。快照须可重建：固定基线提交、tracked/untracked 文件清单、新增/删除/重命名清单及内容；可用基线加完整 tracked patch、untracked 原文和 manifest。删除须定位基线内容，重命名保留 old/new 路径与实际内容。仅路径、摘要或遗漏新增文件的 diff 不足以定位验收对象。混合状态分别标明已提交与未提交部分，不得混称已提交。

验收对象变化后不得自动沿用原证据；更新快照或重新绑定，说明哪些测试/审查仍适用、哪些须重跑或重审。多 Session Goal 最终 closeout 汇总实际实现变化、目标影响、剩余缺口和最终对象证据，可复用子 Session 证据，不能仅列子 closeout 链接。

Reviewer 从 closeout 本文应能说明变化、影响、缺口和声明上限，再通过可点击 Markdown 源链接核查。表格完整不等于通过，Git 提交、自检和测试通过不能替代独立验收。Validation Handoff 必须携带适用性依据、六字段、定位快照、证据绑定及父面汇总，供独立 reviewer 对原始目标与最终对象核验。

本规则采用清单加独立审查；现有 closeout 提示输出仅提醒，不自动检测遗漏，closeout-language 只检查既有语言约束。不得将模板、示例、打印成功或语言检查当作 Implementation Delta 结构或语义通过。规则适用于采用该版本的后续 closeout；仓库落地不证明其他项目已经采用。

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
