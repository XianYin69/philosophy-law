"""search_entries.py — 按关键词/域检索 asset/ 知识卡（上下文压缩取回）。

Usage: python scripts/search_entries.py --q "汉谟拉比" [--domain law]
       [--brief] [--limit 10] [--json]
Exit: 0 命中, 1 无命中。
"""
import argparse
import json

from _corpus import defect, emit, load_entries


def score(entry, needle):
    blob = json.dumps(entry, ensure_ascii=False)
    if needle.lower() in blob.lower():
        return blob.lower().count(needle.lower())
    return 0


def brief(entry):
    return {"id": entry.get("id"), "title": entry.get("title"),
            "domain": entry.get("domain"),
            "gist": str(entry.get("gist") or entry.get("thesis") or "")[:120],
            "verified": entry.get("verified"),
            "force_status": entry.get("force_status")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True)
    ap.add_argument("--domain", choices=["law", "philosophy", "reasoning"])
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    hits = []
    for path, _idx, ent in load_entries():
        if args.domain and ent.get("domain") != args.domain:
            continue
        s = score(ent, args.q)
        if s:
            row = brief(ent) if args.brief else dict(ent)
            row["_file"], row["_score"] = path, s
            hits.append(row)
    hits.sort(key=lambda r: -r["_score"])
    hits = hits[:args.limit]
    if not hits:
        return emit({"check": "search_entries", "query": args.q,
                     "hit_count": 0, "hits": []},
                    [defect("search", "asset/", "query",
                            "无命中：%s（本库无该节点数据，不得估算充数）" % args.q,
                            "见 asset/index/coverage.md 前沿")])
    return emit({"check": "search_entries", "query": args.q,
                 "hit_count": len(hits), "hits": hits}, [])


if __name__ == "__main__":
    raise SystemExit(main())
