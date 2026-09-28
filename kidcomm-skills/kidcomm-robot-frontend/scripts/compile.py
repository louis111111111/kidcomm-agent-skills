#!/usr/bin/env python3
"""kidcomm-robot-frontend · 确定性编译器

把已收集的槽位 (action / target / params) 编译成机器人可执行指令 JSON。
无需模型、离线可跑：这是混合架构"前端脚手架让孩子选完槽位后"的确定性收口。

退出码：0 = 编译成功；2 = 槽位缺失/非法（不可编译）。
"""
import argparse, json, sys

# 机器人动作清单（与 SKILL.md / agent-contract.md 保持一致）
ACTIONS = {"pick_up", "move_to", "play", "turn", "stop"}
TARGET_TYPES = {"block", "ball", "person", "location", "toy", "book", "cup"}
COLORS = {"red", "blue", "green", "yellow", "orange", "purple", "white", "black"}
# 参数取值范围（前端滑杆/机器人端需对齐）
PARAM_RANGES = {"speed": (0.0, 1.0), "duration": (0, 600), "angle": (-180, 180)}
# 哪些动作可以不指定对象
NO_TARGET_ACTIONS = {"stop"}


def compile_instruction(slots: dict):
    """返回 (instruction_dict, error_str)。error 非空表示编译失败。"""
    if not isinstance(slots, dict):
        return None, "slots 必须是 JSON 对象"
    action = slots.get("action")
    if action not in ACTIONS:
        return None, f"动作缺失或不在清单内: {action!r}（允许: {sorted(ACTIONS)}）"

    target = slots.get("target") or {}
    if not isinstance(target, dict):
        return None, "target 必须是对象"
    ttype = target.get("type")
    if ttype is None:
        if action not in NO_TARGET_ACTIONS:
            return None, "缺少 target.type（该动作需要指定对象）"
    elif ttype not in TARGET_TYPES:
        return None, f"target.type 非法: {ttype!r}（允许: {sorted(TARGET_TYPES)}）"
    color = target.get("color")
    if color is not None and color not in COLORS:
        return None, f"颜色非法: {color!r}（允许: {sorted(COLORS)}）"

    params = slots.get("params") or {}
    if not isinstance(params, dict):
        return None, "params 必须是对象"
    for k, (lo, hi) in PARAM_RANGES.items():
        if k in params:
            try:
                v = float(params[k])
            except (TypeError, ValueError):
                return None, f"参数 {k} 非数值: {params[k]!r}"
            if not (lo <= v <= hi):
                return None, f"参数 {k}={v} 超出范围 [{lo},{hi}]"

    clean_target = {k: v for k, v in target.items() if v is not None}
    clean_params = {k: v for k, v in params.items() if v is not None}
    instruction = {
        "action": action,
        "target": clean_target,
        "params": clean_params,
        "confirm": True,
    }
    return instruction, None


def main():
    ap = argparse.ArgumentParser(description="slots → 机器人指令 JSON")
    ap.add_argument("--slots", required=True, help='JSON，如 \'{"action":"pick_up","target":{"type":"block","color":"red"}}\'')
    args = ap.parse_args()
    try:
        slots = json.loads(args.slots)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"slots 不是合法 JSON: {e}"}, ensure_ascii=False))
        sys.exit(2)
    instr, err = compile_instruction(slots)
    if err:
        print(json.dumps({"ok": False, "error": err}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "instruction": instr}, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
