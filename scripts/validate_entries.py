"""validate_entries.py — schema conformance of asset/ knowledge cards.

Checks the field sets defined in asset/schema/entry.schema.md:
  law  : 出处 source / 条文号 article / 年代 era / 法域 jurisdiction /
         效力状态 force_status / 要旨 gist
  phil : 代表文本 text / 核心命题 thesis / 流派 school / 后世批评 criticism
  reas : steps / must_answer / grade_scale
plus id pattern, enum domains, refs tier enum, verified tri-state.

Usage: python scripts/validate_entries.py [--json-only] [--domain law]
Exit: 0 clean, 1 defects (JSON list on stdout).
"""
import argparse
import os

from _corpus import (ID_RE, REQUIRED, SKIP_PREFIXES, TIER_ENUM,
                     VERIFIED_ENUM, add_root_arg, apply_root, defect,
                     emit, force_ok, is_empty, is_skipped, load_entries)

# skip 判定统一走 _corpus.is_skipped（相对技能根的 posix 前缀，与 CWD 无关）


def check_entry(where, ent):
    out = []
    if "__parse_error__" in ent:
        return [defect("schema", where, "file",
                       "YAML 解析失败：%s" % ent["__parse_error__"],
                       "修正标量引号后重跑")]
    domain = ent.get("domain")
    if domain not in REQUIRED:
        out.append(defect("schema", where, "domain",
                          "domain=%r 不在 law/philosophy/reasoning" % domain,
                          "补正确 domain"))
        return out
    for field in REQUIRED[domain]:
        if is_empty(ent.get(field)):
            out.append(defect("schema", where, field,
                              "%s 卡缺必填字段 %s" % (domain, field),
                              "补字段；无法确证填「待核」，不得留空"))
    ident = ent.get("id", "")
    if isinstance(ident, str) and ident and not ID_RE.match(ident):
        out.append(defect("schema", where, "id",
                          "id=%r 不符合 ^(law|phil|reason)\\.[a-z0-9_.-]+$" % ident,
                          "改 id 命名"))
    fs = ent.get("force_status")
    if not is_empty(fs) and not force_ok(fs):
        out.append(defect("schema", where, "force_status",
                          "force_status=%r 不在枚举（可加「（附注）」）" % str(fs)[:30],
                          "取 现行/被修订/已废/历史法源/待核 之一打头"))
    ver = ent.get("verified")
    if isinstance(ver, bool) or not isinstance(ver, str):
        out.append(defect("schema", where, "verified",
                          "verified=%r 为布尔值（YAML 1.1 把 yes/no 读成 bool）" % ver,
                          '加引号写 "yes"/"partial"/"no"'))
    elif ver not in VERIFIED_ENUM:
        out.append(defect("schema", where, "verified",
                          "verified=%r 不在 yes/partial/no" % ver, "改枚举"))
    out += check_refs(where, ent)
    if domain == "philosophy":
        out += check_criticism(where, ent)
    if domain == "reasoning":
        for field in ("steps", "must_answer", "grade_scale"):
            val = ent.get(field)
            if val is not None and not isinstance(val, list):
                out.append(defect("schema", where, field,
                                  "%s 必须是列表" % field, "改列表"))
    return out


def check_refs(where, ent):
    out = []
    refs = ent.get("refs")
    if is_empty(refs):
        return out
    if not isinstance(refs, list):
        return [defect("schema", where, "refs", "refs 必须是列表", "改列表")]
    for i, item in enumerate(refs):
        tag = "%s#refs[%d]" % (where, i)
        if not isinstance(item, dict):
            out.append(defect("schema", tag, "refs", "ref 项必须是映射",
                              "写成 tier+url/citation"))
            continue
        if item.get("tier") not in TIER_ENUM:
            out.append(defect("schema", tag, "tier",
                              "tier=%r 不在 T1–T4" % item.get("tier"), "改 tier"))
        if is_empty(item.get("url")) and is_empty(item.get("citation")):
            out.append(defect("schema", tag, "url|citation",
                              "ref 既无 url 也无 citation", "补出处"))
    return out


def check_criticism(where, ent):
    out = []
    crit = ent.get("criticism")
    if crit is None:
        return out
    if not isinstance(crit, list):
        return [defect("schema", where, "criticism", "criticism 必须是列表",
                       "改列表")]
    for i, item in enumerate(crit):
        tag = "%s#criticism[%d]" % (where, i)
        if not isinstance(item, dict) or is_empty(item.get("by")) \
                or is_empty(item.get("claim")):
            out.append(defect("schema", tag, "criticism",
                              "后世批评项须含 by（批评者）与 claim（论点）",
                              "补 by/claim"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", choices=["law", "philosophy", "reasoning"])
    add_root_arg(ap)
    args = ap.parse_args()
    apply_root(args)
    rows = load_entries()
    defects_ = []
    for path, idx, ent in rows:
        if is_skipped(path):
            continue
        if args.domain and ent.get("domain") != args.domain:
            continue
        where = "%s[%d]:%s" % (path, idx, ent.get("id", "?"))
        defects_ += check_entry(where, ent)
    return emit({"check": "validate_entries",
                 "entries": len(rows),
                 "skipped_prefixes": list(SKIP_PREFIXES),
                 "by_domain_filter": args.domain or "all",
                 "defects": defects_}, defects_)


if __name__ == "__main__":
    raise SystemExit(main())
