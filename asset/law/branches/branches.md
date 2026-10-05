# branches（程序法与部门法）

按部门切分的知识节点，每部门一卡（`branches.yaml`），必要时下钻到具体法源。

## 覆盖

| 部门 | 典型法源 | 卡 id 前缀 |
|---|---|---|
| 宪法 | 各国宪法、违宪审查制度、基本权利教义 | `law.branch.constitutional.*` |
| 行政法 | 行政行为、程序法典、司法审查密度 | `law.branch.administrative.*` |
| 民商法 | 民法典、债法总则、公司法、破产法 | `law.branch.civilcommercial.*` |
| 刑事法 | 刑法典、罪刑法定、量刑与执行 | `law.branch.criminal.*` |
| 诉讼法 | 民事/刑事/行政诉讼程序、证据规则 | `law.branch.procedure.*` |
| 劳动法 | 劳动契约、集体协商、ILO 公约 | `law.branch.labor.*` |
| 知识产权 | 版权、专利、商标、WIPO 与 TRIPS | `law.branch.ip.*` |
| 国际公法 | 联合国宪章、条约法、国家责任、法院规约 | `law.branch.publicintl.*` |
| 国际私法 | 法律适用、管辖、判决承认执行、海牙体系 | `law.branch.privateintl.*` |

## 数据文件

[`branches.yaml`](branches.yaml)

## 下钻原则

部门卡只给「法源地图 + 核心原则 + 争议点」；具体条文进 `codes/` 对应卡，
用 `related` 双向链接。

## 相关

- [law 总览](../law.md) · [systems](../systems/systems.md)
