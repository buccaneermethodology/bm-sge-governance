# Stop Gate 连续执行策略

_Owner: SGE governance | Version: 1.0.0 | Status: active | Updated: 2026-09-22_

## 判定与无效状态

- 有效 verdict 只有 CONTINUE、PAUSE_ALLOWED、GOAL_COMPLETE。CONTINUE 必须继续；PAUSE_ALLOWED 只允许真正的权限决策或阻断请求；只有 GOAL_COMPLETE 允许最终六问收口。
- 无效、缺字段或矛盾状态必须非零退出，receipt_status=invalid、verdict=null、final_allowed=false、PROGRESS_ONLY、REBUILD_STATE；状态缺失本身不是暂停理由。

## 授权与完成谓词

- 调用方通过独立配置显式固定 Goal authority root 及摘要，root 精确绑定 Goal、原始 completion rule、有限谓词和 issuer。state producer 不能自选平行 root；helper 不得生成或发现可信 root。
- 有限 DSL 支持 all_of 与剩余 must-have 为空、无未批准 Scope Delta、指定工作单元终态、无待裁定权限、必需证据已绑定。禁止 producer 自报 completion boolean。
- 已有 approval 必须重算 authority 文件摘要并精确比较结构化 scope、subjects、有效时间；N/A 证据必须关联覆盖对应要求的有效授权。协议仍依赖真实调用方的信任配置和独立审查，摘要自洽不等于业务事实正确。

## 连续执行与恢复

- Milestone、Session closeout、恢复与 final 前调用唯一核心 scripts/stop_gate.py。Session 类型或粒度变化不能使父 Goal 提前终止。
- 下一工作已就绪且仍有 must-have 时推进工作，不提前要求最终证据；下一入口未创建则 MATERIALIZE_NEXT_ENTRY；可修复失败 REPAIR；瞬时网络或工具失败 RETRY_RECOVERY。
- 相同网络或工具故障 fingerprint 连续达到默认 3 次才可暂停。普通测试失败、最后报告语言、实现偏好、回合长度、已覆盖授权都不是新的暂停权限。

## 证据与宿主边界

- 最终证据包含 Goal、原始规则、obligation inventory、最终 diff、独立 Validation、closeout、Dashboard、KB disposition、OPCM、Scope Delta audit、post-closeout reconciliation。
- 保存符合 stop_gate_receipt_v1 的 receipt，记录输入状态摘要、引用文件及重算 digest、时间、Gate 版本。final 前重新运行；任一输入或引用变化后旧 receipt 失效。
- 无宿主 pre-final hook 时，只能声明可审计、fail-closed 协议。自动强制要求宿主在实际 final-response 入口验证最新 receipt；Skill 脚本本身不能绝对拦截模型发言。

## Source Scope

- `通`
- `用`
- ` `
- `G`
- `o`
- `a`
- `l`
- ` `
- `连`
- `续`
- `执`
- `行`
- `与`
- `证`
- `据`
- `绑`
- `定`
- `合`
- `同`

## Related Docs

- `sge-strategy-sgc-structural-contract-v1`
