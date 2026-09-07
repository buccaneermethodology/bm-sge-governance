# sge-governance-skill

可复用的 SGE（Semantic Governance Engineering）治理 Skill 仓库。

公共候选的项目身份是 `bm-sge-governance`；本仓库 `sge-governance-skill` 仅是私有 canonical source。二者、Skill 身份与每次 `candidate_id` 必须由独立 gate 分开核对。

核心入口是 [.codex/skills/sge-governed-checkpoints/SKILL.md](.codex/skills/sge-governed-checkpoints/SKILL.md)。它为非平凡任务提供 Context Bootstrap、ERBE specification-first、SGC、Goal Conformance、lane card、独立 Validation、Semantic Review、closeout-language 和 post-closeout 对账门禁。

## 最小使用

在目标项目中复制 `.codex/skills/sge-governed-checkpoints/`，然后将项目自己的 `kb/`、`Dashboard/` 和 `AGENTS.md` 作为 authority；不要复制本仓库的历史迁移记录或任何具体产品文件。

常用入口：

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage full
python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode sgc
```

上面两条命令可以在公开候选根目录直接运行。维护者在已有实际文件时，再把自己的 Context、lane card 或 closeout 文件路径作为参数传给 `context_bootstrap.py validate`、`lane_task_card.py validate` 和 `guardrail_checklist.py --mode closeout-language`；这些路径不是可直接复制的公共示例，因此不放进 bash fence。

面向第一次接触 SGE 的用户，可以直接复制[通过 Agent 安装和初始化的 Prompt](docs/Agent_Setup_Prompt_CN.md)。先准备一个空的产品项目目录、Git、Python 3 和公开仓库访问权限，再把 Prompt 交给你使用的 coding agent；它不依赖 Codex、特定模型或具体产品类型。也可以阅读[中文新手指南](docs/Beginner_Guide_CN.md)或[快速开始](docs/Quick_Start_CN.md)。

Prompt 使用前唯一的项目准备是：建立一个空目录并把 Agent 的工作目录设为该目录。目录中不要放入产品代码；macOS 的 `.DS_Store` 也应先移走。Prompt 已内置官方公开仓地址 `https://github.com/buccaneermethodology/bm-sge-governance.git`，Agent 不应猜测或替换仓库身份。

公共候选可用以下命令进行 default-deny 检查和干净导出：

```bash
python3 tools/sge_public.py doctor
python3 tools/sge_public.py export /tmp/sge-public-candidate
```

`public_export_manifest_v1.json` 逐文件记录 source、license、provenance、public 决定和执行上下文边界。导出成功只形成 `candidate_not_approved` 候选，不等于 release authorization。

仅在包含私有 Dashboard 执行面的源仓库维护场景中，再运行 `python3 Dashboard/tools/doctor.py --repo .`；公共导出包不包含该内部 doctor，其自检入口始终是 `python3 tools/sge_public.py doctor`。

## 边界

本仓库只维护通用治理能力，不包含音频转写或其他产品实现。`build-kym`、`build-tco-coverage` 和 Loop 编排器都是可选扩展，不会被核心 Skill 默认加载。公共发布、全局安装和跨仓库普遍适用性需要另行验证与授权。

`doctor.py` 会执行非零 unittest discovery、genericity、registry、KB `--check`、引用/公共身份扫描和临时 DKG 生成；发现 0 个测试会以 `zero_tests_discovered` 失败。doctor 通过只表示当前 repo-local 验收面通过，不等于已批准或已公开发布。

## 目录

- `.codex/skills/sge-governed-checkpoints/`：Skill、references、schemas、确定性脚本。
- `kb/data/strategy/`：SGE canonical strategy contracts 与 generic profile。
- `Dashboard/`：执行记忆、Validation、closeout 和 provenance 记录。
- `docs/`：面向新手的公共 companion 文档。
- `docs/Agent_Setup_Prompt_CN.md`：跨 Agent、跨产品的安装与初始化 Prompt。
- `tools/sge_public.py`：可恢复的 doctor/export/bootstrap/install/upgrade/uninstall 入口。
- `extensions/registry_v1.json`：默认关闭的 domain extension 接口；core 不依赖这些扩展。
