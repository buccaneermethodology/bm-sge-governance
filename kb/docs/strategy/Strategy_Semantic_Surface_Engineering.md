# Strategy Semantic Surface Engineering

_Owner: sge-semantic-governance | Version: v1.0 | Status: active | Updated: 2026-09-02_

## 核心定义

- **Meaning**: 当前 authority、ontology、invariants 与 evidence 共同约束下可支持的含义。
- **Semantic Surface**: 未来 Agent 或人类读取后会据此形成判断的命名、状态、contract、Dashboard、closeout、代码与投影表面。
- **Semantic Entropy**: 含义在跨角色、跨 artifact 或跨阶段传递时产生的歧义、丢失和错误压缩。
- **Memory Surface**: KB、Dashboard、日志和生成投影中被后续工作读取的持久表面。

## Meaning Transformation Flow

1. 确认原始意图与 authority。
1. 冻结 contract、examples、counterexamples 与 claim ceiling。
1. 通过 lane handoff 转换为实现任务。
1. 从实际 execution/test evidence 重算判定。
1. 把稳定 truth、执行记忆和派生投影写入各自 carrier。
1. 以 final diff 和 reader-facing surface 做压缩误读测试。

## 语义不一致分类

| ID | Class | Plain Meaning |
| --- | --- | --- |
| S1 | Intent Misalignment | Agent 承诺了错误目标，或解决了相邻但不等价的问题。 |
| S2 | Semantic Drift | 含义在编辑、Agent、Session、重构或执行面扩大中改变。 |
| S3 | Semantic Overclaim | 局部证据被提升为其无法支持的更广能力或公共主张。 |
| S4 | Semantic Ambiguity | 多个合理含义在实现或验收前仍未消解。 |
| S5 | Semantic Unverifiability | 项目无法证明声明、测试、拒绝或接受的是哪个含义。 |
| S6 | Semantic Authority Confusion | 项目失去对哪个 artifact 有权定义 truth 的区分。 |

**Section Constraints**

- S1-S6 是诊断透镜，不是数值评分或普遍科学定律。

## Diagnostic Alignment Surfaces

| ID | Surface | Diagnostic Question |
| --- | --- | --- |
| L0 | Semantic Memory Surface | 含义是否被记录在正确 authority 层：KB truth、Dashboard state、candidate、evidence、report、closeout 或 promotion decision？ |
| L1 | Intent Surface | Human 与 Agent 是否在相同 scope/non-goal 下解决同一问题？ |
| L2 | Capability Surface | 系统可声明什么，必须排除什么？ |
| L3 | Execution Surface | 实现或重构是否保持预期含义？ |
| L4 | Collaboration Surface | Agent、Session、validator、reviewer 和未来读者是否继承同一语义状态？ |
| L5 | Validation Surface | 语义正确性是否可检查、可审计并绑定正确 claim？ |
| L6 | Runtime Evolution Surface | 含义能否在受治理的执行面扩大、CLI rollout、重构和长期复用中保持？ |

**Section Constraints**

- L0-L6 是诊断定位表面，不授权任何 runtime/CLI 扩大。

## Semantic Review Protocol

- [ ] 先检查 authority、ontology、invariants 与 claim ceiling，再检查措辞。
- [ ] 对 done、landed、active、covered、integration、complete、support、foundation 做一行压缩误读测试。
- [ ] 同时输出 Design Freeze Validity 与 Implementation Entry Readiness。
- [ ] 区分 current-contract blocker 与 deferred hardening。
- [ ] witness、case、report 和投影不自动成为 law。

## Promotion Boundaries

- 只 promotion 稳定、可复用、可分离且 owner 明确的最小子集。
- 不因本策略改变 runtime、schema、BDD、acceptance、provider、CLI、图或发布边界。
- 来源项目历史和执行计数只保留在 provenance，不进入 canonical truth。

## Claim Ceiling

本策略提供有界 semantic-surface 诊断与 review vocabulary；不声称自动发现所有语义错误，也不替代人类 oracle 或确定性 gate。

## Source Scope

- `kb/data/strategy/strategy_human_ai_development.json`
- `Dashboard/Artifacts/Stage-Plan-SP-001/SP001_S013_SourceAdjudication.md`
- `kb/data/strategy/sge_strategy_source_manifest_v1.json`

## Related Docs

- `sge-strategy-human-ai-development`
