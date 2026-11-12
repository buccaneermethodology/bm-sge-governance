# 独立 Validation recipe

1. 保持 read-mostly；先建完整 Read Manifest，覆盖 Raw Prompt、Final Goal、original ledger/OPCM、Scope Delta、Design/implementation、closeout、logs、KB、Dashboard、tests 与完整 diff。
2. 用中文先说明任务做什么、声称什么、不证明什么与主要风险。
3. 从 durable inputs 重算 schema、case identity、digest、gates、final-state binding 与 claim ceiling；不可相信 producer 自报。
4. 在首个阻断后继续完成全部预声明维度；报告全部 findings、已检查无问题的维度及证据、未检查维度及原因/准入影响、当前输入中的同类残余与有条件的修复后准入预测。
5. 分开 blocking、non-blocking、questions、Builder repair 与 verdict。当前合同外 hardening 记 follow-on；不改变 oracle、状态码、拒绝优先级、allow/deny、数据写入或权限语义的整理项可记 `non-blocking cleanup`。
6. 缺必读证据、OPCM、Scope Delta audit、Validation Handoff 或 language verdict 时只可 blocked/partial。
7. final pass 必须绑定实际 closeout、最终 KB/Dashboard、full diff 与 post-closeout reconciliation，且 reviewer/source 唯一无冲突。

固定 reviewer prompt、输出模板与 semantic taxonomy 扩读 `../checklists.md`。

编写、协作或复核 AC、用户/系统 G-W-T 或 ERBE cases 时，读取 [用户视角验收条件与案例质量操作参考](../user-oriented-acceptance-case-quality.md)，按原始 AC 映射与六项视角检查，并把隐藏需求作为 Scope Delta 候选反馈主 Agent。

按[行为进度模板](../behavior-progress-template.md)人工核对原始义务/AC、四对象关联、关键连接、分层状态、版本有效性与独立性；用户/Agent两视图必须同底表/时间/revision/证据。逐情境记录实际使用行、观察、判定理由，尤其未知、零贡献、回退及保存重开两分支；表格/生成一致不替代独立语义Review。
