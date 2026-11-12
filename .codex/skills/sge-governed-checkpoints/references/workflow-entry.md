# 统一执行入口操作说明

入口把既有任务定义、lane card、Context、admission、现态和审查工具串起来。它不新增任务 authority，不生成批准，不认证宿主 reviewer 身份，不替代 Stop Gate。

## 日常使用

准备或委派新 lane 时先从现有任务合同选 JSON Pointer，制作一次 `workflow_spec_v1` 引用配置，运行 `scripts/workflow_entry.py prepare`；派发只用生成的 `prompt.md`。恢复时运行 `resume`，按来源观测、未关闭 finding、层级、快照比较和工作依赖决定下一动作。执行包过期时重新基线并使用新的输出目录，不覆盖历史包。

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_entry.py prepare --repo /absolute/project --spec task/spec.json --out task/package
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_entry.py check --repo /absolute/project --bundle task/package
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_entry.py run --repo /absolute/project --bundle task/package --command focused --checkpoint pre_validation --action check --target task-id
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_entry.py resume --repo /absolute/project --bundle task/package
```

`--repo` 必须绝对，其余路径与命令 cwd 必须相对该根；从任何调用目录都相同。API 为 `execute(request: dict) -> dict`，操作和 CLI 同名。`pass` 只表示该入口操作成功，`blocked` 携带稳定 fingerprint；CLI 分别返回 0/非零。

## 引用配置

`schemas/workflow_spec_v1.schema.json` 描述输入。`task_source={path,pointer}` 指向既有任务对象：task_id/session_id/acceptance_criteria_ids/write_scope/required_outputs/maximum_claim。它不是在 manifest 新建一份批准。card_template、context、topology 指向对应旧格式文件；写命令另需既有 approved admission。

`bindings=[{path,serialization,role}]` 使用 `raw_bytes` 或规范化 `canonical_json`；JSON 排版变化只对后者无影响。role=background 才允许无关追加；相关合同、源码、Goal、治理和拓扑必须绑定。工具自动绑定 task_source、card 所有引用、Context 本地存在且适用的 Required Reads、admission 全部引用和命令中的本地脚本，不能靠漏填 bindings 运行陈旧源码。外部阅读索引仍需人工依 Context 读取，不作为工具已经读懂的证据。

`commands` 为名称映射，字段为 argv 数组、cwd、action、target、checkpoint、mutating。`{python}` 替换当前解释器；shell=False，无 shell 插值。合法组合只有 check/false 或 builder、install、upgrade、release、deploy/true。只读声明仍由配置作者及独立审查负责，不是自动副作用检测。写动作运行前重新消费 `scripts/execution_admission.py`。

prepare 使用 `scripts/lane_task_card.py` 原 validator/renderer 与 `scripts/context_bootstrap.py` 原 validator；stage 完整封包后原子发布。输出包含 spec.json、原格式 card.json、prompt.md、manifest.json、seal.json、inputs。相同输入重复调用保持字节不变；冲突不覆盖；并发忙返回 PREPARE_BUSY。崩溃残留 stage/lock 不可派发；确认没有活跃 prepare 后由操作者保存证据并清理锁，再重试。seal 校验防止无意修改和普通篡改，不提供抵御有权整体重写包与 seal 的攻击者的签名认证。

## 现态恢复与来源支持

本次任务使用 state_sources 指向既有 task-bound 状态：findings/work_units/review_budget 为 `{path,pointer,expected_task_id}`，每次 resume 重读；snapshot 含 baseline/current 两 ref 和 delta_read_set。baseline 自动冻结，current 重读。源根对象 task_id 必须匹配当前任务；缺失或身份错配为 unknown，不回退 spec 旧数组，不释放任何 ready 工作。旧静态包兼容嵌入 findings/work_units/review_budget。

快照使用 `scripts/context_state.py` 的 compare_snapshots，结果原样传出。预算使用 `scripts/review_budget_preflight.py` 的 evaluate_budget；不能证明 caller 提供了完整宿主历史。Stop Gate 可以作为预声明检查命令调用 `scripts/stop_gate.py`，固定 authority-root 与摘要仍由调用方提供，入口不生成或选择可信根。

finding 保留 assertion、精确 source 行段/quote、observation、impact、producer 与 confirmation_ref。`closed` 是原来源生命周期，保持关闭且不列 confirmed_blocker；pending/needs_evidence/needs_review/unsupported/confirmed 是当前支持判断。行段匹配只证明定位；只有绑定断言/来源摘要且 reviewer 不等于 producer 的已有 supported 记录才列 confirmed_blocker，语义正确性及真实独立性仍由独立 lane 检查。C44 一类本地确认形状不证明业务断言。

reviews 指向已有独立结论索引：task_id/layer/verdict/reviewer/producer/round/bindings。四层 design/implementation/integration/independent_validation 独立显示 unknown/valid/stale。bindings 当前摘要不符则 stale，保留 round 并要求 rebaseline；不从代码文件存在倒推通过。

work_units 保留 id、ac_ids、depends_on、releases_dependency、observable_result、state、evidence。done 必须当前证据存在且类型化摘要匹配才能释放后继；这仍不是用户 AC 独立验收。连续两个 no_progress 且无新证据时要求 diagnose_no_progress，不擅自缩小目标或暂停。resume 不自动派发新 lane、不重置审查预算、不写回源状态。

## 结果与边界

run 的 argv/stdout/stderr/returncode/checkpoint/action/target 收据写在包外新路径；命令失败即返回 blocked，不串行继续下一命令。resume 的 pass 表示恢复计算成功；还要看 runnable 和 unknown/stale/next_action。没有宿主 hook 时，仅保证入口内检查，不能保证 Agent 无法绕开入口。完整独立审查、KB/Dashboard 收口和 Stop Gate 保持原职责。
