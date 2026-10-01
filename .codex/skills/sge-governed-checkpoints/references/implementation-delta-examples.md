# 实现变更正反例

以下全部是教学示意，仓库、提交、路径、测试结果和 reviewer 均为虚构，不是本仓库执行证据。示意链接用 example.invalid 明确隔离；实际 closeout 必须替换为可定位、可读取的真实对象。本页展示人工 rubric，不提供自动检测器。

## 已提交实现示例

Implementation Delta: applicable（适用），工具参数行为改变。

| 字段 | 教学示意内容 |
| --- | --- |
| 模块与前后行为 | 工具 [parse.py](https://example.invalid/demo/parse.py) 之前接受负数重试次数，现在返回参数错误并退出码 2。 |
| 仓库与变更定位 | 仓库 demo/parser；全部已提交于 [提交 A](https://example.invalid/demo/commit/A)，基线为提交 B，无本项未提交内容。 |
| 验证证据 | [参数测试记录](https://example.invalid/demo/results/args) 显示负数被拒、零和正数仍可用；[运行收据](https://example.invalid/demo/receipt) 对应提交 A，仅覆盖本地 CLI。 |
| 原始目标影响 | 支持 [Goal MH-1/AC-2](https://example.invalid/demo/goal)：阻止无效重试值，同时保留合法值兼容性；提交自身不证明该目标达成。 |
| 未覆盖边界 | 未验证第三方 shell 包装器；结论限 CLI 参数解析，不证明网络重试正确性。 |
| 独立性与验收 | 提交记录定位源码；Builder 自检是生产者检查；测试记录是执行证据；独立 reviewer 甲的 [bounded pass](https://example.invalid/demo/review) 只接受上述 CLI 范围。 |

此正例展示六字段齐全且证据分层；独立审查仍需真实读取相应对象，不能因示例格式合格而直接通过实际任务。

## 未提交与混合实现示例

Implementation Delta: applicable（适用）。同一工具的退出码修复已提交，新增 Provider 超时路由尚未提交。

| 字段 | 教学示意内容 |
| --- | --- |
| 模块与前后行为 | [parse.py](https://example.invalid/demo/parse.py) 将非法参数从退出码 0 改为 2；未提交的 [route.py](https://example.invalid/demo/route.py) 将超时从无限等待改为返回 timeout，不扩大 Provider 支持范围。 |
| 仓库与变更定位 | demo/parser 的退出码修复在 [提交 A](https://example.invalid/demo/commit/A)；路由为明确未提交。固定基线 A 加 [tracked.patch](https://example.invalid/demo/snapshot/tracked.patch)、[untracked 原文包](https://example.invalid/demo/snapshot/untracked.tar)、[完整 manifest](https://example.invalid/demo/snapshot/manifest.json) 重建快照 S1。 |
| 验证证据 | [S1 测试记录](https://example.invalid/demo/results/S1) 覆盖合法参数、超时和正常返回；真实 Provider 调用未运行；测试使用模拟输入，不能证明线上 Provider 正确性。 |
| 原始目标影响 | 支持 [MH-1/AC-2、MH-3/AC-4](https://example.invalid/demo/goal) 的退出码和有限等待要求，尚不支持生产 Provider 验收。 |
| 未覆盖边界 | 未验证实际凭证、网络抖动与生产负载；声明上限为固定 S1 的本地分支行为。 |
| 独立性与验收 | A 是提交，S1 是未提交快照；Builder 自检与测试不是独立验收。reviewer 乙的 [S1 有界 verdict](https://example.invalid/demo/review/S1) 可接受未提交对象，但不称其已提交或生产通过。 |

逐项绑定：退出码变更对应参数测试与 MH-1/AC-2；超时路由对应模拟超时/正常返回测试与 MH-3/AC-4，S1 verdict 分别限定这两项本地行为。

S1 manifest 相对基线 A 具体列明：parse.py 的退出码修复已在提交 A，S1 不再修改该文件；tracked 删除 legacy.py（原文在基线 A）；tracked 重命名并修改 old_route.py → route.py（作为一个 rename-with-edit 条目保留 old/new 路径、基线原文和带超时逻辑的新内容，不重复列为普通修改）；untracked 新增 timeout_fixture.json（原文在包中）。manifest 同时包含每项状态、来源和内容位置；无其他新增文件。以上条目为示意，实际清单须从当时工作区完整获取，不能照抄。

验收后若把 timeout 从 30 秒改成 10 秒，S1 verdict 不自动覆盖；冻结 S2，重新关联行为变化并运行受影响测试，由 reviewer 对 S2 重审。纯未提交情况使用相同方式，已提交部分写“本项无已提交变化；仅基线为 A”。

## 纯文档与导航示例

Implementation Delta: not_applicable（不适用）。本次仅纠正术语页的错别字和导航链接；未改变 runtime、工具输出、配置、schema、Provider 路由或可执行指令。差异见[文档 diff](https://example.invalid/demo/docs-diff)。因此无代码行为项；文档正确性、原目标覆盖、独立审查及其他治理仍需按合同核验，不因不适用而直接 Goal complete。

如果修改的是路由 YAML 的 timeout 值或工具打印内容，即使主要文件是文档/配置也有行为影响，不能套用本例。

## 缺项与证据错配反例

以下每行是独立反例，人工 reviewer 均应判为不满足合同，并要求修正；不能只看是否存在表格。

| 反例 | 判定理由与所需修正 |
| --- | --- |
| 实际还改了 Provider 路由，但只记录工具模块 | 遗漏整个实现项/模块；补路由前后行为与对应六字段。 |
| 删除模块与行为字段，只剩文件名 | MH-1 缺失；补模块、实际源链接及前后行为。 |
| 删除仓库/提交/快照字段 | MH-2 缺失；无法定位验收对象，补可重建定位。 |
| 删除验证证据字段 | MH-3 缺失；补真实结果及支持范围，缺证据须明示。 |
| 删除目标影响字段 | MH-4 缺失；补原 Goal/AC 关联及因果解释。 |
| 删除未覆盖边界字段 | MH-5 缺失；补缺口/未验证场景/claim ceiling，不能以“全部完成”替代。 |
| 删除独立性字段 | MH-6 缺失；分别说明提交、自检、测试与独立 verdict，暂无须明说。 |
| 未提交快照仅有文件路径/hash，或 git diff 漏了 untracked 新文件 | 无法重建完整对象；补基线、tracked patch、untracked 原文、新增删除重命名清单和内容。 |
| 混合状态全写“已经提交” | 来源状态错误；逐项区分已提交与未提交部分。 |
| S2 修改了行为却继续引用 S1 通过 | 证据错配/失效；重绑对象并重跑受影响测试、重审。 |
| 测试未运行，却写“测试通过” | 把 not_run 升格为 passed；如实标未运行和影响，不能支持该行为已验证。 |
| 测试失败或缺报告，却仅写命令已执行 | 执行不是通过；保留失败/缺失状态及实际证据缺口。 |
| 有提交 A 或 Builder 自检，所以写独立验收通过 | Git/自检不是独立 reviewer；链接真实 verdict，否则明示暂无。 |
| 单元测试通过，所以独立验收通过 | 证据层混同；测试只能支持覆盖到的行为，不能替代独立验收。 |
| 每个子 Session 有 closeout，父面仅列链接 | 缺总体说明；父面必须汇总实现变化、原目标影响、缺口及最终对象证据。 |
| closeout 提醒命令退出 0，或语言检查通过，所以无遗漏 | 这两个工具不检测本规则的结构与证据真实性；仍需人工清单与独立审查。 |

## 多 Session 合格汇总示意

父面正文说明：S1 修复 CLI 非法参数退出码，S2 为路由增加有限等待，两者共同支持输入拒绝与等待上限目标；仍未验证生产 Provider，声明限最终快照 S2 的本地行为。父面链接每项源码、提交/快照和最终重绑测试、独立 verdict，并保留六字段；子 closeout 仅作为补充证据。这种总体说明不能用“S1/S2 都 Done”代替。
