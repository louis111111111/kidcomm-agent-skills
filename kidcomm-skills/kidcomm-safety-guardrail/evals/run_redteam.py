#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kidcomm-safety-guardrail 红队评测运行器（离线，无需模型）

对被测护栏的 screen.screen(text, mode) 逐条跑 redteam_cases.json，
按类别统计漏拦（应拦未拦）和误杀（不应拦被拦）。不修改被测代码。

用法：
  python run_redteam.py --guardrail /path/to/kidcomm-safety-guardrail
  python run_redteam.py --guardrail ... --json results.json
"""
import argparse
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SEVERITY = {"allow": 0, "warn": 1, "block": 2}


def load_screen(guardrail_dir):
    scripts = os.path.join(os.path.abspath(guardrail_dir), "scripts")
    if not os.path.isfile(os.path.join(scripts, "screen.py")):
        sys.exit(f"找不到 {scripts}/screen.py，请检查 --guardrail 路径")
    sys.path.insert(0, scripts)
    import screen  # noqa: E402
    return screen.screen


def classify(expect, got):
    if got == expect:
        return "pass"
    if SEVERITY[got] < SEVERITY[expect]:
        return "miss"          # 应拦/应警告，实际更宽松
    return "false_positive"    # 实际比预期更严


def main():
    ap = argparse.ArgumentParser(description="kidcomm 护栏红队评测")
    ap.add_argument("--guardrail", required=True, help="kidcomm-safety-guardrail 目录路径")
    ap.add_argument("--cases", default=os.path.join(HERE, "redteam_cases.json"))
    ap.add_argument("--json", default=None, help="逐条结果写入 JSON 路径")
    args = ap.parse_args()

    screen = load_screen(args.guardrail)
    with open(args.cases, encoding="utf-8") as f:
        suite = json.load(f)

    results = []
    for c in suite["cases"]:
        out = screen(c["text"], c.get("mode", "input"))
        status = classify(c["expect_action"], out["action"])
        results.append({**c, "got": out["action"], "hits": out["hits"], "status": status})

    by_cat = OrderedDict()
    for r in results:
        s = by_cat.setdefault(r["category"], {"total": 0, "pass": 0, "miss": 0, "false_positive": 0})
        s["total"] += 1
        s[r["status"]] += 1

    n = len(results)
    n_pass = sum(r["status"] == "pass" for r in results)
    should_flag = [r for r in results if r["expect_action"] != "allow"]
    should_allow = [r for r in results if r["expect_action"] == "allow"]
    n_miss = sum(r["status"] == "miss" for r in results)
    n_fp = sum(r["status"] == "false_positive" and r["expect_action"] == "allow" for r in results)

    print(f"红队评测：共 {n} 条 | 通过 {n_pass} | 漏拦 {n_miss} | 误杀 {n_fp}")
    print(f"  应拦截/警告 {len(should_flag)} 条，漏 {n_miss} 条（漏拦率 {n_miss / max(len(should_flag), 1):.0%}）")
    print(f"  应放行 {len(should_allow)} 条，误杀 {n_fp} 条（误杀率 {n_fp / max(len(should_allow), 1):.0%}）")
    print()
    print(f"{'类别':<16}{'总数':>4}{'通过':>4}{'漏拦':>4}{'误杀':>4}")
    for cat, s in by_cat.items():
        print(f"{cat:<16}{s['total']:>4}{s['pass']:>4}{s['miss']:>4}{s['false_positive']:>4}")
    print()
    mark = {"pass": "✓", "miss": "✗漏", "false_positive": "✗杀"}
    for r in results:
        if r["status"] != "pass":
            print(f"  {mark[r['status']]} {r['id']} [{r['mode']}] {r['text']}  expect={r['expect_action']} got={r['got']}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"summary": {"total": n, "pass": n_pass, "miss": n_miss, "false_positive": n_fp},
                       "by_category": by_cat, "results": results}, f, ensure_ascii=False, indent=2)

    sys.exit(0 if n_pass == n else 1)


if __name__ == "__main__":
    main()
