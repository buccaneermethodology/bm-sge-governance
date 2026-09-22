# Design、Builder 与 ERBE recipe

1. C0 后、dominant Builder 前保存 Design artifact：authority、目标/非目标、模块/API/schema、实现 slices、tests/gates、风险、handoff 与 delta policy。
2. 需要 ERBE 时冻结 Contract/Cases 并确认可信 RED；Builder write scope 排除 frozen assets。
3. 每个 non-trivial lane 先 validate card digest，再 render prompt；接收端复验 digest。
4. Builder 按依赖顺序实现最小安全切片；分类器、preflight、lifecycle 与 receipt 保持单一责任。
5. 每项 finding 独立记录 disposition、root cause、implementation、focused verification、prevention、residual risk 与 terminal candidate。
6. 运行 same-identity GREEN、focused/negative/regression、KB render、BDD/public gates；只声明 Builder candidate，不自报独立 Validation。

卡片字段或重复审计细则扩读 `../context-efficient-goal-validation.md`。
