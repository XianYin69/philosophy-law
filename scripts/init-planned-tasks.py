"""init-planned-tasks.py — 从 template.json 生成计划任务声明（默认预览，--yes 写盘）。

红线：技能自身**不得执行**计划任务；本脚本只写声明文件，到期由 SMS 调度器读取执行。
一任务一文件 `pt-<skill>-<slug>.json`，字段名与 SMS 读取端一致，不得改动；原子写。
Usage: python scripts/init-planned-tasks.py --slug source-refresh --title "出处抽检"
       --input "抽检 20 条 url_status=unchecked 的出处" --mode interval
       [--every-min 4320] [--at 2026-11-01T08:00] [--depends id1,id2] [--yes]
Exit: 0 ok, 1 参数/冲突问题（JSON 报告在 stdout）。
"""
import argparse
import json
import os
import re
import time

from _corpus import ROOT, defect, emit

PT_DIR = os.path.join(ROOT, "planned_tasks")
TEMPLATE = os.path.join(PT_DIR, "template.json")
SKILL_ID = os.path.basename(ROOT)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ISO_MIN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")
SCHEMA_KEYS = ("id", "title", "skill", "input", "schedule", "session", "status",
               "created", "next_run", "last_run", "runs", "notify", "depends")


def now_local():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def next_run(mode, at, every_min):
    """本地 ISO（不带时区后缀），与 SMS 读取端约定一致。"""
    if mode == "at":
        return at
    if mode == "interval":
        return time.strftime("%Y-%m-%dT%H:%M:00",
                             time.localtime(time.time() + every_min * 60))
    return now_local()


def build_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--mode", required=True, choices=["at", "cron", "interval"])
    ap.add_argument("--at", default="")
    ap.add_argument("--cron", default="0 8 * * *")
    ap.add_argument("--every-min", type=int, default=1440)
    ap.add_argument("--depends", default="")
    ap.add_argument("--yes", action="store_true")
    return ap


def validate(args):
    found = []
    if not SLUG_RE.match(args.slug):
        found.append(defect("planned_task", args.slug, "slug",
                            "slug 须为小写字母数字与中横线", "改 slug"))
    if args.mode == "at" and not ISO_MIN.match(args.at):
        found.append(defect("planned_task", args.slug, "at",
                            "mode=at 须给本地 ISO 时间 YYYY-MM-DDTHH:MM",
                            "补 --at"))
    if not os.path.exists(TEMPLATE):
        found.append(defect("planned_task", "planned_tasks/template.json",
                            "template", "模板缺失", "补 template.json"))
    return found


def build_row(args):
    tpl = json.load(open(TEMPLATE, encoding="utf-8"))
    task_id = "pt-%s-%s" % (SKILL_ID, args.slug)
    row = dict(tpl)
    row.update({
        "id": task_id, "title": args.title, "skill": SKILL_ID,
        "input": args.input,
        "schedule": {
            "mode": args.mode,
            "at": args.at if args.mode == "at" else None,
            "cron": args.cron if args.mode == "cron" else None,
            "every_min": args.every_min if args.mode == "interval" else None,
        },
        "session": {"kind": "cron", "key": "%s:%s" % (SKILL_ID, task_id)},
        "status": "pending", "created": now_local(),
        "next_run": next_run(args.mode, args.at, args.every_min),
        "last_run": None, "runs": 0, "notify": "shell",
        "depends": [d for d in args.depends.split(",") if d],
    })
    return task_id, row


def schema_check(task_id, row):
    found = []
    for key in SCHEMA_KEYS:
        if key not in row:
            found.append(defect("planned_task", task_id, key,
                                "字段与 SMS 读取端不一致", "补字段"))
    if row.get("status") not in ("pending", "running", "done", "paused",
                                 "failed"):
        found.append(defect("planned_task", task_id, "status",
                            "status 非法", "取五值之一"))
    return found


def main():
    args = build_parser().parse_args()
    found = validate(args)
    if found:
        return emit({"check": "init-planned-tasks"}, found)
    task_id, row = build_row(args)
    found = schema_check(task_id, row)
    out = os.path.join(PT_DIR, task_id + ".json")
    if os.path.exists(out):
        found.append(defect("planned_task", task_id, "file",
                            "任务文件已存在，不覆盖", "换 slug 或先删旧声明"))
    text = json.dumps(row, ensure_ascii=False, indent=2) + "\n"
    if found:
        return emit({"check": "init-planned-tasks", "target": task_id}, found)
    if not args.yes:
        return emit({"check": "init-planned-tasks", "mode": "dry-run",
                     "target": "planned_tasks/%s.json" % task_id,
                     "preview": row,
                     "note": "执行权归 SMS 调度器；--yes 原子写盘"}, [])
    tmp = out + ".tmp"
    open(tmp, "w", encoding="utf-8", newline="\n").write(text)
    os.replace(tmp, out)
    return emit({"check": "init-planned-tasks", "mode": "write",
                 "written": task_id}, [])


if __name__ == "__main__":
    raise SystemExit(main())
