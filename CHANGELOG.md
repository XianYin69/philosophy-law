# CHANGELOG

本技能（哲学法律）的版本与变更履历。格式参照 Keep a Changelog；日期为本地日期。

## [0.1.1] - 2026-10-05

### 修改（Skill_Generator 修改路径）

- `SKILL.md`：`description` 由模板残留「Auto-generates and iterates Agent Skills」改写为
  哲学法律自身领域描述；`metadata.category` 由 `development` 改为 `humanities`；
  正文补齐 工作原则／执行路径／子技能／可用工具／知识·依赖·计划任务／红线摘要 六段。
- `scripts/`：新建脚本库（此前完全缺失）——`validate_entries.py`（条目 schema 校验）、
  `check_sources.py`（出处完整性 lint）、`lint_refs.py`（引用一致性/悬空链接/≤50 行/deps 校验）
  三个必需脚本，另补 `grade_output.py`、`search_entries.py`、`new_entry.py`、
  `build_index.py`、`logic_note.py`、`gc_tmp.py`、`run_checks.py`、共享模块 `_corpus.py`
  与索引 `scripts/scripts.md`；此前各 .md 引用的脚本名全部落地，无悬空引用。
- `现状分析/`、`独立思考/`：由 `branch/流程/` 下的流程节点提升为与本体平级的子技能，
  各含 `SKILL.md`（YAML frontmatter）＋ `branch/` ＋ `resistance/`；
  原流程节点保留并改为指向子技能的索引，链接不悬空。
- `asset/`：修复 16 个 YAML 文件的标量引号问题（含 `: ` 或以 `"` 开头的未加引号标量导致
  `yaml.safe_load` 失败，29 文件 185 条目现全部可解析）；`verified: yes/no` 加引号
  避免被读成布尔值（15 处）；`law.china.xinlü` → `law.china.xinlv`（id 须匹配 ASCII 模式）；
  `law.civil.turkey1926` 补 `article`（写「条号待核」，不编造条数）。知识内容未改动。
- `dependence/deps.json`：由空清单补为 7 条依赖，每条含 `source_url` 原始链接
  （本地技能用 `local://`）；`LICENSE`（MIT）与 `planned_tasks/README.md`＋`template.json` 原位核查通过。
- 链接：修正 10 个 .md 内的相对路径深度错误（含 `../../../planned_tasks/`、
  `branch/branch.md` 的 `../../SKILL.md` 等），悬空链接归零。
- 新增本 `CHANGELOG.md`（此前 `resistance/resistance.md` 与 `SKILL.md` 已引用但不存在）。

### 未改动（按指令保留）

- `asset/` 知识树结构（law / philosophy / reasoning / schema / templates / index）与全部条目内容。
- `resistance/` 各约束目录内容（仅修链接）。

## [0.1.0] - 2026-10-05

- 初建：双域知识树（法条 94 / 哲学 89 / 推理 2 卡）、七节点主干流程、
  `resistance/` 六类约束、`dependence/`、`planned_tasks/`、`agent/` 四格式提示词、MIT `LICENSE`。
