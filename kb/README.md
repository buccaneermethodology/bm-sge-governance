# SGE Governance 知识库

本目录是 SGE Governance Skill 的 canonical truth（稳定治理合同、术语与来源规则）。JSON 位于 `kb/data/`，Markdown 位于 `kb/docs/`；Markdown 是可读投影，不是独立真源。

## 当前范围

- `sge_project_profile_v1.json` 定义通用 Skill 身份、根目录与 authority 路由。
- `sge_strategy_source_manifest_v1.json` 固定来源 revision、provenance 与 56 个 strategy 表面的审计入口。
- `sge_strategy_canonical_mapping_v1.json` 定义通用治理规则的抽取、排除与 promotion policy。
- SGC、ERBE 与 workflow registry 提供结构治理、合同验收和可执行阶段入口。

## 权威边界

稳定 truth 写入 `kb/data/`；执行状态、Session、阻断和 closeout 写入 `Dashboard/`。Dashboard DKG 与 Markdown 均为执行记忆投影，不替代本目录的 canonical truth。

本仓库只提供可复用的 repo-local SGE Governance 框架，不实现任何具体产品、provider 或公共发布。KYM/TCO、历史 phase/runtime 和高级 Loop 编排均不属于默认核心；如未来需要，必须作为独立、明确授权的扩展重新设计。

## 工具

- `.codex/skills/sge-governed-checkpoints/`：治理 checkpoint、schema 与确定性脚本。
- `kb/tools/render_kb.py`：从带 `doc_id`/`doc_type` 或 `kind=kb_index` 的 JSON 生成 Markdown 投影；`--check` 只验证、不写入。

## 知识库维护

以下命令均在完整开发源仓或公共包的根目录执行。完整开发源仓的默认清单保留十七项映射，检查命令为 `python3 kb/tools/render_kb.py --check`。公共包使用显式公共清单，当前覆盖发行清单中 `kb/docs/` 下的全部十份 Markdown，检查命令如下。

```bash
python3 kb/tools/render_kb.py --manifest kb/public_render_manifest_v1.json --check
```

`--check` 逐项核对源文件、阅读文档及渲染字节，缺件或内容不一致时以非零退出。显式再生成使用以下写入命令。

```bash
python3 kb/tools/render_kb.py --manifest kb/public_render_manifest_v1.json
```

维护公共发行范围时，同步更新静态公共清单。`python3 tools/public_ci_smoke.py` 会将其全部输出与发行清单的全部公开 KB 输出比较，拒绝漏映射、重复映射和包外源，再执行上述字节检查。其他公开 Markdown 的逐文件存在性及安全检查由 `python3 tools/sge_public.py doctor` 承担。公共包仍保留完整开发清单，维护者应按这里的显式公共入口操作。以上说明对应当前源码维护入口。
