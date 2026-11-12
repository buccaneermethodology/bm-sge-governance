# 用户视角验收条件与案例质量操作参考

编写、协作或复核 AC、用户/系统 G-W-T、ERBE cases 时读取本页。规范与教学正反例保存在 发行 source 仓的唯一 canonical `kb/data/strategy/strategy_user_oriented_acceptance_case_quality_v1.json`；此处阅读 [完整只读方法投影](readers/user-oriented-acceptance-case-quality.md)，并核对 [来源记录](readers/projection-sources.json)。本页只提供路由，不另复制一份规范。

1. 先读原始意图、AC 与批准 authority，保留原分母、claim ceiling 和 frozen write exclusions。
2. 按方法页六项视角改写：操作者目标、贯穿例子、术语因果、用户结果/系统保障、观察点、期望/现状。无需每张卡套六段。
3. 沿原 AC → 用户情境 → 系统规则 → 正例/最小反例/边界 → oracle/evidence 映射；具体教学链见“北京+最近7天”示例。未知 oracle 不可填成拒绝或通过。
4. 积极发现隐藏需求，区分澄清、新增、冲突、待决，反馈主 Agent 并记录 owner/disposition；Scope Delta candidate 不等于批准。保存重开与失败回滚的示范见方法页。
5. Validation 分别检查表达可理解性、原 AC 覆盖、真实 oracle 与证据层；执行判定仍走现有 ERBE。教学例子不证明 DataEase 行为，结构检查不证明用户可用性或模型普遍质量。

行为分解与中间进度按方法页新增六项规则执行；使用[双视图模板](behavior-progress-template.md)按比例复用OPCM/Session/Implementation Delta。四对象、多对多、连接、贡献与证据版本保持可追溯；教学状态不代表产品事实或当前Goal进度。
