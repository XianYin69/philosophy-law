# scripts（脚本库）

英文名、可独立运行；除 PyYAML 外只用标准库。每个脚本对应流程中的一道校验关。

| 脚本 | 用途 | 挂载步骤 | 用法 |
|---|---|---|---|
| `validate_entries.py` | 条目 schema 校验：法条六要素（出处/条文号/年代/法域/效力状态/要旨）、哲学四要素（代表文本/核心命题/流派/后世批评）、推理卡 steps·must_answer·grade_scale，加 id 模式与枚举 | 知识检索、输出审查 | `python scripts/validate_entries.py [--domain law]` |
| `check_sources.py` | 条文与文献出处完整性 lint：缺 `source`/`text`、ref 无 url 且无 citation、url 未标 `url_status`、不确定措辞未标「待核」、二手转述冒充原文 | 出处核验、输出审查 | `python scripts/check_sources.py [--strict]` |
| `lint_refs.py` | 引用一致性：SKILL.md 与 branch/ 相对链接不得悬空、.md ≤ 50 行、文中 `scripts/*.py` 须存在、deps.json 每条须有 `source_url` | 输出审查 | `python scripts/lint_refs.py [--quiet]` |
| `grade_output.py` | 草稿结构校验：现状分析 11 项、独立思考 7 步、结论分级存在 | 现状分析、独立思考 | `python scripts/grade_output.py 草稿.md [--mode state\|think]` |
| `search_entries.py` | 关键词/域检索（`--brief` 即压缩取回） | 知识检索 | `python scripts/search_entries.py --q "汉谟拉比" --brief` |
| `new_entry.py` | 从模板生成新卡（默认 dry-run，`--yes` 落盘） | 知识检索 | `python scripts/new_entry.py --domain law --id law.x.y --yes` |
| `build_index.py` | 重算覆盖度并写 `asset/index/coverage.md` | 收尾 | `python scripts/build_index.py --yes` |
| `logic_note.py` | 判断节点留痕（逻辑链/过程链，写用户缓存目录） | 各判断节点 | `python scripts/logic_note.py add --frm 据 --to 论 --why 由` |
| `gc_tmp.py` | tmp 清点回收、扫 skill 目录缓存残留 | 收尾 | `python scripts/gc_tmp.py [--yes]` |
| `run_checks.py` | 一键全检（validate + sources + refs + index） | 输出审查 | `python scripts/run_checks.py` |
| `lint-deps.py` | 校验 deps.json：每条依赖须有 `source_url` 原始链接（本地技能 `local://<skill-id>`），缺即判不合格 | 收尾 | `python scripts/lint-deps.py` |
| `init-planned-tasks.py` | 从 template.json 生成 `pt-<skill>-<slug>.json` 计划任务声明（默认预览；执行权归 SMS 调度器，技能自身不执行） | 初始化、收尾 | `python scripts/init-planned-tasks.py --slug x --title y --input z --mode interval --yes` |

## 约定

- 退出码 `0` 通过 / `1` 有缺陷；缺陷清单以 JSON 打到 stdout（`ensure_ascii=False`），
  诊断信息走 stderr，故 stdout 恒为单一 JSON 文档。
- 无裸 `except`（只捕 `YAMLError`/`JSONDecodeError`/`OSError`），无 `print` 调试残留，
  源码行长 ≤ 100 字符。
- 缓存与链文件一律写用户缓存目录（`--store` 或 env `PHILAW_LOGIC_STORE`），
  不得落在 skill 目录内。
- `asset/templates/` 是占位模板，validate/check_sources 默认跳过（`--strict` 不改此约定）。

## 边界

脚本只做**形式与出处完整性校验**，不判定「要旨是否忠实于条文」「steelman 是否真的更强」——
那两类须人工/模型复核（见 [审查约束](../resistance/审查约束/审查约束.md)）。
