# SGE Governance Skill 快速开始

```bash
python3 tools/sge_public.py doctor
python3 tools/sge_public.py export /tmp/sge-public-candidate
python3 tools/sge_public.py bootstrap /tmp/sge-demo
cd /tmp/sge-public-candidate
python3 tools/sge_public.py install --target /tmp/sge-demo --admission <owner-provisioned-execution-admission.json>
python3 /tmp/sge-demo/.codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode intake-evaluation
python3 tools/sge_public.py upgrade --target /tmp/sge-demo --admission <owner-provisioned-upgrade-admission.json>
find /tmp/sge-demo/.sge-backups -name SKILL.md -print
python3 tools/sge_public.py uninstall --target /tmp/sge-demo
```

`install`/`upgrade` 在第一次写入前必须提供 owner-provisioned `execution_admission_v1`；它绑定 Goal、Completion Contract、Context、Design/Review、topology、action 和 target。缺失或摘要漂移会 fail closed。`--source` 仅用于维护者或测试 alternate source。

从候选仓库根目录开始运行。`/tmp/sge-public-candidate` 是干净 staging source，`/tmp/sge-demo` 是 target project；两者必须不存在或为空。通过条件：doctor 成功；export 只含 manifest 项；bootstrap 不覆盖非空目录；core 可执行；upgrade 在 `.sge-backups/` 留下旧 core；uninstall 把当前 core 与 install record 移到 `.sge-trash/`。升级失败会恢复旧 core；目标项目的 `AGENTS.md`、`kb/`、`Dashboard/`、Goal 和 Session 始终由 target owner 保持。这是有界 clean-room 行为证据，不是跨平台兼容、公开发布或 production readiness 证明。

## 首任务与初始 KB recipe

安装后的 core 自带首任务分类、只读能力预检与初始 KB recipe。准备 JSON 输入后运行：

```bash
python3 .codex/skills/sge-governed-checkpoints/scripts/first_task_router.py classify /tmp/first-task.json
python3 .codex/skills/sge-governed-checkpoints/scripts/capability_preflight.py inspect /tmp/preflight.json
python3 .codex/skills/sge-governed-checkpoints/scripts/initial_kb_bootstrap.py build /tmp/initial-kb-input.json
```

Goal 缺失或冲突时不会启动 Builder；optional adapter 缺失时明确使用 core recipe。recipe 只生成交接包，不实现产品 KB，也不证明独立 Validation、发布或生产就绪。
# Stop Gate 运行依赖

使用当前 Python 环境（推荐独立虚拟环境）安装依赖后，直接检查 Stop Gate。此 smoke 使用合成证据，只证明安装包可执行，不代表真实 Goal 已完成。

```bash
python3 -m pip install -r .codex/skills/sge-governed-checkpoints/requirements.txt
python3 .codex/skills/sge-governed-checkpoints/scripts/stop_gate.py --help
python3 tools/stop_gate_smoke.py
```
