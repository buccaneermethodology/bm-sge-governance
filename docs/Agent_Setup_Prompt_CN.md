# 通过 Agent 安装和初始化 SGE Governance Skill

这是一段可以复制给任意 coding agent 的初始化 Prompt。它不依赖特定模型、Agent 产品或业务类型。

## 使用前的最小准备

用户只需要完成以下准备：

1. 安装 `git` 和 Python 3，并确保 Agent 可以运行 shell 命令。
2. 建立一个产品项目目录。
3. 将 Agent 的工作目录设置为这个项目目录。
4. 该目录必须为空。若 macOS 自动生成了 `.DS_Store`，应先移走它；不要让 Agent 删除真实项目文件。
5. Agent 需要能够访问官方公开 SGE 仓库：`https://github.com/buccaneermethodology/bm-sge-governance.git`。

## 可复制 Prompt

```text
你是当前项目的 SGE Governance Skill 安装与初始化 Agent。

目标：
把当前工作目录初始化为一个可以使用 SGE Governance Skill 的、产品无关的项目治理仓库。
本次只做安装、初始化、检查和交接，不实现任何具体产品功能。

外部输入：
- 官方公开 SGE 仓库地址：https://github.com/buccaneermethodology/bm-sge-governance.git
- 目标项目目录：当前工作目录

安全边界：
1. 先读取当前目录并列出所有文件，包括隐藏文件。
2. 如果当前目录包含任何用户真实文件、目录、符号链接或未知内容，停止并报告；不要删除、覆盖、移动或重命名它们。
3. 如果当前目录只有 macOS `.DS_Store`，可以把它移动到系统临时目录作为可恢复备份，然后继续；不得因此把任意隐藏文件都视为可忽略。
4. 不要使用当前 Agent 产品专属命令；只使用通用的 Git、Python 3 和文件系统能力。
5. 不要把具体产品名称、产品代码、产品 KB、产品测试或其他项目的历史 Dashboard 复制进当前项目。
6. 不要把“安装成功”表述为产品已经实现、测试通过、发布或生产就绪。

执行步骤：
1. 检查 `git --version`、`python3 --version` 和官方仓库地址是否可用。缺少依赖或网络不可用时停止并说明恢复方法。
2. 将官方公开仓库浅克隆到一个系统临时目录，不要把它克隆到当前项目目录中。
3. 在源仓库中运行其公开候选自检入口：
   `python3 tools/sge_public.py doctor`
   如果失败，停止；不要绕过 doctor，也不要自行修改源仓库。
4. 使用源仓库的公开工具初始化当前项目：
   `python3 tools/sge_public.py bootstrap <当前项目绝对路径>`
5. 使用同一个源仓库安装核心治理 Skill：
   `python3 tools/sge_public.py install --target <当前项目绝对路径>`
6. 检查以下内容存在且可读：
   - `AGENTS.md`
   - `.codex/skills/sge-governed-checkpoints/SKILL.md`
   - 项目 profile
   - `Dashboard/`
   - `kb/`（如果 bootstrap 合同包含该目录）
   - 安装记录（如果工具生成）
7. 从当前项目目录运行治理入口：
   `python3 .codex/skills/sge-governed-checkpoints/scripts/workflow_contract.py --stage full`
   `python3 .codex/skills/sge-governed-checkpoints/scripts/guardrail_checklist.py --mode intake-evaluation`
8. 创建一份简短的中文初始化检查记录，放入当前项目的 `Dashboard/Artifacts/`。记录：源仓库、实际执行的命令、通过项、未证明项、已知限制和第一条 Goal 的建议。
9. 输出一段可复制的第一条 Goal Prompt，但不要自动开始产品实现。

异常处理：
- 目标目录非空：停止，列出阻断文件及原因；不要清空目录。
- `doctor` 失败：停止，保留当前目录不变，并报告失败输出。
- `bootstrap`、`install` 或验证失败：如果工具已提供备份或回滚机制，先使用其机制；否则停止并报告，不要手工猜测删除范围。
- 任何路径、仓库身份、许可证或公开边界不明确：停止并请求人工确认。

最终报告必须用中文，并分成：
1. 已完成的安装与初始化；
2. 证据与命令；
3. 尚未证明的内容；
4. 当前项目的下一步 Goal Prompt；
5. 需要人工决定的事项。
```

## 这段 Prompt 的能力边界

它只能建立治理骨架并完成有界的本地安装检查。它不证明具体产品正确、不替代独立 Validation、不授予发布权限，也不保证所有操作系统和所有 Agent 产品的兼容性。公开仓地址已经固定为本 Prompt 中列出的官方地址；Agent 不应自行猜测或替换为其他仓库。
