# Closeout、KB/Dashboard 与 BDD recipe

1. 写中文 closeout：落地范围、非目标、lanes/例外、Design/Validation handoff、verdict、证据、gates、Semantic、延后范围、KB/Dashboard 与 next candidate。
2. 证据正文使用可点击 Markdown 源文件链接；hash 留给 machine artifact，不作为唯一人类入口。
3. 运行 closeout-language；H1/H2 中文且英文状态有中文解释。
4. stable rule 做 Contract Delta Scan 并落 canonical KB JSON；state/decision/blocker/closeout/follow-on 落 Dashboard。
5. maintained behavior gate 变化同步 BDD；reader cards 写入受版本控制路径。
6. 更新 Session registry 后运行 reconcile check 与 validate；可重建 drift 才 apply 后复验。
7. final-state Validation 与 post-closeout reconciliation 后再决定 terminal；随后执行 next-session scan。

closeout、handoff、Dashboard Agent 模板扩读 `../checklists.md`。

## 实现变更追溯

所有 Goal closeout 先声明 Implementation Delta 适用性；按实际行为判断，配置/脚本/schema/Provider 路由不得按后缀豁免。适用时用“实现变更（Implementation Delta）”，逐项写模块前后行为、仓库与提交/快照、真实验证证据、原 Goal/AC 影响、未覆盖边界、独立验收状态。纯文档/导航不适用须解释无行为变化，其他治理仍执行。

使用 [实现变更模板](../implementation-delta-template.md) 和 [正反例](../implementation-delta-examples.md)，按 [详细人工清单](../checklists.md#实现变更人工核验清单) 核查。未提交快照须保留基线及 tracked/untracked、新增/删除/重命名的清单和内容；混合状态分列。对象改变需更新快照或重新绑定证据，多 Session 父面汇总变化/目标/缺口/最终证据，不只列子链接。表格、自检、测试、提交和提醒均不代替独立验收。
