# entry.schema（条目格式）

三类卡，字段名固定，`scripts/validate_entries.py` 按此校验。

## 一、法条卡（domain: law）

必填：`id` `title` `source` `article` `era` `jurisdiction` `force_status` `gist` `refs` `verified`
可选：`original_quote` `translator` `amended` `related` `degraded` `last_checked`

- `force_status` ∈ `现行` / `被修订` / `已废` / `历史法源` / `待核`
- `verified` ∈ `yes` / `partial` / `no`
- `refs[]` 每项：`tier`（T1–T4）+ `url` 或 `citation`

## 二、哲学卡（domain: philosophy）

必填：`id` `title` `text`（代表文本） `thesis`（核心命题） `school`（流派）
`criticism`（后世批评，列表） `refs` `verified`
可选：`date` `terms` `influence` `degraded` `last_checked`

- `criticism` 至少 1 项，每项含 `by`（批评者）与 `claim`（其论点）。

## 三、推理卡（domain: reasoning）

用于现状分析与独立思考的检查表，必填：
`id` `title` `steps`（有序列表） `must_answer`（必答项） `grade_scale`。

## 通用约定

- `id` 形如 `law.ancient.hammurabi`、`phil.antique.plato.republic`。
- 不能确证的字段值写 `待核`，不得留空、不得猜测。
- 一卡一议题；跨域关联用 `related: [id]`。

## 相关

- [asset 总览](../asset.md) · [templates](../templates/templates.md)
