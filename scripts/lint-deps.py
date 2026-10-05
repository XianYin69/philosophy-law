"""lint-deps.py — 校验 dependence/deps.json 的依赖清单完整性。

每条依赖必须带 `source_url` 原始链接（GitHub/GitLab/官方仓库或发布页；
本地技能用 `local://<skill-id>`）；缺 source_url 即判不合格并报错退出。
Usage: python scripts/lint-deps.py [--path dependence/deps.json]
Exit: 0 合格, 1 不合格。
"""
import argparse
import json
import os
import re

import _corpus
from _corpus import add_root_arg, apply_root, defect, emit

REQUIRED_FIELDS = ("name", "source_url", "license", "version", "install",
                   "checked_at")
URL_OK = re.compile(r"^(https?://|local://|file://)")
DATE_OK = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def check(path):
    out = []
    if not os.path.exists(path):
        return [defect("deps", os.path.relpath(path, _corpus.ROOT), "file",
                       "deps.json 缺失", "按 dependence/dependence.md 建清单")]
    try:
        data = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [defect("deps", os.path.relpath(path, _corpus.ROOT), "json",
                       "deps.json 不是合法 JSON：%s" % str(exc)[:120],
                       "修 JSON")]
    deps = data.get("dependencies")
    if not isinstance(deps, list):
        return [defect("deps", "dependence/deps.json", "dependencies",
                       "dependencies 须为列表", "改结构")]
    if not deps:
        out.append(defect("deps", "dependence/deps.json", "dependencies",
                          "清单为空：本技能至少依赖 Python 与 PyYAML",
                          "补依赖条目"))
    for i, dep in enumerate(deps):
        tag = "dependence/deps.json#dependencies[%d]" % i
        if not isinstance(dep, dict):
            out.append(defect("deps", tag, "dep", "依赖项须为对象", "补字段"))
            continue
        url = str(dep.get("source_url") or "").strip()
        if not url:
            out.append(defect("deps", tag, "source_url",
                              "依赖 %r 缺 source_url（判不合格）" % dep.get("name"),
                              "补原始链接；本地技能用 local://<skill-id>"))
        elif not URL_OK.match(url):
            out.append(defect("deps", tag, "source_url",
                              "source_url=%r 协议非法" % url,
                              "用 http(s):// 或 local://"))
        elif url.startswith("local://"):
            ref = url[len("local://"):]
            home = os.environ.get("KILO_SKILLS_DIR") or os.path.join(
                os.path.expanduser("~"), ".kilocode", "skills")
            if not os.path.isdir(os.path.join(home, ref)):
                out.append(defect("deps", tag, "source_url",
                                  "local://%s 在技能目录内不存在" % ref,
                                  "改指向真实本地技能"))
        for field in REQUIRED_FIELDS:
            val = dep.get(field)
            if not (isinstance(val, str) and val.strip()):
                out.append(defect("deps", tag, field,
                                  "缺字段 %s" % field, "补 %s" % field))
        checked = str(dep.get("checked_at") or "")
        if checked and not DATE_OK.match(checked):
            out.append(defect("deps", tag, "checked_at",
                              "checked_at=%r 非 YYYY-MM-DD" % checked,
                              "改本地日期"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=None)
    add_root_arg(ap)
    args = ap.parse_args()
    apply_root(args)
    if args.path is None:
        args.path = os.path.join(_corpus.ROOT,
                                                            "dependence",
                                                            "deps.json")
    found = check(args.path)
    return emit({"check": "lint-deps",
                 "deps": os.path.relpath(args.path, _corpus.ROOT)}, found)


if __name__ == "__main__":
    raise SystemExit(main())
