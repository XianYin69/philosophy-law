"""Shared corpus access for 哲学法律 validation scripts (stdlib + PyYAML).

路径锚定红线：语料根＝本文件所在技能根 `Path(__file__).resolve().parent.parent`，
**永不**使用 `os.getcwd()`；`--root` 仅供工具侧覆盖。所有上报路径一律是
「相对该根的 posix 路径」，因此同一份报告在任意 CWD 下逐字节一致。

Every script in this directory reports defects as JSON on stdout and exits
`0` (clean) or `1` (defects found). No bare except, no debug prints.
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    sys.stderr.write("PyYAML required: pip install pyyaml (%s)\n" % exc)
    raise SystemExit(2)

SKILL_ROOT = Path(__file__).resolve().parent.parent
ROOT = str(SKILL_ROOT)  # 可经 set_root()/--root 覆盖
ASSET = os.path.join(ROOT, "asset")

# 脚手架不参与条目校验：模板里是占位 id／枚举，schema 文件本身是定义。
SKIP_PREFIXES = ("asset/templates/", "asset/schema/")

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


def set_root(path):
    """Override the corpus root (absolute); recompute derived dirs."""
    global ROOT, ASSET
    ROOT = str(Path(path).resolve())
    ASSET = os.path.join(ROOT, "asset")
    return ROOT


def asset_dir():
    """Current asset dir — call it, never cache it at import time."""
    return os.path.join(ROOT, "asset")


def add_root_arg(ap):
    ap.add_argument("--root", default=None,
                    help="语料根覆盖（默认＝本脚本所在技能根，与 CWD 无关）")


def apply_root(args):
    if getattr(args, "root", None):
        set_root(args.root)
    return ROOT


def rel(path):
    """Root-relative posix path. Idempotent, and never touches the CWD.

    绝对路径 → 相对 ROOT 取 relpath；已是相对路径 → 视为「已相对 ROOT」，
    只做 normpath＋posix 化。旧版对相对路径再走一次 os.path.relpath，
    Python 会拿 CWD 当基准拼出 `../../../…`，skip 前缀随之失配。
    """
    p = os.fspath(path)
    if not os.path.isabs(p):
        return os.path.normpath(p).replace(os.sep, "/")
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def is_skipped(path):
    """True for scaffolding (templates / schema) — matched on root-relative
    posix path, so the verdict is independent of the caller's CWD."""
    return rel(path).startswith(SKIP_PREFIXES)


def walk_files(subdir, suffixes):
    """Absolute paths under ROOT/subdir, sorted — CWD-independent."""
    base = os.path.join(ROOT, subdir)
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in (".git", "tmp",
                                                        "__pycache__")]
        for name in sorted(filenames):
            if name.endswith(suffixes):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def md_files():
    return walk_files(".", (".md",))


def yaml_files():
    return walk_files("asset", (".yaml",))


def load_entries():
    """Yield (root-relative posix path, index, entry) for asset/**.yaml.

    契约：第一项恒为「相对 ROOT 的 posix 路径」，调用方不得再对它取
    os.path.relpath（那会引入 CWD）；需要展示路径时直接用 rel()（幂等）。
    """
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
