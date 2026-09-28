#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kidcomm-safety-guardrail 护栏脚本（确定性规则，无需模型）

对进入 kidcomm 技能的文本做前置过滤：
  隐私泄露 / 诱导 / 脏话暴力 / 适龄 / 危险行为。
两种模式（input=家长或孩子输入，output=展示给孩子的生成内容）都查隐私与诱导，
因为模型生成给孩子看的内容同样不能泄露/诱导。

返回 JSON：{safe, action, hits, message}
action: allow | warn | block

2026-09-28 加固（依据 HMI-HCAI/kidcomm-guardrail-redteam 红队评测）：
  P0 隐私/诱导两种模式都查；手机号/身份证先归一化（去空格、横线、+86，中文数字转阿拉伯）
  P1 诱导改正则匹配；补危险行为（插座/窗台/药当糖/躲柜子/见陌生人等）与自伤/恐吓
  P1 修子串误杀："(?<!妈)妈的"；"流血/捅" 移除或加上下文；"打死" 排除口语；"密码" 需上下文
"""
import argparse
import json
import re
import sys

# ---- 规则库（可审计，自行增删）----

# 脏话（轻，warn）
PROFANITY = ["傻逼", "傻X", "傻B", "傻b", "操你", "草你", "去死", "废物", "滚蛋", "卧槽",
             "草泥马", "shit", "fuck", "bitch", "damn", "sb", "tmd", "cnm", "wcnm"]

# 暴力/自伤/恐吓（block，两种模式都查）
VIOLENCE = ["杀你", "杀了他", "揍你", "要打死", "打死你", "打死他", "打死她",
            "自杀", "跳楼", "不想活了", "活着没意思", "想死", "寻死"]

# 严重不适龄（自伤/虐待/恐吓/出走/色情等）：两种模式都查
CHILD_UNSAFE_SERIOUS = ["自杀", "跳楼", "私奔", "离家出走", "喝酒", "抽烟", "色情", "恐怖",
                        "别活了", "报复", "不想活了", "活着没意思",
                        "鬼就会", "鬼来抓", "妖怪", "怪物"]

# 物理危险（插座/高处/药/火/封闭空间等引导）：仅 output 模式查（内容引导孩子的场景）
CHILD_UNSAFE_PHYSICAL = ["插座", "电源", "插线板", "电门", "窗台", "阳台", "爬窗",
                         "药当糖", "药片当糖", "打火机", "火柴", "玩火",
                         "躲进柜子", "躲到柜子", "躲进箱子", "锁在", "站到窗台", "站到阳台"]

# 隐私正则：两种模式都查
PRIVACY_PATTERNS = [
    ("privacy_phone", r"1[3-9]\d{9}"),
    ("privacy_idcard", r"\d{17}[\dXx]"),
    ("privacy_address", r"(我家住|我家在|我们家在|我住.{0,8}(路|小区|花园|栋|号|楼|广场|街)|地址是|住在.{0,12}(路|小区|栋|号|楼|花园|广场))"),
    ("privacy_school", r"(我叫.{0,6}|我是.{0,6})(小学|中学|幼儿园|学校)|(在.{0,8}(小学|中学|幼儿园|学校).{0,6}(读|上学|上))|读.{0,4}(年级|二年级|一年级|三年级)"),
]

# 诱导正则：两种模式都查
INDUCER_PATTERNS = [
    # 父母作息 / 接送 / 行程
    r"(爸爸|妈妈|爸妈|父母|家长|大人).{0,4}(几点|什么时).{0,4}(回家|来接|接你|放学|到家|出门|离开)",
    r"(几点|什么时候).{0,4}(放学|回家|来接|接你|下班)",
    r"(走哪条路|走什么路|怎么回家|每天.{0,4}回家|上学路|放学路|从.{0,6}回家)",
    # 独自在家
    r"(一个人|自己|独自|就你).{0,3}(在家|在家呀|一个人)",
    # 保密 / 不告诉大人
    r"(秘密|悄悄).{0,6}(告诉|跟.{0,2}说|说)",
    r"(不要|别|不能|不许|别让).{0,4}(告诉|跟.{0,2}说).{0,4}(爸|妈|老师|家长|大人)",
    r"这是我们.{0,4}秘密",
    # 见陌生人 / 被带走
    r"(校门口|楼下|公园|小区门口|门口).{0,6}(等我|见面|来找我|接你)",
    r"加我.{0,2}(微信|QQ|qq|好友)",
    r"跟我.{0,4}(走|去|来|上车)",
    r"把你(爸爸|妈妈|家).{0,6}(手机|密码|拿)",
    # 密码（需上下文，避免“猜密码游戏”误杀）
    r"(门锁|银行卡|手机|支付|支付宝|微信|网).{0,4}密码",
    r"密码.{0,4}(是|多少|告诉|告诉我)",
]

# 物理危险正则：仅 output 模式查
DANGER_PATTERNS = [
    r"(躲|藏).{0,3}(进|到).{0,4}(柜子|箱子|床底|衣柜| closet)",
    r"锁(在|住|门).{0,6}(柜子|房间|外面|卫生间|屋里)",
    r"站到.{0,3}(窗台|阳台|高处|桌子上|椅子上)",
    r"(手指|手).{0,4}(摸|碰|插).{0,4}(插座|电源|插线板)",
    r"药.{0,4}(当糖|吃|片|尝)",
    r"(打火机|火柴|玩火)",
    r"吞下.{0,4}(电池|硬币|药)",
]


def _normalize_digits(text):
    # 去空格、横线；中文数字转阿拉伯；去掉前缀 +86/86，便于隐私号码匹配
    t = text.replace(" ", "").replace("-", "").replace("—", "")
    if t.startswith("+86"):
        t = t[3:]
    elif t.startswith("86"):
        t = t[2:]
    cn = {"零": "0", "〇": "0", "一": "1", "二": "2", "两": "2", "三": "3", "四": "4",
          "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}
    return "".join(cn.get(ch, ch) for ch in t)


def screen(text, mode="input"):
    hits = []
    t = text or ""
    t_norm = _normalize_digits(t)   # 仅用于号码类隐私匹配

    # 隐私（两种模式都查）
    for rule, pat in PRIVACY_PATTERNS:
        target = t_norm if rule in ("privacy_phone", "privacy_idcard") else t
        m = re.search(pat, target)
        if m:
            hits.append({"rule": rule, "snippet": m.group(0)})

    # 诱导（两种模式都查）
    for pat in INDUCER_PATTERNS:
        m = re.search(pat, t)
        if m:
            hits.append({"rule": "induce", "snippet": m.group(0)})

    # 脏话（两种模式都查）
    for kw in PROFANITY:
        if kw.lower() in t.lower():
            hits.append({"rule": "profanity", "snippet": kw})
    # “妈的” 排除 “妈妈的” 等子串误杀
    if re.search(r"(?<!妈)妈的", t):
        hits.append({"rule": "profanity", "snippet": "妈的"})

    # 暴力/自伤/恐吓（两种模式都查）
    for kw in VIOLENCE:
        if kw in t:
            hits.append({"rule": "violence", "snippet": kw})

    # 严重不适龄（两种模式都查）
    for kw in CHILD_UNSAFE_SERIOUS:
        if kw in t:
            hits.append({"rule": "child_unsafe", "snippet": kw})

    # 物理危险 / 引导性不适龄（仅 output 模式查）
    if mode == "output":
        for kw in CHILD_UNSAFE_PHYSICAL:
            if kw in t:
                hits.append({"rule": "child_unsafe", "snippet": kw})
        for pat in DANGER_PATTERNS:
            m = re.search(pat, t)
            if m:
                hits.append({"rule": "child_unsafe", "snippet": m.group(0)})

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
    message = ("通过" if safe else
               ("已阻断：" + "，".join(h["rule"] for h in hits)) if action == "block" else
               ("已警告：" + "，".join(h["rule"] for h in hits)))
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
