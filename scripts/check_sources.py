"""check_sources.py — 条文与文献出处完整性 lint.

默认报错项（红线：不得编造出处；无法确证的年代/条文号须标「待核」）：
  S1 每条 ref 须有 tier + (url 或 citation)；有 url 必须标 url_status。
  S2 法条卡缺 source、哲学卡缺 text（代表文本）→ 无出处不得入库。
  S3 era / article 含不确定措辞（待查·存疑·一说·大约·未定·或有异文·不可确）
     却未标「待核」→ 报错。（「争议」属学理用语，不作不确定标记。）
  S4 original_quote 存在、refs 无 T1 原文、且该字段未自标「译述/非原文/二手转述」
     → 报错（二手转述冒充原文）。
仅 --strict 计入（属知识判断，不强制改数据）：
  S5 verified=yes 却无任何可核锚点（url_status=checked 或 T1/T2 著录）。
  S6 verified=partial/no 却无 degraded 说明。
Usage: python scripts/check_sources.py [--strict] [--domain law]
Exit: 0 clean, 1 defects (JSON on stdout).
"""
import argparse

from _corpus import (URL_STATUS_ENUM, defect, emit, is_empty, load_entries, rel)

UNCERTAIN = ["待查", "存疑", "一说", "大约", "未定", "或有异文", "不可确",
             "未经核", "尚无定说"]
SELF_FLAG = ["译述", "非原文", "二手", "不得当作原文", "重构", "转述"]
SKIP_PREFIX = ("asset/templates/",)


def refs_of(ent):
    refs = ent.get("refs")
    return [r for r in refs if isinstance(r, dict)] if isinstance(refs, list) else []


def check_refs(where, ent):
    out = []
    refs = ent.get("refs")
    if isinstance(refs, list):
        for i, item in enumerate(refs):
            tag = "%s#refs[%d]" % (where, i)
            if not isinstance(item, dict):
                out.append(defect("source", tag, "refs", "ref 项须为映射",
                                  "写成 tier + url/citation"))
                continue
            if is_empty(item.get("url")) and is_empty(item.get("citation")):
                out.append(defect("source", tag, "url|citation",
                                  "该 ref 既无 url 也无 citation（出处缺失）",
                                  "补原始链接或规范文献著录"))
            if not is_empty(item.get("url")):
                status = item.get("url_status")
                if is_empty(status):
                    out.append(defect("source", tag, "url_status",
                                      "url 未标 url_status",
                                      "补 checked/unchecked/blocked"))
                elif status not in URL_STATUS_ENUM:
                    out.append(defect("source", tag, "url_status",
                                      "url_status=%r 非法" % status,
                                      "取 checked/unchecked/blocked"))
    return out


def check_uncertain(where, ent):
    out = []
    for field in ("era", "article"):
        val = ent.get(field)
        if isinstance(val, str) and any(h in val for h in UNCERTAIN) \
                and "待核" not in val:
            out.append(defect("source", where, field,
                              "%s 含不确定措辞却未标「待核」：%s"
                              % (field, val[:40]),
                              "在该字段追加「待核」，或删去不确定表述"))
    return out


def check_quote(where, ent):
    quote = ent.get("original_quote")
    if is_empty(quote):
        return []
    tiers = {r.get("tier") for r in refs_of(ent)}
    if "T1" in tiers:
        return []
    if any(flag in str(quote) for flag in SELF_FLAG):
        return []
    return [defect("source", where, "original_quote",
                  "有 original_quote、refs 无 T1 原文，且未自标「译述/非原文」",
                  "补 T1 校勘本，或在字段内写明系译述")]


def check_strict(where, ent):
    out = []
    refs = refs_of(ent)
    verified = str(ent.get("verified"))
    anchored = any(r.get("url_status") == "checked" for r in refs) or \
        any(r.get("tier") in ("T1", "T2") and not is_empty(r.get("citation"))
            for r in refs)
    if verified == "yes" and not anchored:
        out.append(defect("source", where, "verified",
                          "verified=yes 但无可核锚点（checked url 或 T1/T2 著录）",
                          "补锚点或降为 partial"))
    if verified in ("partial", "no") and is_empty(ent.get("degraded")):
        out.append(defect("source", where, "degraded",
                          "verified=%s 无 degraded 说明" % verified,
                          "写明缺项与降级口径"))
    return out


def check_entry(where, ent, strict):
    out = []
    domain = ent.get("domain")
    if "__parse_error__" in ent or domain not in ("law", "philosophy",
                                                  "reasoning"):
        return out
    need = {"law": "source", "philosophy": "text"}.get(domain)
    if need and is_empty(ent.get(need)):
        out.append(defect("source", where, need,
                          "%s 卡缺出处字段 %s" % (domain, need),
                          "补出处；确证不了写「待核」"))
    out += check_refs(where, ent)
    out += check_uncertain(where, ent)
    out += check_quote(where, ent)
    if strict:
        out += check_strict(where, ent)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="把 S5/S6（知识判断类）也计入缺陷")
    ap.add_argument("--domain", choices=["law", "philosophy", "reasoning"])
    args = ap.parse_args()
    rows = load_entries()
    found = []
    for path, idx, ent in rows:
        where = "%s[%d]:%s" % (rel(path), idx, ent.get("id", "?"))
        if where.startswith(SKIP_PREFIX):
            continue
        if args.domain and ent.get("domain") != args.domain:
            continue
        found += check_entry(where, ent, args.strict)
    return emit({"check": "check_sources", "entries": len(rows),
                 "strict": args.strict,
                 "skipped_prefixes": list(SKIP_PREFIX)}, found)


if __name__ == "__main__":
    raise SystemExit(main())
