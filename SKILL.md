---
name: 哲学法律
version: 0.1.0
description: >
  哲学与法律双域知识库与推理框架：各国从古至今的法典条文（出处/条文号/年代/法域/
  效力状态/要旨）、从苏格拉底到当代的哲学（代表文本/核心命题/流派/后世批评），
  配「现状分析」「独立思考」两个子技能，区分应然与实然，给出可推翻条件与结论分级。
license: MIT
metadata:
  category: humanities
---

# 哲学法律

使用 `哲学法律` skill 来完成用户请求。

## 工作原则

1. **出处优先**：条文/命题须带可核出处（T1 原文 > T2 校勘译本 > T3 研究文献 > T4 通识）；确证不了的年代或条号显式标「待核」，禁止编造。
2. **应然/实然分离**：规范文本与当下事实并置而不混同；事实须给来源、统计口径与信息时效。
3. **不迎合**：先重构对手最强论证（steelman），再给己方论证与自我反驳，结论分级 强/中/弱/存疑。
4. **学理边界**：敏感议题只作学理与制度分析；不作个案法律意见，结尾提示咨询执业律师。

## 执行路径

[知识检索](branch/流程/知识检索/知识检索.md) → [出处核验](branch/流程/出处核验/出处核验.md) →
[条文引用](branch/流程/条文引用/条文引用.md) → [法域比较](branch/流程/法域比较/法域比较.md) →
[现状分析](branch/流程/现状分析/现状分析.md) → [独立思考](branch/流程/独立思考/独立思考.md) →
[输出审查](branch/流程/输出审查/输出审查.md) → 交付

主干索引：[branch/流程/](branch/流程/流程.md)；兜底约束：[resistance/](resistance/resistance.md)

## 子技能

- [现状分析](现状分析/SKILL.md)：制度运行现状·争议焦点·利益相关方·可比法域参照·趋势与不确定性。
- [独立思考](独立思考/SKILL.md)：steelman → 己方论证 → 自我反驳 → 前提依赖与推翻条件 → 分级。

## 可用工具（scripts/）

`validate_entries.py`、`check_sources.py`、`lint_refs.py`、`grade_output.py`、
`search_entries.py`、`build_index.py`、`run_checks.py`——清单见 [scripts](scripts/scripts.md)。

## 知识·依赖·计划任务

[asset/](asset/asset.md)（185 卡：法条 94 / 哲学 89 / 推理 2）· [deps.json](dependence/deps.json) · [planned_tasks/](planned_tasks/README.md) · [CHANGELOG](CHANGELOG.md)

## 红线摘要

不得编造条文出处或哲学文献；无法确证须标「待核」且不得参与结论承重；二手转述不得当原文；
跨法域比较须注语境差异；不作个案法律意见；所有 .md ≤ 50 行、悬空链接 = 0；缓存不入 skill 目录。
