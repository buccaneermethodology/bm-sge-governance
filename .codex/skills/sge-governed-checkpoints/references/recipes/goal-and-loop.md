# Goal 与 Loop recipe

1. 建立 Read Manifest：用户/附件、AGENTS、相关 KB/Dashboard、AC、历史 design/closeout；列 missing/skipped/stale risk。
2. 冻结中文任务解释、scope/non-goal/risk、must-have ledger、AC mapping、authority、claim ceiling、termination。
3. 适用时先完成 ERBE Contract/Cases 与 trusted RED，再做 pre-Builder Semantic Review。
4. review 后使用 Goal Patch；Builder 只接收 base + patches 确定性解析的 Final Goal。
5. 保存 Session DAG 与 continuation contract。在每个 Milestone、Session closeout、恢复与 final 前调用 `scripts/stop_gate.py`，保存 durable receipt；未终止且 ready 时自动继续。
6. final Validation 同时覆盖 original objective、实际 closeout、最终 KB/Dashboard 与完整 diff。

Goal Patch、OPCM、duplication 或 snapshot 细则扩读 `../context-efficient-goal-validation.md`。

## Stop Gate 执行合同

输入遵守 `schemas/loop_state_v1.schema.json`；输出遵守 `schemas/stop_gate_receipt_v1.schema.json`。调用方管理 Goal authority root，显式传入 root 路径、source root 和预先固定的 SHA-256。state producer 不能自行替换可信 root。helper 只委托核心，不能保留平行终态判断。

- `CONTINUE`：一行进度，执行 DISPATCH_NEXT_WORK、MATERIALIZE_NEXT_ENTRY、REPAIR、RETRY_RECOVERY 或 COMPLETE_FINAL_EVIDENCE；不得发送最终答复。
- `PAUSE_ALLOWED`：只请求真正的人类决策或报告已达恢复阈值的阻断；已授权事项不重复询问。
- `GOAL_COMPLETE`：原始完成谓词、must-have、独立 Validation、closeout、Dashboard/KB、最终 diff 等证据全部绑定后，引用 receipt 并使用最终六问。
- 无效状态：非零退出，receipt_status=invalid、verdict=null、final_allowed=false、PROGRESS_ONLY、REBUILD_STATE；自动修复重试，不转为暂停。相同恢复故障达到阈值后才可按真实恢复记录申请暂停，默认 3 次。

中间工作尚有 must-have 时，不要求预造最终证据。下一入口缺失由 Orchestrator 创建。最终报告的语言和格式不是人类权限 checkpoint。普通测试失败继续修复；单次网络/工具中断先自动恢复。

final 前重新评估当前输入与所有引用文件，任何状态或文件变化都使旧 receipt 失效。没有宿主 pre-final hook 时只提供协议和审计证据，不能声称绝对阻止模型 final。
