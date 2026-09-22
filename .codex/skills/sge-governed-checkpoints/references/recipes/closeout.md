# Closeout、KB/Dashboard 与 BDD recipe

1. 写中文 closeout：落地范围、非目标、lanes/例外、Design/Validation handoff、verdict、证据、gates、Semantic、延后范围、KB/Dashboard 与 next candidate。
2. 证据正文使用可点击 Markdown 源文件链接；hash 留给 machine artifact，不作为唯一人类入口。
3. 运行 closeout-language；H1/H2 中文且英文状态有中文解释。
4. stable rule 做 Contract Delta Scan 并落 canonical KB JSON；state/decision/blocker/closeout/follow-on 落 Dashboard。
5. maintained behavior gate 变化同步 BDD；reader cards 写入受版本控制路径。
6. 更新 Session registry 后运行 reconcile check 与 validate；可重建 drift 才 apply 后复验。
7. final-state Validation 与 post-closeout reconciliation 后再决定 terminal；随后执行 next-session scan。

closeout、handoff、Dashboard Agent 模板扩读 `../checklists.md`。
