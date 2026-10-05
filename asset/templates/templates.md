# templates（交付空白卡）

复制使用，填完再跑校验。

## 法条卡

见 [`entry-law.yaml`](entry-law.yaml)：`source / article / era / jurisdiction /
force_status / gist / refs / verified`。

## 哲学卡

见 [`entry-phil.yaml`](entry-phil.yaml)：`text / thesis / school / criticism`。

## 现状分析稿

见 [`current-state.md`](current-state.md)：六必答项 + 时效 + 不确定性 + 转介提示。

## 独立思考稿

见 [`independent-think.md`](independent-think.md)：立场澄清 → steelman →
己方论证 → 自我反驳 → 前提依赖与推翻条件 → 结论分级。

## 填写规则

- 不能确证 → 写 `待核`，不得留空。
- `refs` 至少一条，标 tier（T1–T4）。
- 草稿放 `tmp/`，经 `python scripts/new_entry.py --yes` 落入 `asset/`。

## 校验

```
python scripts/validate_entries.py
python scripts/grade_output.py tmp/draft.md
```

## 相关

- [schema](../schema/entry.schema.md)
- [机制兜底](../../resistance/机制兜底/机制兜底.md)
