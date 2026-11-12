# 统一执行入口与现态恢复合同

_Owner: SGE governance | Version: 1.0.0 | Status: active | Updated: 2026-10-29_

## 界面与权威

- workflow_entry.py 是 prepare/check/run/resume 四命令薄入口。manifest 只记录引用、摘要类型、命令与依赖，不生成 authority、批准、独立 verdict 或终态。旧 CLI 与 Stop Gate authority 路由保持不变。
- 所有路径以显式绝对 repo 为根，其他路径相对且解析 symlink 后不得越界。任务对象和 card 的身份、Session、AC、写域、输出、声明上限逐项比较；历史 dependency/background 引用不替换当前身份。

## 冻结与失效

- raw_bytes 为原字节 SHA-256；canonical_json 使用 UTF-8、ensure_ascii=False、sort_keys=True、separators=(逗号,冒号)。card 总体为规范化摘要，旧 refs 保留原字节规则。
- prepare 校验旧 card/Context，自动绑定关键来源，复制 inputs，stage 完整且 seal 校验后原子发布。相同输入不改字节，冲突不覆盖；相关 authority/source/topology 变化失效，明确 background 无关追加不失效。seal 不是外部签名或宿主身份认证。

## 执行与恢复

- 命令只接受预声明 argv/cwd/checkpoint/action/target。check/false 不消费写准入；builder/install/upgrade/release/deploy 必须 true 且运行前消费旧 admission。命令只读性由配置作者及独立审查负责，不作任意程序副作用静态分析。
- state_sources 引用既有 task-bound findings/work_units/review_budget 和 snapshot baseline/current，不新增手工平行账本。baseline 冻结，其余现态每次 resume 重读并记录 observation。缺失/类型/身份错配为 unknown，不回退嵌入静态数组，ready 工作清空。
- 旧 context_state.compare_snapshots 结果原样传播；review_budget_preflight.evaluate_budget 保留原 lineage/events；缺源先 inspect_state_sources，stale 或 rebaseline_required 要求 rebaseline；连续两个无贡献单元要求诊断，不自动暂停。

## 支持判断与生命周期

- finding 精确行段和 quote 只证明定位；assertion/observation/impact 与独立 confirmation 绑定才可列 confirmed_blocker。宿主身份与原文语义仍由独立 Reviewer 确认。
- closed 是既有 finding 来源生命周期，投影保留 closed 且 confirmed_blocker=false；支持判断 pending/needs_evidence/needs_review/unsupported/confirmed 不得覆盖关闭生命周期。
- design/implementation/integration/independent_validation 分层 unknown/valid/stale，文件存在不推通过。done 工作需当前证据类型化摘要匹配才能释放依赖，仍不替代原 AC 独立验收。

## 声明与部署边界

- API 或 CLI pass 仅证明该操作范围成功；自测不等于独立验收，机制验收不等于产品试点或完整 Goal 完成。无宿主 hook 只承诺入口内。
- 默认 Skill 准备/委派/恢复路径引用操作说明。公共发布 exact allowlist 含入口、schemas、reference 和全部旧工具依赖，临时安装副本实际运行四命令后才能声明安装可用；不因此宣称发布或生产适用。

## Source Scope

- `统`
- `一`
- `执`
- `行`
- `入`
- `口`
- `的`
- `输`
- `入`
- `绑`
- `定`
- `、`
- `现`
- `态`
- `适`
- `配`
- `与`
- `声`
- `明`
- `边`
- `界`
