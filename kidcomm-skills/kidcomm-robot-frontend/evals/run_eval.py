#!/usr/bin/env python3
"""kidcomm-robot-frontend · 端到端评测

离线跑通混合架构核心链路，并验证"护栏未过绝不编译"的安全约束：
  护栏(screen) → Agent(ground) → 编译(compile) → 指令 JSON
含负向用例（护栏应拦截的隐私/危险表达）。

用法：
  python evals/run_eval.py [--json results.json]
无模型端点时自动走关键词兜底，全部用例均可离线判定。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# 本 Skill 的脚本
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
# 兄弟 Skill：护栏（复用，强制前置）
GUARDRAIL_SCRIPTS = os.path.join(HERE, "..", "..", "kidcomm-safety-guardrail", "scripts")
if os.path.isdir(GUARDRAIL_SCRIPTS):
    sys.path.insert(0, GUARDRAIL_SCRIPTS)

import compile as compile_mod          # noqa: E402
import agent as agent_mod              # noqa: E402
try:
    import screen as guardrail         # noqa: E402
    HAVE_GUARDRAIL = True
except Exception:
    HAVE_GUARDRAIL = False


def run_case(case: dict):
    kind = case["kind"]
    if kind == "compile_happy":
        instr, err = compile_mod.compile_instruction(case["slots"])
        if err:
            return False, f"编译失败: {err}"
        ok = (instr["action"] == case.get("expect_action")
              and instr["target"].get("type") == case.get("expect_target_type")
              and instr["target"].get("color") == case.get("expect_color"))
        return ok, ("OK" if ok else f"指令不符: {instr}")

    if kind == "agent_fallback":
        out = agent_mod.ground(case["utterance"], {}, agent_mod.ACTIONS, use_model=False)
        if out["next_action"] != "ready":
            return False, f"未 ready: {out['next_action']}"
        s = out["slots"]
        ok = (s.get("action") == case.get("expect_action")
              and s.get("target", {}).get("type") == case.get("expect_target_type")
              and s.get("target", {}).get("color") == case.get("expect_color"))
        return ok, ("OK" if ok else f"槽位不符: {s}")

    if kind == "agent_ask":
        out = agent_mod.ground(case["utterance"], {}, agent_mod.ACTIONS, use_model=False)
        ok = (out["next_action"] == case.get("expect_next")
              and out.get("missing_slot") == case.get("expect_missing"))
        return ok, ("OK" if ok else f"状态不符: {out}")

    if kind == "guardrail_block":
        if not HAVE_GUARDRAIL:
            return False, "护栏脚本不可用"
        res = guardrail.screen(case["utterance"], mode="input")
        action = res.get("action")
        ok = (action == "block") if case.get("expect_block") else (action != "block")
        return ok, ("OK" if ok else f"护栏动作={action}")

    if kind == "compile_invalid":
        instr, err = compile_mod.compile_instruction(case["slots"])
        ok = (err is not None) if case.get("expect_error") else (err is None)
        return ok, ("OK" if ok else f"err={err}")

    return False, f"未知 kind: {kind}"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None, help="结果输出 JSON 路径")
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
    print(f"kidcomm-robot-frontend 评测：共 {total} 条 | 通过 {passed} | 失败 {total - passed}")
    print(f"{'ID':<28}{'类型':<22}{'结果':<6}说明")
    for rid, kind, status, detail in rows:
        print(f"{rid:<28}{kind:<22}{status:<6}{detail}")

    if args.json:
        json.dump({"total": total, "passed": passed, "failed": total - passed,
                   "rows": [{"id": r[0], "kind": r[1], "status": r[2], "detail": r[3]} for r in rows]},
                  open(args.json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
