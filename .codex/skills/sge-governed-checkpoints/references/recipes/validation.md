# 独立 Validation recipe

1. 保持 read-mostly；先建完整 Read Manifest，覆盖 Raw Prompt、Final Goal、original ledger/OPCM、Scope Delta、Design/implementation、closeout、logs、KB、Dashboard、tests 与完整 diff。
2. 用中文先说明任务做什么、声称什么、不证明什么与主要风险。
3. 从 durable inputs 重算 schema、case identity、digest、gates、final-state binding 与 claim ceiling；不可相信 producer 自报。
4. 分开 blocking、non-blocking、questions、Builder repair 与 verdict。当前合同外 hardening 记 follow-on。
5. 缺必读证据、OPCM、Scope Delta audit、Validation Handoff 或 language verdict 时只可 blocked/partial。
6. final pass 必须绑定实际 closeout、最终 KB/Dashboard、full diff 与 post-closeout reconciliation，且 reviewer/source 唯一无冲突。

固定 reviewer prompt、输出模板与 semantic taxonomy 扩读 `../checklists.md`。
