#!/usr/bin/env python3
"""kidcomm-robot-frontend · Agent 对话层（自然语言 → 槽位 / 指令意图）

混合架构的"对话层"：本地 LLM 做残差消歧 + grounding + member-check；
无模型时用中文关键词兜底，保证离线也能演示核心链路（评审/演示友好）。

模型端点遵循 kidcomm 既有 KIDCOMM_BASE_URL/MODEL/API_KEY 解耦（OpenAI 兼容）。
无端点或 requests 缺失时，自动走关键词兜底，绝不崩溃。

输出严格 JSON（见 references/agent-contract.md）：
  {next_action: ask|fill|ready, missing_slot, question, slots, member_check}
"""
import argparse, json, os, sys

# 动作优先级（先匹配更具体的动词）
ACTIONS = ["pick_up", "move_to", "play", "turn", "stop"]
ACTION_KW = {
    "pick_up": ["拿", "捡", "取", "抓", "给我", "要", "摘", "端"],
    "move_to": ["去", "走到", "移动到", "过来", "去到", "去那", "去那儿", "往", "到", "找"],
    "play": ["玩", "唱", "跳", "跳舞", "游戏", "陪", "一起"],
    "turn": ["转", "转向", "转头", "掉头", "转个身"],
    "stop": ["停", "别动", "停下", "停止", "不许", "不要动", "住手"],
}
COLOR_KW = [("red", "红"), ("blue", "蓝"), ("green", "绿"), ("yellow", "黄"),
            ("orange", "橙"), ("purple", "紫"), ("white", "白"), ("black", "黑")]
TYPE_KW = [("block", "积木"), ("ball", "球"), ("toy", "玩具"), ("person", "人"),
           ("location", "地方"), ("book", "书"), ("cup", "杯子")]

ZH = {"pick_up": "拿", "move_to": "去", "play": "玩", "turn": "转", "stop": "停下",
      "block": "积木", "ball": "球", "toy": "玩具", "person": "人",
      "location": "那个地方", "book": "书", "cup": "杯子"}
COLOR_ZH = {"red": "红", "blue": "蓝", "green": "绿", "yellow": "黄", "orange": "橙",
            "purple": "紫", "white": "白", "black": "黑"}
NO_TARGET_ACTIONS = {"stop"}


def detect_action(text: str):
    for a in ACTIONS:  # 已按优先级
        if any(k in text for k in ACTION_KW[a]):
            return a
    return None


def detect_target(text: str):
    color = next((c for c, k in COLOR_KW if k in text), None)
    ttype = next((t for t, k in TYPE_KW if k in text), None)
    if color is None and ttype is None:
        return None
    return {k: v for k, v in (("type", ttype), ("color", color)) if v}


def _merge_target(slots_target, detected):
    detected = detected or {}
    t = dict(slots_target or {})
    if not t.get("type") and detected.get("type"):
        t["type"] = detected["type"]
    if not t.get("color") and detected.get("color"):
        t["color"] = detected["color"]
    return {k: v for k, v in t.items() if v}


def ground(utterance: str, slots: dict = None, actions: list = None, use_model: bool = False):
    """返回 agent 契约 dict。无模型走关键词兜底；有端点且 use_model 时尝试 LLM。"""
    slots = slots or {}
    actions = actions or ACTIONS
    utterance = utterance or ""

    if use_model and os.environ.get("KIDCOMM_BASE_URL"):
        try:
            llm = _llm_ground(utterance, slots, actions)
            if llm:
                return llm
        except Exception:
            pass  # 失败回退兜底

    action = slots.get("action") or detect_action(utterance)
    target = _merge_target(slots.get("target"), detect_target(utterance))

    missing = []
    if action is None:
        missing.append("action")
    elif action not in actions:
        missing.append("action")  # 超出机器人能力
    if action not in NO_TARGET_ACTIONS and "type" not in target:
        missing.append("target")

    if missing:
        q = ("你想让机器人做什么呀？可以点上面的动作卡片～" if "action" in missing
             else "你说的是哪个呀？能指给我看吗？")
        return {"next_action": "ask", "missing_slot": missing[0], "question": q,
                "slots": {k: v for k, v in {"action": action, "target": target}.items() if v},
                "member_check": None}

    desc = "你想让机器人" + ZH.get(action, action)
    if target.get("color"):
        desc += COLOR_ZH.get(target["color"], target["color"]) + "色"
    if target.get("type"):
        desc += ZH.get(target["type"], target["type"])
    desc += "，对吗？"
    return {"next_action": "ready", "missing_slot": None, "question": None,
            "slots": {"action": action, "target": target}, "member_check": desc}


def _llm_ground(utterance, slots, actions):
    import requests  # 惰性导入
    base = os.environ["KIDCOMM_BASE_URL"].rstrip("/")
    model = os.environ.get("KIDCOMM_MODEL", "local-model")
    key = os.environ.get("KIDCOMM_API_KEY", "")
    sys_prompt = (
        "你是儿童机器人前端的理解模块，把孩子的自然语言解析成机器人槽位。"
        f"允许的动作只有：{','.join(actions)}。target.type 取值：block/ball/person/location/toy。"
        '只输出 JSON：{"action":..,"target":{"type":..,"color":..},"missing":[..],"member_check":..}。'
        "信息不足时 missing 列出缺的槽位（action/target）。"
    )
    r = requests.post(base + "/v1/chat/completions",
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                      json={"model": model,
                            "messages": [{"role": "system", "content": sys_prompt},
                                         {"role": "user", "content":
                                          f"已有槽位：{json.dumps(slots, ensure_ascii=False)}\n孩子说：{utterance}"}],
                            "temperature": 0, "max_tokens": 200}, timeout=20)
    content = r.json()["choices"][0]["message"]["content"]
    obj = json.loads(_extract_json(content))
    action = obj.get("action")
    target = obj.get("target") or {}
    missing = obj.get("missing") or []
    if missing:
        return {"next_action": "ask", "missing_slot": missing[0],
                "question": obj.get("question", f"还想知道：{missing}"),
                "slots": {"action": action, "target": target}, "member_check": None}
    return {"next_action": "ready", "missing_slot": None, "question": None,
            "slots": {"action": action, "target": target},
            "member_check": obj.get("member_check", "对吗？")}


def _extract_json(s: str):
    i, j = s.find("{"), s.rfind("}")
    return s[i:j + 1] if i >= 0 and j >= 0 else s


def main():
    ap = argparse.ArgumentParser(description="自然语言 → 槽位/指令意图")
    ap.add_argument("--utterance", default="")
    ap.add_argument("--slots", default="{}")
    ap.add_argument("--actions", default=",".join(ACTIONS))
    ap.add_argument("--model", action="store_true", help="尝试调用 KIDCOMM_* 端点")
    a = ap.parse_args()
    try:
        slots = json.loads(a.slots)
    except Exception as e:
        print(json.dumps({"error": f"slots 不是合法 JSON: {e}"}, ensure_ascii=False))
        sys.exit(2)
    out = ground(a.utterance, slots, a.actions.split(","), use_model=a.model)
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
