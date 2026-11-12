# Design、Builder 与 ERBE recipe

1. C0 后、dominant Builder 前保存 Design artifact：authority、目标/非目标、模块/API/schema、实现 slices、tests/gates、风险、handoff 与 delta policy。
2. 需要 ERBE 时冻结 Contract/Cases 并确认可信 RED；Builder write scope 排除 frozen assets。Builder 提交前为每条合同声明列正例与最小反例，覆盖分母由合同决定。
3. 每个 non-trivial lane 先 validate card digest，再 render prompt；接收端复验 digest。
4. Builder 按依赖顺序实现最小安全切片；分类器、preflight、lifecycle 与 receipt 保持单一责任。
5. 每项 finding 独立记录 disposition、root cause、implementation、focused verification、prevention、residual risk 与 terminal candidate。
6. 运行 same-identity GREEN、focused/negative/regression、KB render、BDD/public gates；只声明 Builder candidate，不自报独立 Validation。
7. Builder start 必须携带已验证的 `execution_admission_v1`；admission 不是 Stop Gate terminal receipt 的替代品。
8. 修复同类问题时穷举整个声明 family，例如字段增删全集及 resource/component/revision 的合法相等、合法不等、一侧非法、两侧非法组合；finding 要指明扩散检查全集。

卡片字段或重复审计细则扩读 `../context-efficient-goal-validation.md`。

编写、协作或复核 AC、用户/系统 G-W-T 或 ERBE cases 时，读取 [用户视角验收条件与案例质量操作参考](../user-oriented-acceptance-case-quality.md)，按原始 AC 映射与六项视角检查，并把隐藏需求作为 Scope Delta 候选反馈主 Agent。

Design与任务卡按[行为进度模板](../behavior-progress-template.md)引用当前相关对象/连接ID、AC pointer及来源，不复制全段G-W-T。Builder交接记录任务贡献前后、证据、剩余缺口/下一步，并分别报告能力来源与连接验证；任务完成不能升级场景。

任务会修改、删除或覆盖受影响文件时，先按需读取 [按文件状态保全与增量复核](../context-efficient-goal-validation.md#按文件状态保全与增量复核)，选择可靠固定引用或必要原件，并区分提交、暂存区、工作区及不存在状态；完整操作表不进入 kernel。
