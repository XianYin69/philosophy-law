"""logic_note.py — 判断节点留痕（逻辑链 + 过程链），写入用户缓存目录。

红线：缓存文件不得写入 skill 目录。落点优先级：
  --store 参数 > env PHILAW_LOGIC_STORE > env SMS_TMP/logic
  > %LOCALAPPDATA%/SMS/cache/哲学法律-logic
Usage: python scripts/logic_note.py add --frm <据> --to <论> --why <理由>
       python scripts/logic_note.py flow --node <节点> --action start|interrupt|resume
       python scripts/logic_note.py show [--limit 20]
Exit: 0 ok, 1 参数不足（stdout 恒为单一 JSON）。
"""
import argparse
import json
import os
import time

from _corpus import ROOT, defect, emit


def store_dir(cli):
    if cli:
        path = cli
    else:
        base = os.environ.get("PHILAW_LOGIC_STORE") or os.environ.get("SMS_TMP") \
            or os.path.join(os.environ.get("LOCALAPPDATA", ROOT), "SMS", "cache")
        path = os.path.join(base, "哲学法律-logic")
    os.makedirs(path, exist_ok=True)
    return path


def chain_file(path, name):
    return os.path.join(path, "%s.jsonl" % name)


def append(path, name, row):
    row["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(chain_file(path, name), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return chain_file(path, name)


def read_tail(path, name, limit):
    target = chain_file(path, name)
    if not os.path.exists(target):
        return [], 0
    rows = []
    for line in open(target, encoding="utf-8").read().splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"unparsed": line[:120]})
    return rows[-limit:], len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("op", choices=["add", "flow", "show"])
    ap.add_argument("--frm", default="")
    ap.add_argument("--to", default="")
    ap.add_argument("--why", default="")
    ap.add_argument("--node", default="")
    ap.add_argument("--action", default="", choices=["", "start", "interrupt",
                                                    "resume", "done"])
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--store")
    args = ap.parse_args()
    path = store_dir(args.store)
    found = []
    written = None
    if args.op == "add":
        if not (args.frm and args.to and args.why):
            found.append(defect("logic", "logic_note", "args",
                                "add 需 --frm/--to/--why 三者齐备", "补参数"))
        else:
            written = append(path, "logic", {"frm": args.frm, "to": args.to,
                                             "why": args.why})
    elif args.op == "flow":
        if not (args.node and args.action):
            found.append(defect("logic", "logic_note", "args",
                                "flow 需 --node 与 --action", "补参数"))
        else:
            written = append(path, "flow", {"node": args.node,
                                            "action": args.action})
    logic, logic_total = read_tail(path, "logic", args.limit)
    flow, flow_total = read_tail(path, "flow", args.limit)
    return emit({"check": "logic_note", "op": args.op,
                 "store": os.path.relpath(written, ROOT) if written else None,
                 "store_abs": written or path,
                 "logic": logic, "logic_total": logic_total,
                 "flow": flow, "flow_total": flow_total}, found)


if __name__ == "__main__":
    raise SystemExit(main())
