"""Shared corpus access for 哲学法律 validation scripts (stdlib + PyYAML).

Every script in this directory reports defects as JSON on stdout and exits
`0` (clean) or `1` (defects found). No bare except, no debug prints.
"""
import json
import os
import re
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.stderr.write("PyYAML required: pip install pyyaml (%s)\n" % exc)
    raise SystemExit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(ROOT, "asset")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FORCE_ENUM = ["现行", "被修订", "已废", "历史法源", "待核"]
VERIFIED_ENUM = ["yes", "partial", "no"]
TIER_ENUM = ["T1", "T2", "T3", "T4"]
URL_STATUS_ENUM = ["checked", "unchecked", "blocked"]
ID_RE = re.compile(r"^(law|phil|reason)\.[a-z0-9_.-]+$")
REQUIRED = {
    "law": ["id", "title", "source", "article", "era", "jurisdiction",
            "force_status", "gist", "refs", "verified"],
    "philosophy": ["id", "title", "text", "thesis", "school", "criticism",
                   "refs", "verified"],
    "reasoning": ["id", "title", "steps", "must_answer", "grade_scale",
                  "refs", "verified"],
}


def walk_files(subdir, suffixes):
    base = os.path.join(ROOT, subdir)
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tmp")]
        for name in sorted(filenames):
            if name.endswith(suffixes):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def md_files():
    return walk_files(".", (".md",))


def yaml_files():
    return walk_files("asset", (".yaml",))


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def load_entries():
    """Yield (relpath, index, entry) for every mapping in asset/**.yaml."""
    rows = []
    for path in yaml_files():
        try:
            doc = yaml.safe_load(open(path, encoding="utf-8"))
        except yaml.YAMLError as exc:
            rows.append((rel(path), -1, {"__parse_error__": str(exc)[:200]}))
            continue
        if isinstance(doc, dict):
            doc = [doc]
        if not isinstance(doc, list):
            continue
        for idx, ent in enumerate(doc):
            if isinstance(ent, dict):
                rows.append((rel(path), idx, ent))
    return rows


def is_empty(value):
    return value is None or (isinstance(value, str) and not value.strip()) \
        or (isinstance(value, (list, dict)) and not value)


def force_ok(value):
    """Accept `枚举` or `枚举（附注）`; reject anything else."""
    text = str(value or "").strip()
    return any(text == t or text.startswith(t + "（") or text.startswith(t + "(")
               for t in FORCE_ENUM)


def emit(report, defects):
    """Print the JSON report; return the process exit code."""
    out = dict(report)
    out.setdefault("defects", defects)
    out["defect_count"] = len(defects)
    out["status"] = "FAIL" if defects else "PASS"
    out["root"] = ROOT
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if defects else 0


def defect(check, where, field, msg, fix=""):
    return {"check": check, "where": where, "field": field,
            "message": msg, "fix": fix}
