# Semantic Review recipe

1. 同时做 Boundary Review 与 Evolution / Implementation-Entry Review。
2. 输出 `Design Freeze Validity` 与 `Implementation Entry Readiness` 两个独立 verdict。
3. 检查 truth carrier、authority、state axes、forbidden collapse、Scope Delta、claim ceiling、minimum safe slice、implementation ladder、next-session map 与 misuse scenario。
4. 对 done/landed/active/covered/integration/complete/support/foundation 做单行压缩误读测试。
5. pre-Builder 与 final Semantic Review 分别保留时序证据；后者不能倒推前者。
6. classifier/receipt 不得演化成 God Object；半 schema DSL、governance inflation 与 misplaced truth 应明确指出。
7. 在正式 Semantic Review 前完成确定性一致性预检；Review 首轮穷尽预声明基线，不能遇首个 FAIL 提前返回。输出全量发现、已检查无问题面、未检查原因、同类残余和修复后准入预测。
8. 按工件身份累计最多三轮，revision/card/cycle/rebaseline 不重置。Round 1 为全基线，Round 2 为集中修复 Delta Review，Round 3 只核验 Round 2 新 finding 的修复或显式 rebaseline；Round 2 新 finding 要说明首轮为何无法合理发现。
9. 区分阻断缺陷与 non-blocking cleanup。若整理项不改变 oracle、状态码、拒绝优先级、allow/deny、数据写入或权限，可用 `PASS_WITH_MINOR_FIX`，修复后做确定性检查或短 Delta Review，不重启完整设计审查。

S1–S6/L0–L6 taxonomy 与模板扩读 `../checklists.md`。
