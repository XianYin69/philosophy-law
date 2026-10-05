"""build_index.py — 重算 asset/ 覆盖度并写 asset/index/coverage.md（计数勿手改）。

Usage: python scripts/build_index.py [--yes]
Exit: 0 ok, 1 无法写出（缺目录）。
"""
import argparse
import collections
import os

from _corpus import (ASSET, ROOT, defect, emit, load_entries, rel)

OUT = os.path.join(ASSET, "index", "coverage.md")
HEAD = "# coverage（覆盖度与拓扑前沿）\n\n"


def tally():
    stats = collections.defaultdict(lambda: {"files": set(), "entries": 0,
                                             "yes": 0, "partial": 0,
                                             "no": 0, "daikeng": 0})
    for path, _idx, ent in load_entries():
        domain = ent.get("domain") or "unknown"
        row = stats[domain]
        row["files"].add(path)
        row["entries"] += 1
        verified = str(ent.get("verified"))
        if verified in ("yes", "True"):
            row["yes"] += 1
        elif verified == "partial":
            row["partial"] += 1
        elif verified in ("no", "False"):
            row["no"] += 1
        blob = " ".join(str(v) for v in ent.values())
        row["daikeng"] += blob.count("待核")
    return stats


def render(stats, old):
    lines = [HEAD]
    lines.append("由 `python scripts/build_index.py` 重算，勿手改计数。\n\n")
    lines.append("## 当前状态（脚本重算）\n\n")
    lines.append("| 域 | 文件数 | 条目数 | verified=yes | partial | no | 「待核」出现次数 |\n")
    lines.append("|---|---|---|---|---|---|---|\n")
    for domain in sorted(stats):
        row = stats[domain]
        lines.append("| %s | %d | %d | %d | %d | %d | %d |\n" % (
            domain, len(row["files"]), row["entries"], row["yes"],
            row["partial"], row["no"], row["daikeng"]))
    total = sum(r["entries"] for r in stats.values())
    lines.append("\n合计条目 %d；数据文件 %d 个。\n" % (
        total, len({f for r in stats.values() for f in r["files"]})))
    cut = old.find("## 可再拓扑的节点（前沿）")
    if cut >= 0:
        lines.append("\n" + old[cut:])
    else:
        lines.append("\n## 可再拓扑的节点（前沿）\n\n"
                     "待人工补录（判定标准见 asset/asset.md 分层原则）。\n")
    return "".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()
    stats = tally()
    old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    text = render(stats, old)
    if not args.yes:
        return emit({"check": "build_index", "mode": "dry-run",
                     "out": rel(OUT), "domains": sorted(stats),
                     "preview_lines": len(text.splitlines())}, [])
    if not os.path.isdir(os.path.dirname(OUT)):
        return emit({"check": "build_index", "mode": "write"},
                    [defect("index", rel(OUT), "dir",
                            "缺目录，无法写出", "补 asset/index/")])
    tmp = OUT + ".tmp"
    open(tmp, "w", encoding="utf-8", newline="\n").write(text)
    os.replace(tmp, OUT)
    return emit({"check": "build_index", "mode": "write",
                 "out": rel(OUT), "lines": len(text.splitlines()),
                 "domains": sorted(stats)}, [])


if __name__ == "__main__":
    raise SystemExit(main())
