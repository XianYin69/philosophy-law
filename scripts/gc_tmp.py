"""gc_tmp.py — 垃圾回收：tmp 草稿/镜像的清点与释放（默认 dry-run）。

约定：tmp/ 只放草稿与镜像；交付后清理。skill 目录内不得留缓存文件。
Usage: python scripts/gc_tmp.py [--tmp <dir>] [--yes]
Exit: 0 ok, 1 发现 skill 目录内的缓存残留。
"""
import argparse
import os

import _corpus
from _corpus import add_root_arg, apply_root, defect, emit

CACHE_PATTERNS = (".tmp", ".bak", ".orig", ".log", ".pyc")
CACHE_DIRS = ("__pycache__",)


def is_cache(name):
    return name.endswith(CACHE_PATTERNS) or name in CACHE_DIRS


def scan_tmp(tmp):
    rows = []
    if not os.path.isdir(tmp):
        return rows
    for dirpath, dirnames, filenames in os.walk(tmp):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rows.append({"path": os.path.relpath(full, _corpus.ROOT).replace(os.sep, "/"),
                         "bytes": os.path.getsize(full)})
    return rows


def scan_skill_caches():
    hits = []
    for dirpath, dirnames, filenames in os.walk(_corpus.ROOT):
        if os.path.basename(dirpath) == ".git":
            dirnames[:] = []
            continue
        for name in list(dirnames):
            if is_cache(name):
                hits.append(os.path.join(dirpath, name))
        for name in filenames:
            if is_cache(name):
                hits.append(os.path.join(dirpath, name))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmp", default=None)
    ap.add_argument("--yes", action="store_true")
    add_root_arg(ap)
    args = ap.parse_args()
    apply_root(args)
    if args.tmp is None:
        args.tmp = os.path.join(_corpus.ROOT, "tmp")
    rows = scan_tmp(args.tmp)
    caches = scan_skill_caches()
    found = [defect("gc", os.path.relpath(p, _corpus.ROOT).replace(os.sep, "/"),
                    "cache", "skill 目录内缓存残留", "删除或移入用户缓存目录")
             for p in caches]
    removed = 0
    if args.yes:
        for row in rows:
            full = os.path.join(_corpus.ROOT, row["path"].replace("/", os.sep))
            if os.path.isfile(full):
                os.remove(full)
                removed += 1
    return emit({"check": "gc_tmp", "tmp": args.tmp,
                 "mode": "write" if args.yes else "dry-run",
                 "tmp_files": [r["path"] for r in rows],
                 "tmp_bytes": sum(r["bytes"] for r in rows),
                 "removed": removed,
                 "skill_cache_hits": len(caches)}, found)


if __name__ == "__main__":
    raise SystemExit(main())
