# Intake 与首任务 recipe

1. 保存 Raw User Intent authority；判断目标、source authority、repo/KB/Dashboard 边界、风险、缺失信息与执行路线。
2. 使用 `first_task_router.py` 区分 trivial read-only、governed implementation/validation 与 Goal missing/existing/conflict。
3. 构造 read_only、implementation 或 validation Context Bootstrap，验证 required/conditional reads、semantic refresh、epistemic domains、impact 与 topology。
4. Goal missing 时先冻结 Goal；conflict 时请求人类 authority；只有 Goal existing 且合同 ready 才进入相应 lane。
5. optional capability 缺失时运行 core fallback，不静默安装或升级声明。
6. 进入 Builder、install、upgrade、release 或 deploy 前，物化并验证 execution admission；未绑定 Goal、Contract、Context、Design/Review 或 topology 时不得开始副作用。

输出：Intake verdict、Context packet identity、route、claim ceiling、下一 gate。模板或复杂 trigger 扩读 `../checklists.md`。
