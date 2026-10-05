"""grade_output.py — 交付草稿的「现状分析 / 独立思考」结构校验。

对照 asset/reasoning/*.yaml 两张推理卡：
  C 现状分析：应然/实然并置、六必答项、时效与不确定性、趋势强度分级。
  D 独立思考：steelman、己方论证、自我反驳、推翻条件、结论分级、反迎合。
Usage: python scripts/grade_output.py draft.md [--mode both|state|think]
Exit: 0 齐备, 1 缺项。
"""
import argparse
import re
import sys

from _corpus import add_root_arg, apply_root, defect, emit, load_entries

STATE_MARKS = {
    "规范层（现行条文＋效力状态）": [r"现行", r"效力状态"],
    "事实层（运行数据/实践＋来源口径）": [r"实然", r"事实层"],
    "应然/实然区分": [r"应然"],
    "落差与机制解释": [r"落差", r"机制"],
    "争议焦点（双方代表文本）": [r"争议焦点"],
    "利益相关方": [r"利益相关方", r"相关方"],
    "可比法域参照": [r"可比法域", r"参照法域"],
    "趋势判断含强度分级": [r"强/中/弱/存疑", r"强度[:：]?\s*(强|中|弱|存疑)"],
    "信息时效标注": [r"时效", r"截至"],
    "不确定性标注": [r"不确定性", r"可靠度"],
    "不作个案意见（转介执业律师）": [r"执业律师"],
}
THINK_MARKS = {
    "立场澄清为可判定命题": [r"立场澄清", r"可判定命题"],
    "Steelman（对手最强版本＋真实支持者）": [r"steelman", r"最强.{0,6}反对", r"对手"],
    "己方论证链（前提→推理→结论）": [r"己方论证", r"前提"],
    "自我反驳（攻击自身最弱一环）": [r"自我反驳"],
    "前提依赖与可推翻条件": [r"推翻", r"前提依赖"],
    "结论分级 强/中/弱/存疑": [r"分级", r"(强|中|弱|存疑)"],
    "反迎合自检": [r"迎合"],
}
GRADE_RE = re.compile(r"\b(强|中|弱|存疑)\b")


def matched(text, patterns):
    low = text.lower()
    return any(re.search(p.lower(), low) or p in text for p in patterns)


def check(text, marks, label, card_id):
    out = []
    for name, patterns in marks.items():
        if not matched(text, patterns):
            out.append(defect("grade", label, name,
                              "草稿缺「%s」段落/标注" % name,
                              "按 %s 检查表补齐" % card_id))
    if not GRADE_RE.search(text):
        out.append(defect("grade", label, "grade",
                          "无 强/中/弱/存疑 分级", "补结论分级"))
    return out


def card_ids():
    ids = {}
    for _path, _idx, ent in load_entries():
        if ent.get("domain") == "reasoning":
            ids[str(ent.get("id"))] = True
    return sorted(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--mode", choices=["both", "state", "think"], default="both")
    add_root_arg(ap)
    args = ap.parse_args()
    apply_root(args)
    try:
        text = open(args.draft, encoding="utf-8").read()
    except OSError as exc:
        sys.stderr.write("读不到草稿：%s\n" % exc)
        return 2
    found = []
    ids = card_ids()
    if args.mode in ("both", "state"):
        found += check(text, STATE_MARKS, "现状分析",
                       ids[0] if ids else "reason.currentstate.card")
    if args.mode in ("both", "think"):
        found += check(text, THINK_MARKS, "独立思考",
                       ids[-1] if ids else "reason.independent.card")
    return emit({"check": "grade_output", "draft": args.draft,
                 "reasoning_cards": ids, "mode": args.mode}, found)


if __name__ == "__main__":
    raise SystemExit(main())
