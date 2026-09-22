# ERBE Specification-First Acceptance V1

_Owner: sge-core | Version: v1.0 | Status: active | Updated: 2026-07-26_

## 权威分层

- `stable_method`：kb strategy JSON
- `per_goal_acceptance`：Dashboard frozen ERBE Contract/Cases
- `execution_gate`：independent ERBE runner and maintained tests
- `readable_projection`：tests/bdd/readable_cards/; projection-only

## 适用性

- required
- proportional
- not_applicable
- blocked_oracle

## 生命周期

- candidate
- reviewed
- frozen
- red_verified
- builder_locked
- green_candidate
- independently_validated
- absorbed

## 合同必需字段

- state_axes
- terminal_predicates
- invariants
- examples
- counterexamples
- forbidden_collapses
- observable_evidence
- oracle_owner
- write_exclusions
- claim_ceiling

## 不变量

- domain terminal predicates remain separate from Goal composite verdicts
- contract/execution/behavior verdicts remain separate
- environment errors are not semantic RED
- RED and GREEN use the same frozen case identity
- producer status is not independent validation evidence

## 明确非目标

- finite examples are not complete semantic law
- readable BDD cards are not pass/fail authority
- ERBE does not prove general semantic correctness or automatic human approval

## Builder 规则

Builder write scope excludes frozen contract, cases, expected values, RED evidence and claim ceiling; any revision requires Contract Patch, Scope Delta and re-RED.

## Claim Ceiling

`ERBE_GOVERNED_SPECIFICATION_FIRST_ACCEPTANCE_LANDED`

## Source Scope

- `Dashboard/Artifacts/Stage-Plan-SP-001/SP001_S002_SGECore_Design.md`
- `.codex/skills/sge-governed-checkpoints/SKILL.md`
- `Dashboard/Artifacts/Stage-Plan-SP-001/SP001_S002_SGECore_ERBE_Contract.json`
