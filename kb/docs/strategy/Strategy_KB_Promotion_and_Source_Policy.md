# Strategy KB Promotion and Source Policy

_Owner: sge-kb-governance | Version: v1.0 | Status: active | Updated: 2026-09-02_

## Authority Ladder

| 层 | Carrier | Authority |
| --- | --- | --- |
| L1 | 用户原始意图与批准 | 任务和 scope authority |
| L2 | kb/data machine-readable contract | 稳定 canonical truth |
| L3 | 由 canonical JSON 生成的 kb/docs | 阅读面，不可独立编辑 |
| L4 | Dashboard 与 closeout | 执行状态、决定、阻断和 evidence |
| L5 | tests/runtime/reports | 与 claim 匹配的观察证据 |
| L6 | 派生索引与可视化 | 只读 projection |

## Promotion Criteria

- [ ] 规则跨 Session 稳定，而非单次 workaround。
- [ ] 规则可复用且能与来源产品事实分离。
- [ ] owner、authority、dependencies、non-goals 与 claim ceiling 明确。
- [ ] 存在 canonical JSON 或新的 frozen contract，而不是只引用 Markdown。
- [ ] 独立 Validation/Semantic Review 已检查 truth placement 和误用风险。

## Contract Delta Scan

| 分类 | 落点 |
| --- | --- |
| promote-to-KB | 稳定规则进入 kb/data，并重新渲染阅读面 |
| Dashboard-only | 执行状态、blocker、decision、candidate next session |
| gate-docs later | 尚未冻结的操作说明 |
| runtime/tests later | 需要单独合同和验收的行为变化 |
| deferred session | 当前 scope 外但具体可执行的 follow-on |

## Source Policy

- 来源阅读面只用于理解；promotion 必须追溯 canonical source 或显式记录 null reason。
- 外部/历史来源使用逻辑 provenance 和固定 revision，不把本机绝对路径写入公共 canonical truth。
- Dashboard inventory、schema-valid、render pass 和派生 projection 都不能替代 semantic promotion。

## 明确非承诺

- 不 wholesale promotion 来源目录。
- 不把 report、derived projection、closeout 或 runtime output 当 semantic law。
- 不因 KB promotion 自动改变 runtime、schema、acceptance 或发布状态。

## Claim Ceiling

本策略只规定 canonical truth、execution memory 和 derived projection 的 promotion/source 边界；不证明任何具体 artifact 已 promotion、发布或生产就绪。

## Source Scope

- `AGENTS.md`
- `kb/data/strategy/strategy_human_ai_development.json`
- `kb/data/strategy/strategy_semantic_surface_engineering.json`
- `Dashboard/Artifacts/Stage-Plan-SP-001/SP001_S013_SourceAdjudication.md`

## Related Docs

- `sge-strategy-human-ai-development`
- `sge-strategy-semantic-surface-engineering`
