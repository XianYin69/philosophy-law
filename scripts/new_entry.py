"""new_entry.py — 从 asset/templates/ 生成一张新卡（默认 dry-run，--yes 落盘）。

Usage: python scripts/new_entry.py --domain law --id law.ancient.xxx
       [--out asset/law/codes/new.yaml] [--yes]
Exit: 0 ok, 1 参数/校验问题（stdout 恒为单一 JSON）。
"""
import argparse
import os
import re

import yaml

from _corpus import (REQUIRED, add_root_arg, apply_root, asset_dir,
                     defect, emit, rel)

TEMPLATES = {
    "law": "entry-law.yaml",
    "philosophy": "entry-phil.yaml",
}
ID_RE = re.compile(r"^(law|phil|reason)\.[a-z0-9_.-]+$")


def template_path(domain):
    """模板绝对路径由当前 ROOT 推导（不在 import 期固化）。"""
    name = TEMPLATES.get(domain)
    if not name:
        return None
    return os.path.join(asset_dir(), "templates", name)


def load_template(domain):
    path = template_path(domain)
    if not path or not os.path.exists(path):
        return None
    doc = yaml.safe_load(open(path, encoding="utf-8"))
    if isinstance(doc, list):
        doc = doc[0] if doc else None
    return doc if isinstance(doc, dict) else None


def build(domain, ident):
    tpl = load_template(domain)
    if tpl is None:
        return None, []
    tpl["id"] = ident
    tpl["domain"] = domain
    for field in REQUIRED[domain]:
        tpl.setdefault(field, "待核")
    return tpl, yaml.safe_dump([tpl], allow_unicode=True, sort_keys=False,
                               width=76)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, choices=["law", "philosophy"])
    ap.add_argument("--id", required=True)
    ap.add_argument("--out")
    ap.add_argument("--yes", action="store_true")
    add_root_arg(ap)
    args = ap.parse_args()
    apply_root(args)
    found = []
    if not ID_RE.match(args.id):
        found.append(defect("new_entry", args.id, "id",
                            "id 不符合 ^(law|phil|reason)\\.[a-z0-9_.-]+$",
                            "改 id"))
    if found:
        return emit({"check": "new_entry"}, found)
    tpl, text = build(args.domain, args.id)
    if tpl is None:
        return emit({"check": "new_entry"},
                    [defect("new_entry", args.domain, "template",
                            "缺模板 %s" % template_path(args.domain),
                            "补 asset/templates/ 模板")])
    out = args.out or os.path.join(asset_dir(), args.domain, "codes",
                                   args.id.split(".")[-1] + ".yaml")
    if os.path.exists(out):
        return emit({"check": "new_entry", "target": rel(out)},
                    [defect("new_entry", rel(out), "file", "目标已存在，不覆盖",
                            "换 id 或 --out")])
    if not args.yes:
        return emit({"check": "new_entry", "mode": "dry-run",
                     "target": rel(out), "preview": text,
                     "note": "写盘后须跑 validate_entries + check_sources"}, [])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".tmp"
    open(tmp, "w", encoding="utf-8", newline="\n").write(text)
    os.replace(tmp, out)
    return emit({"check": "new_entry", "mode": "write", "target": rel(out)}, [])


if __name__ == "__main__":
    raise SystemExit(main())
