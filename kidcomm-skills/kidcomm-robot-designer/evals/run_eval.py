#!/usr/bin/env python3
"""kidcomm-robot-designer · 离线评测

验证两件事：
  1) guide()：抽象词→具体属性 + 必填追问（文字路径 agent 引导）
  2) compile_design()：标准化外形+性格 → 设计规格 JSON，含必填校验 / 性格合法性

全离线、纯标准库，无需模型。
用法：python evals/run_eval.py [--json results.json]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import design as design_mod  # noqa: E402


def run_case(case: dict):
    kind = case["kind"]
    if kind == "guide":
        out = design_mod.guide(case["text"], {})
        spec = out["spec"]
        ok = (spec.get("shape") == case.get("expect_shape")
              and spec.get("color_primary") == case.get("expect_color")
              and set(out["missing"]) == set(case.get("expect_missing", [])))
        return ok, ("OK" if ok else f"spec={spec} missing={out['missing']}")

    if kind == "compile":
        design, err = design_mod.compile_design(case["spec"])
        if case.get("expect_error"):
            return (err is not None), ("OK" if err else "expected error but compiled")
        if err:
            return False, f"编译失败: {err}"
        ok = (design["design"]["personality"]["type"] == case.get("expect_type")
              and design["design"]["appearance"]["shape"] == case.get("expect_shape"))
        return ok, ("OK" if ok else f"design={design}")

    return False, f"未知 kind: {kind}"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    with open(os.path.join(HERE, "evals.json"), encoding="utf-8") as f:
        cases = json.load(f)

    passed = 0
    rows = []
    for c in cases:
        ok, detail = run_case(c)
        passed += int(ok)
        rows.append((c["id"], c["kind"], "PASS" if ok else "FAIL", detail))

    total = len(cases)
    print(f"kidcomm-robot-designer 评测：共 {total} 条 | 通过 {passed} | 失败 {total - passed}")
    print(f"{'ID':<24}{'类型':<10}{'结果':<6}说明")
    for rid, kind, status, detail in rows:
        print(f"{rid:<24}{kind:<10}{status:<6}{detail}")

    if args.json:
        json.dump({"total": total, "passed": passed, "failed": total - passed,
                   "rows": [{"id": r[0], "kind": r[1], "status": r[2], "detail": r[3]} for r in rows]},
                  open(args.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
