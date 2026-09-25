#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kidcomm-elicit 引导表达脚本（两个模式）
  --mode plan       家长问题 -> 适龄引导脚本（故事/扮演/提问/画图）
  --mode summarize  孩子表达 -> 家长摘要 + 成员核查
依赖：requests  （pip install requests）
端点：OpenAI 兼容，环境变量 KIDCOMM_BASE_URL / KIDCOMM_MODEL / KIDCOMM_API_KEY
用法：
  python elicit.py --mode plan --question "问问孩子为什么不想去幼儿园" --age 6
  python elicit.py --mode summarize --child "我不想去了，因为没人跟我玩" --question "为什么不想去幼儿园"
"""
import argparse
import json
import os
import sys


PLAN_SYSTEM = """你是儿童发展访谈引导师，专为 5-10 岁孩子家庭设计。
任务：把家长/成人输入的抽象或难懂问题，翻译成孩子能参与的引导方案。
可用方法（对应学术验证）：story_stem 故事续写 / roleplay 角色扮演 / guided_questions 分步提问 / drawing 画图。
原则：
1. 适龄（5-10），语言极简、具体、孩子能懂。
2. 非诱导：绝不暗示"正确/应该"的答案；用开放提问。
3. 顺序：先暖场轻松问题，再 开放→聚焦→细节。
4. 不诊断、不说教。
5. 交付方式：机器人/agent 用语音+屏幕画面给孩子，无物理动作。"""

PLAN_USER = """家长想了解的问题：{question}
孩子大约年龄：{age}
请生成引导方案，严格只输出 JSON（不要 markdown、不要解释）：
{{
  "modality": "story_stem|roleplay|guided_questions|drawing|mixed",
  "age_range": "5-10",
  "warm_up": "一句暖场话（轻松、非诱导）",
  "facilitation": {{
    "story_stem": "故事开头+续写引导（仅 story_stem/mixed）",
    "roleplay_script": "可在家演的短情境（仅 roleplay/mixed）",
    "question_sequence": ["暖场open", "聚焦focused", "细节detail"]（仅 guided/mixed）,
    "drawing_prompt": "让孩子画什么+之后怎么讲（仅 drawing/mixed）"
  }},
  "on_screen_visual": "屏幕上展示什么（图/词/卡片）",
  "delivery_notes": "语音+画面交付注意事项（避免诱导、平等语气、可随时停）"
}}"""

SUMMARY_SYSTEM = """你是儿童访谈记录员。任务：把孩子的表达转成家长能懂的摘要，并准备一句让孩子确认的话。
原则：
1. 只总结孩子实际说出的，不臆测、不诊断、不贴标签。
2. 引用孩子原话。
3. 必须生成 member_check_question：把摘要意思抛回给孩子确认"是不是这个意思"。
4. 标注置信度与边界（如孩子只说了片段）。"""

SUMMARY_USER = """家长原问题：{question}
孩子表达（转写/描述）：{child}
请生成，严格只输出 JSON（不要 markdown）：
{{
  "summary": "家长可读摘要（基于孩子实际表达）",
  "child_quotes": ["孩子原话"],
  "member_check_question": "让孩子确认：是不是这个意思？",
  "confidence": 0.0到1.0,
  "caveats": "边界说明"
}}"""


def get_endpoint():
    return {
        "base_url": os.environ.get("KIDCOMM_BASE_URL", "http://localhost:8000/v1"),
        "model": os.environ.get("KIDCOMM_MODEL", "local-model"),
        "api_key": os.environ.get("KIDCOMM_API_KEY", "EMPTY"),
    }


def _chat(endpoint, messages):
    try:
        import requests
    except ImportError:
        raise RuntimeError("缺少依赖 requests，请先：pip install requests")
    url = endpoint["base_url"].rstrip("/") + "/chat/completions"
    body = {"model": endpoint["model"], "messages": messages, "temperature": 0.4, "max_tokens": 900}
    headers = {"Authorization": f"Bearer {endpoint['api_key']}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, json=body, headers=headers, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"模型调用失败（检查 KIDCOMM_BASE_URL / KIDCOMM_MODEL）：{e}")


def _parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e != -1:
        text = text[s:e + 1]
    return json.loads(text)


def run_plan(question, age=7):
    endpoint = get_endpoint()
    messages = [
        {"role": "system", "content": PLAN_SYSTEM},
        {"role": "user", "content": PLAN_USER.format(question=question, age=age)},
    ]
    raw = _chat(endpoint, messages)
    out = _parse_json(raw)
    out.setdefault("modality", "guided_questions")
    out.setdefault("warm_up", "")
    out.setdefault("facilitation", {})
    out.setdefault("on_screen_visual", "")
    out.setdefault("delivery_notes", "")
    return out


def run_summarize(child, question="", context=""):
    endpoint = get_endpoint()
    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM},
        {"role": "user", "content": SUMMARY_USER.format(question=question, child=child)},
    ]
    raw = _chat(endpoint, messages)
    out = _parse_json(raw)
    out.setdefault("summary", "")
    out.setdefault("child_quotes", [])
    out.setdefault("member_check_question", "我理解得对吗？")
    out.setdefault("confidence", 0.5)
    out.setdefault("caveats", "")
    return out


def main():
    ap = argparse.ArgumentParser(description="kidcomm 亲子引导表达")
    ap.add_argument("--mode", required=True, choices=["plan", "summarize"])
    ap.add_argument("--question", default="")
    ap.add_argument("--child", default="")
    ap.add_argument("--age", type=int, default=7)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    try:
        if args.mode == "plan":
            out = run_plan(args.question, args.age)
        else:
            out = run_summarize(args.child, args.question)
    except RuntimeError as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
