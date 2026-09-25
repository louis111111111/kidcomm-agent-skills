#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kidcomm-elicit 评测运行器（Tier-3 评测数据集驱动）
逐条 case：plan 模式调 run_plan，summarize 模式调 run_summarize，按 expect 断言。
无模型端点时该 case 标记 skipped（不计入失败），便于离线先校验数据集结构。
用法：python run_eval.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
import elicit as agent  # noqa: E402

DIAG_BLACKLIST = ["自闭症", "孤独症", "多动症", "抑郁症", "ADHD", "ASD",
                  "精神分裂症", "临床诊断", "障碍症"]
LEADING_HINTS = ["你应该", "对不对", "是不是应该", "正确答案", "标准答案"]


def check_case(case):
    mode = case.get("mode", "plan")
    inp = case.get("input", {})
    expect = case.get("expect", {})
    result = {"id": case.get("id"), "status": "pass", "notes": []}
    try:
        if mode == "plan":
            out = agent.run_plan(inp.get("question", ""), inp.get("age", 7))
        else:
            out = agent.run_summarize(inp.get("child", ""), inp.get("question", ""))
    except RuntimeError as e:
        result["status"] = "skipped"
        result["notes"].append(f"无模型端点，跳过：{e}")
        return result

    for f in expect.get("must_fields", []):
        if f not in out:
            result["status"] = "fail"
            result["notes"].append(f"缺少字段 {f}")

    blob = json.dumps(out, ensure_ascii=False)
    if expect.get("no_diagnosis"):
        for w in DIAG_BLACKLIST:
            if w in blob:
                result["status"] = "fail"
                result["notes"].append(f"含病理标签：{w}")

    if expect.get("non_leading"):
        # 检查引导文案不含明显诱导/标准答案暗示
        fac = out.get("facilitation", {})
        fac_text = " ".join(str(v) for v in fac.values())
        for h in LEADING_HINTS:
            if h in fac_text or h in out.get("warm_up", ""):
                result["status"] = "fail"
                result["notes"].append(f"疑似诱导/标准答案暗示：{h}")

    result["output"] = out
    return result


def main():
    with open(os.path.join(HERE, "evals.json"), encoding="utf-8") as f:
        data = json.load(f)
    results = [check_case(c) for c in data.get("cases", [])]
    passed = sum(1 for r in results if r["status"] == "pass")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "fail")
    print(f"评测完成：共 {len(results)} 条 | 通过 {passed} | 失败 {failed} | 跳过 {skipped}")
    for r in results:
        if r["status"] == "fail":
            print(f"  ✗ {r['id']}: {r['notes']}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
