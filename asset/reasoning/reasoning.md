# reasoning（推理模板卡）

两类子技能的数据化检查表，供 `scripts/grade_output.py` 与人工复核共用。

## 文件

- [`current-state.yaml`](current-state.yaml)：现状分析（应然/实然并置）。
- [`independent-thinking.yaml`](independent-thinking.yaml)：独立思考（steelman + 分级）。

## 用法

1. 起草时按 `steps` 顺序写小标题（中文标题可译，但顺序与要素不得少）。
2. 交付前 `python scripts/grade_output.py 草稿.md`，缺项即 FAIL。
3. `must_answer` 用于自检：任一必答项空缺 → 走
   [降级策略](../../resistance/降级策略/降级策略.md)。

## 分级口径（两卡共用）

| 级别 | 含义 |
|---|---|
| 强 | 多源一致、无有效反驳、前提为公理性事实 |
| 中 | 主流立场但有实质反对意见，前提可辩护 |
| 弱 | 依赖单一来源或争议前提 |
| 存疑 | 数据缺口或 `verified: partial/no` 占主导 |

## 相关

- [现状分析节点](../../branch/流程/现状分析/现状分析.md)
- [独立思考节点](../../branch/流程/独立思考/独立思考.md)
