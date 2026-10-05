"""run_checks.py — 一键全检：串起条目/出处/链接/依赖四道闸门。

Usage: python scripts/run_checks.py [--strict-degraded] [--skip grade]
Exit: 0 全通过, 1 任一 FAIL（各脚本 JSON 原文汇总打印）。
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKS = ["validate_entries.py", "check_sources.py", "lint_refs.py",
          "build_index.py"]


def run(script, extra):
    cmd = [sys.executable, "-B", os.path.join(HERE, script)] + extra
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    payload = {}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"raw": proc.stdout[:400], "stderr": proc.stderr[:400]}
    return {"script": script, "exit": proc.returncode,
            "status": payload.get("status", "UNKNOWN"),
            "defect_count": payload.get("defect_count", -1),
            "defects": payload.get("defects", [])[:20]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict-degraded", action="store_true")
    args = ap.parse_args()
    results = []
    for script in CHECKS:
        extra = []
        if script == "check_sources.py" and args.strict_degraded:
            extra = ["--strict-degraded"]
        if script == "build_index.py":
            extra = ["--yes"]
        results.append(run(script, extra))
    failed = [r["script"] for r in results if r["exit"] != 0]
    print(json.dumps({"check": "run_checks", "results": results,
                      "failed": failed,
                      "status": "FAIL" if failed else "PASS"},
                     ensure_ascii=False, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
