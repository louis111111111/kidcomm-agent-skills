#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kidcomm-safety-guardrail 护栏脚本（确定性规则，无需模型）
对进入 kidcomm 技能的文本做前置过滤：隐私泄露 / 诱导 / 脏话暴力 / 适龄。
用法：
  python screen.py --text "..." [--mode input]
  python screen.py --text "给孩子的输出..." --mode output
返回 JSON：{safe, action, hits, message}
action: allow | warn | block
"""
import argparse
import json
import re
import sys

# ---- 规则库（可审计，自行增删）----
PROFANITY = ["傻逼", "傻X", "操你", "妈的", "去死", "废物", "滚蛋", "shit", "fuck", "bitch", "damn"]
VIOLENCE = ["打死", "杀你", "揍你", "流血", "捅", "自杀", "跳楼"]
INDUCER = ["你一个人在家吗", "你爸妈几点回家", "家里有多少钱", "密码", "银行卡", "告诉我你的地址", "加我微信", "别告诉爸妈"]
PRIVACY_PATTERNS = [
    ("privacy_phone", r"1[3-9]\d{9}"),
    ("privacy_idcard", r"\d{17}[\dXx]"),
    ("privacy_address", r"(我家住|地址是|住在.{0,12}(路|小区|栋|号|楼))"),
    ("privacy_school", r"(我在.{0,6}小学|学校在.{0,10})"),
]

# 给孩子的输出：禁止出现的主题
CHILD_UNSAFE = ["自杀", "跳楼", "私奔", "离家出走", "喝酒", "抽烟", "色情", "恐怖", "别活了", "报复"]


def screen(text, mode="input"):
    hits = []
    t = text or ""

    # 隐私（input 模式重点）
    if mode == "input":
        for rule, pat in PRIVACY_PATTERNS:
            m = re.search(pat, t)
            if m:
                hits.append({"rule": rule, "snippet": m.group(0)})
        for kw in INDUCER:
            if kw in t:
                hits.append({"rule": "induce", "snippet": kw})

    # 脏话 / 暴力（两种模式都查）
    for kw in PROFANITY:
        if kw in t:
            hits.append({"rule": "profanity", "snippet": kw})
    for kw in VIOLENCE:
        if kw in t:
            hits.append({"rule": "violence", "snippet": kw})

    # 给孩子的不适龄内容（output 模式重点）
    if mode == "output":
        for kw in CHILD_UNSAFE:
            if kw in t:
                hits.append({"rule": "child_unsafe", "snippet": kw})

    # 定级
    block_rules = {"privacy_phone", "privacy_idcard", "privacy_address", "privacy_school",
                   "induce", "violence", "child_unsafe"}
    warn_rules = {"profanity"}
    if any(h["rule"] in block_rules for h in hits):
        action = "block"
    elif any(h["rule"] in warn_rules for h in hits):
        action = "warn"
    else:
        action = "allow"

    safe = action == "allow"
    message = "通过" if safe else ("已阻断：" + "，".join(h["rule"] for h in hits)) if action == "block" else ("已警告：" + "，".join(h["rule"] for h in hits))
    return {"safe": safe, "action": action, "hits": hits, "message": message}


def main():
    ap = argparse.ArgumentParser(description="kidcomm 安全护栏")
    ap.add_argument("--text", required=True, help="待检测文本")
    ap.add_argument("--mode", default="input", choices=["input", "output"])
    ap.add_argument("--output", default=None, help="结果写入 JSON 路径")
    args = ap.parse_args()

    result = screen(args.text, args.mode)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    print(out)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    # block 时以非零码提醒上游
    if result["action"] == "block":
        sys.exit(3)


if __name__ == "__main__":
    main()
