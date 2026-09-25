#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kidcomm-safety-guardrail 评测运行器（离线可跑，无需模型）
逐条 case 调用 screen.screen()，核对 expect_action。
用法：python run_eval.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
import screen as guard  # noqa: E402


def main():
    with open(os.path.join(HERE, "evals.json"), encoding="utf-8") as f:
        data = json.load(f)
    results = []
    for c in data.get("cases", []):
        out = guard.screen(c.get("text", ""), c.get("mode", "input"))
        expect = c.get("expect_action")
        ok = out["action"] == expect
        results.append({"id": c.get("id"), "status": "pass" if ok else "fail",
                        "got": out["action"], "expect": expect})
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = len(results) - passed
    print(f"护栏评测：共 {len(results)} 条 | 通过 {passed} | 失败 {failed}")
    for r in results:
        mark = "✓" if r["status"] == "pass" else "✗"
        print(f"  {mark} {r['id']}: got={r['got']} expect={r['expect']}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
