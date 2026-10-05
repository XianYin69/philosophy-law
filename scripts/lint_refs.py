"""lint_refs.py — 引用一致性检查：相对链接不得悬空、.md ≤ 50 行、脚本引用须存在。

Checks:
  R1 markdown 相对链接目标必须存在（目录链接须含同名 .md 或索引文件）。
  R2 每个 .md ≤ 50 行（红线只约束 markdown 文本）。
  R3 文中提到的 `scripts/<name>.py` 必须真实存在。
  R4 deps.json 每条依赖必须带 source_url。
Usage: python scripts/lint_refs.py [--quiet]
Exit: 0 clean, 1 defects.
"""
import argparse
import json
import os
import re

from _corpus import (LINK_RE, ROOT, defect, emit, md_files, rel)

SCRIPT_RE = re.compile(r"scripts/([A-Za-z0-9_-]+\.py)")
DIR_OK = ("README.md", "index.md", "index.json")


def resolve(dir_link, base):
    target = os.path.normpath(os.path.join(base, dir_link.rstrip("/")))
    if os.path.exists(target) and not os.path.isdir(target):
        return target
    if os.path.isdir(target):
        stem = os.path.basename(target)
        cand = os.path.join(target, stem + ".md")
        if os.path.exists(cand):
            return cand
        for name in DIR_OK:
            if os.path.exists(os.path.join(target, name)):
                return os.path.join(target, name)
    return None


def check_md(path):
    out = []
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    if len(lines) > 50:
        out.append(defect("refs", rel(path), "length",
                          "markdown %d 行 > 50 行红线" % len(lines),
                          "拆分到子文档"))
    base = os.path.dirname(path)
    for target in LINK_RE.findall(text):
        t = target.split("#")[0].strip()
        if not t or t.startswith(("http://", "https://", "mailto:", "local://")):
            continue
        if resolve(t, base) is None:
            out.append(defect("refs", rel(path), "link",
                              "悬空链接 -> %s" % target,
                              "修正相对路径或补建目标"))
    for name in set(SCRIPT_RE.findall(text)):
        if not os.path.exists(os.path.join(ROOT, "scripts", name)):
            out.append(defect("refs", rel(path), "script",
                              "引用不存在的脚本 scripts/%s" % name,
                              "补脚本或改引用"))
    return out


def check_deps():
    out = []
    path = os.path.join(ROOT, "dependence", "deps.json")
    if not os.path.exists(path):
        return [defect("refs", "dependence/deps.json", "file",
                       "deps.json 缺失", "按 dependence.md 建清单")]
    data = json.load(open(path, encoding="utf-8"))
    deps = data.get("dependencies")
    if not isinstance(deps, list):
        return [defect("refs", "dependence/deps.json", "dependencies",
                       "dependencies 须为列表", "改结构")]
    for i, dep in enumerate(deps):
        tag = "dependence/deps.json#dependencies[%d]" % i
        if not isinstance(dep, dict):
            out.append(defect("refs", tag, "dep", "依赖项须为对象", "补字段"))
            continue
        url = (dep.get("source_url") or "").strip()
        if not url:
            out.append(defect("refs", tag, "source_url",
                              "依赖 %r 缺 source_url" % dep.get("name"),
                              "补原始链接；本地技能用 local://<skill-id>"))
        elif not re.match(r"^(https?://|local://|file://)", url):
            out.append(defect("refs", tag, "source_url",
                              "source_url=%r 协议非法" % url,
                              "用 http(s):// 或 local://"))
        for field in ("name", "license", "version", "install", "checked_at"):
            if not (dep.get(field) or "").strip():
                out.append(defect("refs", tag, field,
                                  "依赖 %r 缺 %s" % (dep.get("name"), field),
                                  "补字段"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    found = []
    for path in md_files():
        found += check_md(path)
    found += check_deps()
    report = {"check": "lint_refs", "md_files": len(md_files())}
    if args.quiet:
        report["defects"] = [d["where"] + ": " + d["message"] for d in found]
    else:
        report["defects"] = found
    return emit(report, found)


if __name__ == "__main__":
    raise SystemExit(main())
