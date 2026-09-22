# Core-only initial KB bootstrap

运行 `scripts/initial_kb_bootstrap.py build` 生成 machine-readable recipe packet；随后分别运行 `validate` 与 `render`。默认只写 stdout，只有显式 `--output` 才写文件，并拒绝覆盖已有 artifact。

最小交付包括 canonical JSON source、deterministic reader projection、provenance 与 limitations。Goal missing 时返回 `goal_required`，不得直接进入 Builder。`doc-system-kb-builder` 等扩展只可作可选 adapter；缺失时继续 core recipe，不安装、不联网、不提升权限。

输出是可执行 handoff 模板，不代表业务 ontology、产品 KB implementation、独立 Validation、release 或 promotion 已完成。
