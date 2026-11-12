# 行为分解与进度双视图模板

## 使用方式与边界

稳定规则见[完整只读方法投影](readers/user-oriented-acceptance-case-quality.md)及[来源记录](readers/projection-sources.json)；唯一 canonical 仍位于发行 source 仓 `kb/data/strategy/strategy_user_oriented_acceptance_case_quality_v1.json`，投影只供阅读，不更改项目 authority。方法投影的六项行为分解章节；原有六点写作视角仍用于写清G-W-T。本模板不新增机器gate/schema/CLI、自动百分比或批准权限。

先复用当前Goal的Original Plan Coverage Matrix（OPCM）、Session、[Implementation Delta](implementation-delta-template.md)及原证据；只引用已有ID和链接，不复制全段G-W-T或再建状态账本。普通Goal可将下列维度合并到已有表的字段/区域，不强制五张表；复杂依赖才按需拆表，不适用项说明原因。空白表示待填，不表示未开始或通过。

每个实际记录时点先填Goal/Session ID、观察时间、共享底表revision、原意图/AC/批准来源、承诺集合、候选集合、本次证据清单。任务卡引用相关对象ID/AC pointer和最大声明；最终回到原始AC/完成条件。

## 先用具体故事开场，再长出行为树

例如：我在仓库接到“补映射设计”的任务，只看任务名不知道服务哪条原AC；我展开“任务归属”分支，应能沿任务ID找到原始义务、场景和共享行为。又如方法页、模板都已生成，但独立Review没执行；我展开“局部与整体缺口”，应先看到成果证据、仍缺的独立验证及下一步，而非一个笼统完成标签。这是模板使用处境，不是DataEase实际运行。

实际进度只持续维护Progress.md；HTML从同文件全文派生，不另手写状态账本。每次更新源，同步生成固定Progress.html并显示更新时间与源revision/digest；用户刷新看新内容，不承诺实时推送。阶段记录在同源文件按时间简短追加，旧绑定历史保持只读；必要的Validation baseline/独立Review/Stop receipt仍保留。

阅读树骨架（按需合并，不是新增五表）：原目标根→具体场景分支→系统行为唯一主节点→成果/贡献引用叶子。名称先于ID；每主节点先写成果、证据、缺口、下一步，再折叠身份、owner、状态轴和规则。一个主节点只存一次当前状态；共享行为在其他分支锚点引用，原始承诺与尚未展开范围放可展开的保留分支。深度/广度表示拆解，不代表完成率。

<details><summary>示例阅读树（空白骨架，不含实际状态）</summary><ul><li>原目标：引用原AC与完成条件<ul><li>接到任务后找到原要求<ul><li>四对象与多对多主节点：填写成果→证据→缺口→下一步；详情填ID/owner/状态轴</li></ul></li><li>发现局部成果仍缺整体证据<ul><li>连接与验证主节点：分别填写节点证据和连接证据</li><li>共享引用：链接前述唯一主节点，不重复状态</li></ul></li><li>原始承诺和未展开范围：收起但不删除</li></ul></li></ul></details>

未开始、未验证、未知、失败、环境/authority阻塞分别解释；只有真实前置条件不可用才写阻塞及解除条件。虚线/颜色只是辅助，节点须有父归属，不制造孤点。HTML保留完整表格/锚点/details，实际浏览器检查展开、键盘、约390px窄屏、链接和源一致性；这些是展示层检查，不替代原AC人工审查，不默认新增生成脚本/CLI/gate。

## 按比例空白记录

| 可合并维度 | 在既有记录中填写 |
| --- | --- |
| 对象 | 稳定ID；义务/AC、用户场景、系统行为、任务四类；精确来源/G-W-T链接；真实入口；各自验收判定/oracle；owner；承诺或候选 |
| 关联 | 关联ID；两端ID；主/其他关联；含义及来源；保留多对多，树只是投影 |
| 连接与来源 | 连接ID、源→目标、接口约定；待接入/已接入未验证/通过/失败/待核实；连接证据/revision；新增/复用/待核实与独立来源证据 |
| 状态与证据 | 设计/实现/接入/测试准备分列；验证层级/结果/独立性分列；revision/环境/时间/当前有效性；未知、未开始、未运行、失败、环境阻塞分别依据 |
| 贡献与发现 | 贡献ID、任务→对象、前→后、成果证据、剩余缺口、下一步/owner；发现ID、细化/任务改路/Scope Delta候选、影响、裁定/批准reference；稳定ID变更记录 |

合并行填写骨架：对象ID｜类型｜原AC/GWT引用｜验收依据｜关联ID｜连接ID/状态｜来源/证据｜状态轴｜验证层级·结果·独立性｜revision·有效性｜贡献ID·前后｜缺口·下一步·owner｜承诺或候选。实际证据应可点击；没有证据写未知，不造文件。

用户视图选择场景/义务、阶段成果、本次推进、障碍、下一步；Agent视图选择系统行为、连接、任务owner、cases、证据版本。两者均从同一底表行投影，表头注明相同时间/revision；状态只在底表改，不独立手写两份真源。冲突时回到原记录取证；两视图不互相作truth。

## 北京与最近七天教学底表

**以下输入、状态、owner、revision和证据名均为教学假设；未运行DataEase，也不是本Goal真实进度。** Authority及G-W-T正文统一引用[方法页贯穿例子](readers/user-oriented-acceptance-case-quality.md#贯穿教学正例与两层-g-w-t)，不复制全文。主情境观察时点=E2，底表revision=DEMO-E2；主情境展示模块通过、连接失败。后文MC-05替换输入独立标记为ALT-E3/DEMO-ALT-E3，含DEMO-E1历史假设，不并入主E2当前事实。

教学D1/M1/C1/V1等是本节文字输入记号，不是实际证据artifact。实际使用须换为真实文件链接、观察及reviewer；可点击方法来源不使教学状态成为产品事实。

### 对象与多对多关联

| 行ID / 类型 | 来源与验收判定 | 关联及边界 |
| --- | --- | --- |
| O-AC / 原始义务 | 方法页AC-DEMO-1：兼容目标保留北京、动态最近7天、源不变；按合同入口验收 | 原分母O-AC保持，任务拆分不改变最终边界；本教学假设未包含保存重开 |
| O-SC-COPY / 用户场景 | 方法页用户G-W-T，页面乙粘贴应用显示选择、源甲不变 | L1：O-AC→本场景；依赖O-B-COPY、O-B-DATE |
| O-SC-QUERY / 用户场景 | 同一动态语义要求的分解，按目标查询日计算最近7天；正式结果oracle待实际合同 | L2：O-AC→本场景；同样依赖O-B-DATE，不是新增批准AC |
| O-B-COPY / 系统行为 | 方法页系统G-W-T，转换保留城市、源输入 | L3：支撑O-SC-COPY；T-MAP关联 |
| O-B-DATE / 共享行为 | 同页系统G-W-T，relative/last_7_days不固化 | L4/L5：同时支撑两场景，仅一个行为ID |
| O-B-QUERY / 系统行为 | 消费相对语义，按查询日求值；具体oracle待合同 | L6：支撑O-SC-QUERY，有关键连接 |
| T-MAP / 设计子交付任务 | 本任务只交付后续映射改进设计；本子交付对应的实现尚未开始 | L7/L8：一个设计任务关联O-B-COPY和O-B-DATE；不否定另一任务已有模块成果，不升级O-AC |
| T-MODULE / 既有模块任务 | 既有O-B-COPY/O-B-QUERY实现及模块自检；与T-MAP后续设计子交付不同 | L10/L11：关联已有两模块；自检不证明后续映射改进实施或连接通过 |
| O-CLI / 直接系统流程义务 | 独立教学假设：CLI拒绝无权限调用、不写数据；按CLI合同观察 | L9：直接映射T-CLI；无UI用户，不并入AC-DEMO-1分母 |
| T-CLI / 任务 | 准备权限case和副作用观察；owner=示例CLI lane | 按真实CLI入口验收，不虚构UI场景 |

四对象各自完成依据：O-AC按原始完成条件；场景按其可观察结果；行为按其合同/不变量；任务按交付合同。一个层级通过不推导父级通过。

### 连接与能力来源

| 连接ID | 源→目标与约定 | 状态/连接证据 | 能力来源/来源证据 | 缺口与下一步 |
| --- | --- | --- | --- | --- |
| C-DATE-QUERY | O-B-DATE→O-B-QUERY，传递相对日期 | 连接失败；教学C1日期固化，DEMO-E2 | 转换拟新增、查询拟复用；M1仅两端模块能力 | 连接owner修复并重验；模块通过不证明整链 |
| C-REUSE | 既有查询服务→调用点 | 待核实，无真实接线证据 | 复用候选；M2仅说明服务存在，兼容性待核 | 查来源revision/接口/实际调用，不自动新增实现 |
| C-PENDING | O-B-COPY→映射点 | 待接入 | 新增；D1仅设计 | 实施接线后先标未验证 |
| C-WIRED | 映射点→显示适配点 | 已接入未验证；教学W1接线记录 | 来源待核实；W1不证明能力身份 | 准备并执行连接case |

### 分层状态与版本

所有通过限定本行层级和示例revision。

| 状态行ID / 对象 | 设计 / 实现 / 接入 / 测试准备 | 层级 / 结果 / 独立性 | revision有效性与缺口 |
| --- | --- | --- | --- |
| S-DESIGN / T-MAP设计子交付 | 已审 / 本子交付的后续实现未开始 / 后续映射待接入 / 改进case草案、环境待备 | 设计 / 通过 / 独立示例Reviewer | D1，DEMO-E2设计范围；O-AC未验收 |
| S-MODULE / O-B-COPY、O-B-QUERY（T-MODULE既有模块） | 有设计 / 既有模块已实现 / 见连接表 / 模块case已备 | 模块 / 通过 / producer自检 | M1，DEMO-E2仅模块；不代独立Validation/连接通过 |
| S-UNKNOWN / C-REUSE | 未知 / 未知 / 待核实 / 未知 | 连接 / 未知 / 未知 | 无证据、revision未知；先取证，不能写未开始 |
| S-NOTSTART / T-CLI | 有要求 / 未开始 / 不适用（case任务） / 未开始 | CLI / 未运行 / 无结果 | 教学计划P1确认未启动；DEMO-E2，不等于失败 |
| S-NOTRUN / O-SC-COPY | 有设计 / 局部实现 / 连接失败 / 场景case已备 | 场景 / 未运行 / 尚未独立运行 | DEMO-E2无场景证据；修连接后按原入口验 |
| S-ENV / O-SC-QUERY | 有设计 / 局部实现 / 见连接 / 环境阻塞 | 场景 / 环境阻塞、行为不可判 / producer尝试 | 教学E1数据库不可用；DEMO-E2，恢复环境而非写行为失败 |
| S-FAIL / C-DATE-QUERY | 有设计 / 已接线 / 失败 / case已备 | 连接 / 失败 / 独立示例Reviewer | C1，DEMO-E2；日期固化，父场景未通过 |

这些轴可并行/回退，不是固定线性状态机。测试准备不代表运行。UI/API/CLI/后台依原入口，内部证据不冒充用户结果。

### 贡献、发现与稳定ID

| 行ID | 任务→对象；前→后 | 成果/证据与剩余缺口 | 下一步/owner |
| --- | --- | --- | --- |
| K-DESIGN | T-MAP设计子交付→O-B-COPY、O-B-DATE；未审→设计通过 | D1；同一贡献ID关联两行为、两场景，成果计一次；O-AC不升 | 实施/示例Builder |
| K-ZERO | T-PROBE→C-REUSE；未知→未知 | 教学Z1无有效来源或接线证据；零贡献可见 | 查接口/revision/调查lane |
| K-GAP | T-TEST→C-DATE-QUERY；接线未验→失败 | C1暴露新缺口F-DATE，不能写正向通过 | 修转换再验/连接owner |
| F-DETAIL | 细化已有动态日期要求 | 补跨日case映射，原分母/预期不变，不默认新审批 | 主Agent核对后继续 |
| F-ROUTE | 实现改路为复用适配器 | 任务调整，记录依赖影响，原预期/authority不变 | 主Agent记录后实施 |
| F-SAVE | 本教学AC未包含保存重开 | Scope Delta候选，待裁定；不入承诺统计 | 主Agent/适当authority决定 |
| F-SAVE-INCLUDED | 另一个输入分支：原AC已明确包含保存重开 | 已有要求细化，补原AC→行为→case；不新增承诺AC | 按原合同执行/主Agent |
| CH-1 | O-B-DATE细化为MAP/EVAL子行为 | 保留父ID/来源，记新子ID、原因、前后边、时间DEMO-E2；不制造进度 | 更新引用，仍验O-AC |
| CH-2 | 删除/替换/合并/重命名时的填写要求 | 保留旧ID、继承/失效关系、来源与裁定reference；不静默消失 | 改冻结预期走Contract Patch/Scope Delta/必要批准/re-RED |

贡献不按任务数或简单平均升级原始义务。发现需补证据/未知、影响、推荐项、owner和裁定reference；候选可见但隔离承诺分母。

## 历史与新版的独立替换输入

本节是MC-05及MC-10回退子情境的**独立对照输入**，观察时点ALT-E3、底表revision=DEMO-ALT-E3；它替换相应对象的状态输入，不与主E2表合并，也不声称是主E2之后实际发生的历史。主E2的S-MODULE不作为本对照当前通过证据。

| 对照底表行ID | 对象/变化 | 历史与当前证据归因 | 缺口/下一步 |
| --- | --- | --- | --- |
| S-HISTORY | O-B-DATE；设计已有、实现受新版变更影响、接入待复核、回归case已备 | 教学V1仅证明DEMO-E1历史模块独立通过；DEMO-ALT-E3当前结果待复核，不继承通过；独立性仅归历史Reviewer | 当前回归/示例Validator |
| K-ROLLBACK | T-REV→O-B-DATE；DEMO-E1通过→DEMO-ALT-E3受影响待复核 | 教学V2变更，旧V1保留；贡献为暴露回退，不是新的正向验收 | 重新取当前证据/示例Validator |

对照的两种视图均只投影本节同一底表（ALT-E3/DEMO-ALT-E3），不混用E2行：

| 对照视图 | 投影与共同来源 |
| --- | --- |
| 用户视图 | O-SC-COPY/O-SC-QUERY关联的动态日期保障当前待复核，父O-AC未验；历史成果保留但当前有缺口（S-HISTORY、K-ROLLBACK），下一步当前回归 |
| Agent视图 | O-B-DATE / 示例Validator；V1归DEMO-E1，DEMO-ALT-E3受影响待复核（同S-HISTORY、K-ROLLBACK）；回归case已备、当前结果未定 |

## 同一底表的两种视图

以下主情境两表均投影“示例E2 / DEMO-E2”，不包含ALT-E3对照；括号ID定位上方唯一底表，不独立新增状态或结果，不复制G-W-T全文。

### 用户视图

| 场景/义务 | 阶段成果/本次推进 | 障碍与下一步 |
| --- | --- | --- |
| 北京+最近7天复制（O-SC-COPY→O-AC） | 设计成果可见（S-DESIGN、K-DESIGN） | 场景未运行、连接失败（S-NOTRUN、C-DATE-QUERY）；修后验原AC |
| 目标日期查询（O-SC-QUERY→O-AC） | 模块自检可见（S-MODULE），共享成果不重计 | S-FAIL、S-ENV；修连接、恢复环境后独立验 |
| CLI权限（O-CLI） | 未开始（S-NOTSTART） | 准备CLI case，无UI要求 |
| 保存重开（F-SAVE） | 发现可见、仍候选 | 主Agent裁定，不计承诺完成 |

### Agent视图

| 行为/任务owner | 依赖/cases | 证据版本与缺口 |
| --- | --- | --- |
| O-B-COPY、O-B-DATE / T-MAP、示例Builder | L3..L8、C-PENDING、C-DATE-QUERY；方法页正反例 | D1/M1/C1均假设；K-DESIGN同一ID；O-AC未验 |
| O-B-QUERY / 示例查询lane | C-REUSE；模块与连接case分开 | S-UNKNOWN来源未知，S-MODULE不是独立验收 |
| O-CLI / T-CLI、示例CLI lane | L9、CLI权限及副作用case | S-NOTSTART未运行，不虚构UI用户 |
| F-SAVE / 主Agent | 候选scope，不改冻结expected | F-SAVE与F-SAVE-INCLUDED是不同输入分支，不是同时批准 |

## 十二类人工填写与复核引导

这是人工指引，不是自动runner。MC编号对应本轮示范分类；实际任务引用自己的冻结case identity/authority。每案另填真实输入、底表/视图行、实际产物section链接、观察结果、预期对照、判定理由、reviewer、revision/环境。未填/未跑不得写通过；MC-04/10逐子情境填写。

| 情境 | 实际填写与判定操作 |
| --- | --- |
| MC-01 设计已审未实施 | 填S-DESIGN/K-DESIGN，核对T-MAP设计子交付成果可见、其后续实现未开始、O-AC未验；不把T-MODULE既有实现混入此任务，不压成完成百分比 |
| MC-02 模块过连接失败 | 分开S-MODULE/S-FAIL，核对两视图保留C-DATE-QUERY失败、父场景未通过 |
| MC-03 共享/跨任务 | 追L4/L5、L7/L8与K-DESIGN，核对多对多、四对象验收和同成果不重计 |
| MC-04 状态区别 | 分别填写S-UNKNOWN、S-NOTSTART、S-NOTRUN、S-ENV、S-FAIL五个输入及依据，不能合并一句通过 |
| MC-05 旧版/新版 | 单独使用ALT-E3/DEMO-ALT-E3对照底表及其两视图，填S-HISTORY/K-ROLLBACK，保留DEMO-E1旧通过归因，当前待复核；不合并主E2模块通过输入 |
| MC-06 保存重开 | 分别用原AC已包含输入填F-SAVE-INCLUDED，未包含输入填F-SAVE；核对补映射/候选待裁定隔离 |
| MC-07 三类变更 | 对照F-DETAIL/F-ROUTE/CH-2，前两类不默认审批，改变批准预期走既有冻结路线 |
| MC-08 复用待核 | 填C-REUSE，分查能力来源和接线，存在能力不推导接通或新增scope |
| MC-09 系统/流程入口 | O-CLI直接映射T-CLI，按原UI/API/CLI/后台入口验收，不虚构用户 |
| MC-10 双视图/非单调 | 主E2对K-ZERO/K-GAP分别填；回退另用ALT-E3的K-ROLLBACK及该对照两视图。每组两视图内部同时间/revision/源行，不跨情境拼接。实际任务在唯一Progress.md内保留真实checkpoint的时间/贡献/当时证据与缺口，不新建展示快照；既有绑定历史只读保留，不能用教学表倒填历史 |
| MC-11 全生命周期 | 逐入口取Goal/Design关联→任务卡ID→里程碑贡献→closeout→原AC证据，引用原OPCM/Session/Implementation Delta |
| MC-12 无最终Review | 输入文档已生成/命令通过但缺独立Review，只可报候选和证据层；完整AC/流程及最终态独立绑定另查 |

## 实际收口提示

逐项回到原OPCM核对技术与流程must-have。分清教学/实际、来源/连接、模块/场景、自检/独立、历史/当前、候选/承诺。KB存稳定方法，Dashboard存真实进度/快照/决策。模板齐全与生成一致不证明产品验收、全过程完成或模型普遍改善。
