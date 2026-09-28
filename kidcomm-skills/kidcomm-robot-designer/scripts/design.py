#!/usr/bin/env python3
"""kidcomm-robot-designer · 设计逻辑（离线可跑）

两件事：
1) guide()  —— 文字路径的 agent 引导：把孩子的抽象词（"可爱的"）映射成具体属性，
              并追问缺失的必填项。无 LLM 时走关键词+语料兜底。
2) compile_design() —— 把标准化外形+性格编译成可交付的设计规格 JSON
              （appearance / personality / build_hint / image_prompt / code_stub）。

模型端点（图像/LLM）仅在部署期接入，本脚本纯标准库、确定性、可评测。
"""
import argparse, json, os, sys

# ---- 选项词典 ----
SHAPE_OPT = ["圆", "方", "三角", "椭圆", "星形", "爱心"]
SHAPE_EN = {"圆": "round", "方": "square", "三角": "triangle", "椭圆": "oval",
            "星形": "star", "爱心": "heart"}
COLOR_OPT = [("red", "红"), ("blue", "蓝"), ("green", "绿"), ("yellow", "黄"),
             ("pink", "粉"), ("purple", "紫"), ("orange", "橙"), ("black", "黑"),
             ("white", "白"), ("silver", "银"), ("gold", "金")]
SIZE_OPT = [("small", "小"), ("medium", "中"), ("large", "大")]
PART_OPT = ["身体", "头", "翅膀", "尾巴", "触角", "爪子", "手臂"]

REQUIRED_APPEARANCE = ["shape", "color_primary", "size"]  # 必填目录：凑齐才能完成"捏脸"

# ---- 性格语料（personality → 表情/动作/语气）----
PERSONALITY = [
    {"k": "happy", "n": "开心", "face": "弯弯笑眼 + 大笑", "acts": ["蹦跳", "转圈", "挥手"], "tone": "轻快"},
    {"k": "angry", "n": "愤怒", "face": "圆睁眼 + 锯齿嘴/抿紧", "acts": ["跺脚", "挥拳", "喷气"], "tone": "低沉大声"},
    {"k": "timid", "n": "胆小", "face": "大睁眼 + 小嘴", "acts": ["躲身后", "缩头", "小碎步"], "tone": "细声"},
    {"k": "brave", "n": "勇敢", "face": "坚定眼神 + 微笑", "acts": ["大步前进", "张开双臂", "保护姿态"], "tone": "稳"},
    {"k": "gentle", "n": "温柔", "face": "柔和眼 + 浅笑", "acts": ["轻拍", "拥抱", "慢慢走"], "tone": "轻柔"},
    {"k": "naughty", "n": "调皮", "face": "眨眼 + 坏笑", "acts": ["做鬼脸", "偷偷动", "蹦跳"], "tone": "俏皮"},
]

# ---- 从 corpus.json 加载（单一真相源；文件缺失时退回上方手写默认值）----
def _load_corpus():
    try:
        _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "corpus", "corpus.json")
        with open(_p, encoding="utf-8") as _f:
            return json.load(_f)
    except Exception:
        return None

_CORPUS = _load_corpus()
if _CORPUS:
    SHAPE_EN = _CORPUS["shape"]
    COLOR_OPT = [(en, cn) for cn, en in _CORPUS["color"].items()]
    SIZE_OPT = [(en, cn) for cn, en in _CORPUS["size"].items()]
    PART_OPT = list(_CORPUS["parts"])
    ABSTRACT = _CORPUS["abstract_to_concrete"]
    PERSONALITY = _CORPUS["personality"]

# ---- 抽象词 → 具体属性 语料（agent 引导用）----
# 优先用 corpus.json 的 abstract_to_concrete；仅在 corpus.json 缺失时退回手写默认值（保证脚本仍可离线运行）
if not _CORPUS:
    ABSTRACT = {
        "可爱": {"shape": "round", "color_primary": "pink", "note": "圆圆的脸、粉粉的颜色、大大的眼睛"},
        "萌": {"shape": "round", "color_primary": "pink", "note": "圆圆的、粉粉的、萌萌的"},
        "酷": {"color_primary": "black", "note": "黑黑的、酷酷的"},
        "帅": {"color_primary": "blue", "note": "蓝蓝的、帅帅的"},
        "凶": {"color_primary": "red", "note": "红红的、凶凶的"},
        "软": {"texture": "毛茸茸", "shape": "round", "note": "毛茸茸的、圆圆的"},
        "威风": {"size": "large", "parts": ["翅膀"], "note": "大大的、带翅膀"},
    }

# 基础护栏（与 screen.py 同源思路；部署期仍强制跑完整护栏）
_GUARD = ["身份证", "住址", "家住在", "小区", "门牌", "学校叫", "我的学校", "我叫", "我的名字",
          "躲柜子", "别出声", "不要告诉", "保密", "独自在家", "密码"]


def guarded(text: str) -> bool:
    return any(w in text for w in _GUARD)


def guide(text: str, spec: dict = None):
    """文字路径引导：抽象→具体 + 追问必填。返回 {bot_msg, spec, missing[]}。"""
    spec = dict(spec or {})
    text = text or ""
    msg = ""
    # 抽象词
    hit = next((k for k in ABSTRACT if k in text), None)
    if hit:
        a = ABSTRACT[hit]
        for f in ("shape", "color_primary", "size", "texture", "mouth"):
            if f in a and not spec.get(f):
                spec[f] = a[f]
        for p in a.get("parts", []):
            if p not in spec.get("parts", []):
                spec.setdefault("parts", []).append(p)
        msg += f"「{hit}」呀～我猜你想要 {a['note']}。 "
    # 具体词
    for cn, en in SHAPE_EN.items():
        if cn in text:
            spec["shape"] = en
    for en, cn in COLOR_OPT:
        if cn in text:
            spec["color_primary"] = en
    for en, cn in SIZE_OPT:
        if cn in text:
            spec["size"] = en
    for p in PART_OPT:
        if p in text and p not in spec.get("parts", []):
            spec.setdefault("parts", []).append(p)
    # 追问必填
    missing = [f for f in REQUIRED_APPEARANCE if not spec.get(f)]
    if missing:
        cn = {"shape": "形状（圆/方/三角…）", "color_primary": "颜色", "size": "大小（小/中/大）"}
        msg += "还想知道：你的小机器人是【" + "、".join(cn[m] for m in missing) + "】呀？"
    else:
        msg += "外形我差不多懂啦！下面把形状/颜色/大小再确认一下，就可以选性格咯～"
    return {"bot_msg": msg, "spec": spec, "missing": missing}


def lookup_personality(pk: str):
    return next((p for p in PERSONALITY if p["k"] == pk), None)


def compile_design(spec: dict):
    """把标准化外形+性格编译成设计规格 JSON。必填缺失或性格非法 → (None, err)。"""
    if not isinstance(spec, dict):
        return None, "spec 必须是对象"
    appr = spec.get("appearance") or {}
    for f in REQUIRED_APPEARANCE:
        if not appr.get(f):
            return None, f"外形必填项缺失: {f}（{REQUIRED_APPEARANCE} 必须齐备才能完成捏脸）"
    pk = spec.get("personality")
    if isinstance(pk, dict):
        pk = pk.get("type")
    pers = lookup_personality(pk) if isinstance(pk, str) else None
    if pers is None:
        return None, f"性格非法或未选: {pk!r}（允许: {[p['k'] for p in PERSONALITY]}）"

    appearance = {k: appr[k] for k in ("shape", "color_primary", "size") if appr.get(k)}
    if appr.get("parts"):
        appearance["parts"] = appr["parts"]
    if appr.get("texture"):
        appearance["texture"] = appr["texture"]

    design = {
        "design": {
            "appearance": appearance,
            "personality": {"type": pers["k"], "expression": pers["face"],
                            "actions": pers["acts"], "tone": pers["tone"]},
            "source": spec.get("source", "text"),
        },
        "build_hint": f"技术组请按此外形({appearance.get('shape')}/{appearance.get('color_primary')}/"
                     f"{appearance.get('size')}"
                     + (f"，带{'-'.join(appearance.get('parts', []))}" if appearance.get("parts") else "")
                     + f")与性格({pers['k']})建模/编程。",
        "image_prompt": _image_prompt(appearance, pers),
        "code_stub": _code_stub(appearance, pers),
        "generated_by": "kidcomm-robot-designer v1",
    }
    return design, None


def _image_prompt(appearance, pers):
    parts = ", ".join(appearance.get("parts", [])) or "no extra parts"
    return (f"a {appearance.get('size')} {appearance.get('color_primary')} {appearance.get('shape')} robot, "
            f"with {parts}, {pers['k']} expression ({pers['face']}), children's drawing style --ar 1:1")


def _code_stub(appearance, pers):
    parts_js = "[" + ", ".join(f'"{p}"' for p in appearance.get("parts", [])) + "]"
    return (f'const robot = new RobotDesign({{\n'
            f'  appearance: {{ shape: "{appearance.get("shape")}", '
            f'colorPrimary: "{appearance.get("color_primary")}", size: "{appearance.get("size")}", '
            f'parts: {parts_js} }},\n'
            f'  personality: "{pers["k"]}",\n'
            f'  facial: PERSONALITY_MAP["{pers["k"]}"].expression,\n'
            f'  motions: PERSONALITY_MAP["{pers["k"]}"].actions\n'
            f'}});\nrobot.mount(scene);')


def _main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    g = sub.add_parser("guide"); g.add_argument("--text", default=""); g.add_argument("--spec", default="{}")
    c = sub.add_parser("compile"); c.add_argument("--spec", required=True)
    args = ap.parse_args()

    if args.mode == "guide":
        try:
            spec = json.loads(args.spec)
        except Exception as e:
            print(json.dumps({"error": f"spec 不是合法 JSON: {e}"})); sys.exit(2)
        if guarded(args.text):
            print(json.dumps({"blocked": True, "bot_msg": "这个我不太方便聊哦～我们专心造小机器人好不好？"}))
            sys.exit(0)
        out = guide(args.text, spec)
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(0)

    if args.mode == "compile":
        try:
            spec = json.loads(args.spec)
        except Exception as e:
            print(json.dumps({"error": f"spec 不是合法 JSON: {e}"})); sys.exit(2)
        design, err = compile_design(spec)
        if err:
            print(json.dumps({"ok": False, "error": err}, ensure_ascii=False)); sys.exit(2)
        print(json.dumps({"ok": True, **design}, ensure_ascii=False))
        sys.exit(0)


if __name__ == "__main__":
    _main()
