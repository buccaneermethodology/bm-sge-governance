# SGE Governance Skill 中文新手指南

本指南帮助一个没有既有项目背景的新仓库建立最小治理循环。完成这些步骤，只能说明该仓库已经拥有可运行的治理骨架；不能说明产品正确、已经发布或生产就绪。

## 1. 先检查候选包

在候选仓库根目录运行：

```bash
python3 tools/sge_public.py doctor
```

看到 `public_doctor:pass` 表示 manifest 中每个公开文件都存在、许可证字段完整且没有命中的私有身份残留。

## 2. 导出干净公共候选

在候选仓库根目录运行，目标目录必须不存在或为空：

```bash
python3 tools/sge_public.py export /tmp/sge-public-candidate
```

成功输出形如 `exported:<文件数>:/tmp/sge-public-candidate`；文件数以当前 manifest 为准。普通用户应先 clone 当前公开仓并在该目录运行安装命令，工具默认把当前公开仓作为 source；`--source` 只用于维护者或测试 alternate source，不是普通用户必需参数。

## 3. 建立最小项目

```bash
python3 tools/sge_public.py bootstrap /tmp/my-sge-project
```

该命令只写入新的空目录，生成 `AGENTS.md`、项目 profile、Dashboard 最小表面和 README。若目录非空，命令会失败，避免覆盖已有项目。

## 4. 安装 core Skill

```bash
cd /tmp/sge-public-candidate
python3 tools/sge_public.py install \
  --target /tmp/my-sge-project
```

成功输出形如 `installed:17:/tmp/my-sge-project`。普通用户不需要指定 `--source`：命令从当前公开仓目录读取 source；`--source` 只用于维护者、高级诊断或测试 alternate source。安装只复制 manifest 允许的 `.codex/skills/sge-governed-checkpoints/` 文件，并写入包含 candidate、source/manifest identity、文件摘要、写入范围和 target 路径的 install record。目标项目自己的 `AGENTS.md`、`kb/`、`Dashboard/`、Goal 和 Session 仍是该项目的 authority，安装不会覆盖这些表面。

## 5. 升级并确认可恢复备份

当 staging 中出现经过审查的新候选时运行：

```bash
python3 tools/sge_public.py upgrade \
  --target /tmp/my-sge-project
find /tmp/my-sge-project/.sge-backups -name SKILL.md -print
```

成功输出形如 `upgraded:17:/tmp/my-sge-project`，随后 `find` 应至少显示一个旧 core 的 `SKILL.md`。若新版本有问题，从打印出的 `.sge-backups/<timestamp>/...` 路径恢复。升级先保存旧 core 的文件摘要与 backup tree 摘要；复制或记录写入失败时会自动恢复旧 core，原 install record 仍保持有效。这只保证本地事务性的可恢复行为，不是跨平台升级保证。

## 6. 跑一个最小 Goal

可复制提示：

```text
/goal 请在当前仓库建立一个最小、可验证的 Goal。先读取 AGENTS.md 与项目 profile，明确原始目标、非目标、claim ceiling、一个 Session、Validation Handoff 和终止条件；不要把计划落库表述为实现完成。
```

Session 执行提示：

```text
执行当前 Goal 的第一个 ready Session。先做 Task Intake 和 Context Bootstrap；若是非平凡改动，按 lane card 启动 Design、Builder、Validation、Closure，并在 closeout 中说明做了什么、不证明什么。
```

独立验证提示：

```text
作为独立 Validation lane，从 durable inputs 重算结果；同时检查原始 Goal 与当前设计，列出已读/未读证据、blocking findings、claim ceiling、KB/Dashboard truth split 和最终 verdict。不要修改 Builder 产物。
```

## 7. 故障恢复

- `destination_must_be_empty`：换一个空目录，或先人工检查现有目录；工具不会覆盖。
- `identity_or_private_residue`：定位 manifest 报告的文件和 token，移出公共候选或给出经审查的公开裁决。
- `uninstall_requires_install_record`：目标不是由本工具安装，工具拒绝猜测删除范围。
- 升级失败：工具会在目标项目 `.sge-backups/` 保存旧 core，再写新版本；运行 `find /tmp/my-sge-project/.sge-backups -name SKILL.md -print` 定位可恢复副本。

## 8. 卸载

```bash
python3 /tmp/sge-public-candidate/tools/sge_public.py uninstall --target /tmp/my-sge-project
```

卸载把已安装 core 移到目标项目 `.sge-trash/`，并把 install record 移为同一时间戳目录下的 `install-record.json`；不删除项目自己的 KB、Dashboard 或 AGENTS.md。需要时可将 core 与 record 一起手工移回。工具只处理自己记录的 core surface；缺少 install record、target layout 不安全或 core 被替换为 symlink 时会拒绝猜测删除范围。

## 9. 边界说明

本指南描述的是当前本地公开 source 的 candidate lifecycle evidence：`doctor`、安装、升级、备份、失败回滚和可恢复卸载。它不证明 GitHub 公开仓已创建或发布，不授予 push/tag/release 权限，也不证明跨平台兼容、license 再分发权或 production readiness。

## 10. 不依赖外部 Skill 的初始 KB 路径

core 内的 `initial_kb_bootstrap.py` 会把原始目标、authority、Goal route、canonical JSON、reader projection、provenance、lanes、Validation 与 closeout 组合成可校验 packet。默认只输出到屏幕；指定 `--output` 时也拒绝覆盖已有文件。

先运行 `first_task_router.py`：若没有 Goal，结果为 `goal_required`，此时先写 Goal，不能直接开始 Builder；若声称已有 Goal，必须提供唯一的 Goal ID 与仓库相对路径，否则按 authority conflict 停止。再运行 `capability_preflight.py`：`doc-system-kb-builder` 等 adapter 是 optional；明确不可用时继续 core recipe，unknown 或非法状态则失败关闭。此路径只证明本地 core recipe 可运行，不证明产品事实已生成、KB 已完成或不同 Agent 行为一致。
