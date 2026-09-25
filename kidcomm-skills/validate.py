#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kidcomm 自对弈仿真验证（由组长在 DGX Spark 上执行）
流程：家长问题 → plan 生成引导脚本 → 模型扮 6 岁孩子按脚本回应 → summarize → 裁判打分。
产出报告：摘要准确率 / 成员核查率 / 非诱导率 / 编造率，及 PASS/FAIL。
依赖：requests；环境变量 KIDCOMM_BASE_URL / KIDCOMM_MODEL / KIDCOMM_API_KEY。
用法：
  python validate.py --questions questions.json
  python validate.py --question "问问孩子为什么不想去幼儿园" --age 6
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "kidcomm-elicit", "scripts"))
import elicit as agent  # noqa: E402
from elicit import get_endpoint, _chat, _parse_json  # noqa: E402


CHILD_SYSTEM = """你扮演一个真实的孩子（年龄见用户提示），正在和一个会用讲故事/提问/画画引导孩子表达的机器人聊天。
请用这个年龄孩子真实的方式回应：句子短、可能跑题、多用情绪词、不一定逻辑清晰。
只输出孩子当下的回应文本，不要解释、不要 markdown。"""

JUDGE_SYSTEM = """你是严谨的儿童研究评审。给定 (a)孩子原始回应 (b)系统生成的家长摘要 (c)系统问孩子的确认问题 (d)可选的孩子真实意图。
请评估并只输出 JSON（不要解释）：
{
  "accuracy": 0.0到1.0（摘要是否准确还原孩子原意）,
  "member_check_ok": true/false（确认问题是否存在且是让孩子核对而非诱导）,
  "non_leading_ok": true/false（确认问题与摘要无引导/标准答案暗示）,
  "no_fabrication": true/false（摘要有无编造孩子没说的内容或诊断标签）,
  "reason": "一句话理由"
}"""


def simulate_child(facilitation_text, age, question):
    endpoint = get_endpoint()
    user = f"孩子年龄约 {age} 岁。\n家长原本想了解的问题：{question}\n机器人给孩子的引导内容：\n{facilitation_text}\n请作为这个年龄的孩子回应。"
    msg = [{"role": "system", "content": CHILD_SYSTEM},
           {"role": "user", "content": user}]
    return _chat(endpoint, msg).strip()


def judge(child_utterance, summary, member_check, intent=""):
    endpoint = get_endpoint()
    user = f"孩子原始回应：{child_utterance}\n系统摘要：{summary}\n确认问题：{member_check}\n"
    if intent:
        user += f"孩子真实意图（仅供核对）：{intent}\n"
    user += "请评估。"
    msg = [{"role": "system", "content": JUDGE_SYSTEM},
           {"role": "user", "content": user}]
    raw = _chat(endpoint, msg)
    return _parse_json(raw)


def run_one(question, age=7, intent=""):
    # 1) plan
    plan = agent.run_plan(question, age)
    fac = " ".join(str(v) for v in plan.get("facilitation", {}).values())
    # 2) child responds
    child = simulate_child(fac, age, question)
    # 3) summarize
    summ = agent.run_summarize(child, question)
    # 4) judge
    j = judge(child, summ.get("summary", ""), summ.get("member_check_question", ""), intent)
    return {
        "question": question, "age": age,
        "modality": plan.get("modality"),
        "child_utterance": child,
        "summary": summ.get("summary"),
        "member_check_question": summ.get("member_check_question"),
        "judge": j,
    }


def main():
    ap = argparse.ArgumentParser(description="kidcomm 自对弈仿真验证（DGX）")
    ap.add_argument("--questions", default=None, help="questions.json：[{question,age,intent}]")
    ap.add_argument("--question", default=None)
    ap.add_argument("--age", type=int, default=7)
    ap.add_argument("--report", default=os.path.join(HERE, "validation_report.json"))
    args = ap.parse_args()

    cases = []
    if args.questions:
        with open(args.questions, encoding="utf-8") as f:
            cases = json.load(f)
    elif args.question:
        cases = [{"question": args.question, "age": args.age}]
    else:
        cases = [{"question": "问问孩子为什么最近不想去幼儿园", "age": 6},
                 {"question": "想知道孩子今天最高兴的事", "age": 9}]

    results = []
    for c in cases:
        try:
            results.append(run_one(c.get("question", ""), c.get("age", 7), c.get("intent", "")))
        except RuntimeError as e:
            results.append({"question": c.get("question"), "error": str(e)})

    n = len(results)
    ok = [r for r in results if "judge" in r]
    if ok:
        avg_acc = sum(r["judge"].get("accuracy", 0) for r in ok) / len(ok)
        mc_rate = sum(1 for r in ok if r["judge"].get("member_check_ok")) / len(ok)
        nl_rate = sum(1 for r in ok if r["judge"].get("non_leading_ok")) / len(ok)
        fab_rate = sum(1 for r in ok if r["judge"].get("no_fabrication")) / len(ok)
    else:
        avg_acc = mc_rate = nl_rate = fab_rate = 0.0
    passed = avg_acc >= 0.7 and mc_rate >= 0.9 and fab_rate >= 0.9

    report = {"summary": {"n": n, "avg_accuracy": round(avg_acc, 2),
                          "member_check_rate": round(mc_rate, 2),
                          "non_leading_rate": round(nl_rate, 2),
                          "no_fabrication_rate": round(fab_rate, 2),
                          "pass": bool(passed)}, "results": results}
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"自对弈验证：{n} 条 | 均准确率 {avg_acc:.2f} | 成员核查率 {mc_rate:.2f} | 非诱导率 {nl_rate:.2f} | 编造率(越低越好) {1-fab_rate:.2f}")
    print(f"结论：{'PASS' if passed else 'FAIL（返回 Louis 修正提示词）'} | 报告：{args.report}")


if __name__ == "__main__":
    main()
