# asset（知识底座）

双域知识树 + 两类推理模板。所有条目为 YAML 数据卡，供脚本校验与检索。

## 结构

- [`schema/`](schema/entry.schema.md)：条目格式（法条卡 / 哲学卡 / 推理卡）。
- [`law/`](law/law.md)：知识域一——各国从古至今法典与条文、法系、部门法。
- [`philosophy/`](philosophy/philosophy.md)：知识域二——从苏格拉底到现在的哲学。
- [`reasoning/`](reasoning/reasoning.md)：现状分析与独立思考的模板与检查表。
- [`index/`](index/coverage.md)：覆盖度与拓扑前沿（哪些节点仍可继续展开）。
- [`templates/`](templates/templates.md)：交付用的空白卡。

## 分层原则

域 → 传统/时代 → 法典/文本 → 编章条/命题 → 注释与批评。
穷尽标准：任一节点还能按「时间、地域、学派、部门」任一维度切分出
有独立出处的子节点，即视为可再拓扑，须继续展开并记入 `index/coverage.md`。

## 校验

```
python scripts/validate_entries.py
python scripts/check_sources.py
python scripts/build_index.py
```

## 注意

条目 `gist` 是要旨，不是原文；引用原文须回查 `refs` 中的 T1/T2 来源。
