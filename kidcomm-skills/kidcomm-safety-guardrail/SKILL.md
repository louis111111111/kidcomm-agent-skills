---
name: kidcomm-safety-guardrail
description: >
  Use as a mandatory pre-filter before any kidcomm skill processes child speech,
  parent context, or generates child-facing content. It blocks privacy leakage
  (home address, phone number, real names, school, schedule), profanity, violence,
  and any content that induces a child to reveal family information or meets
  strangers. Also use to screen text that will be shown to a 5–10 year old for
  age-appropriateness. Deterministic rules run first (no model needed); an optional
  model-based check runs only when KIDCOMM_GUARDRAIL_MODEL is set.
  Do NOT use this as a content generator; it only screens and flags.
---

# 适龄安全护栏 (Safety Guardrail)

## Overview
本 Skill 是 `kidcomm` 技能族的**安全闸门**。它不参与生成，只做拦截与标注。所有进入解码器/洞察/脚手架的文本都先过这一关。

为什么必须有它：儿童数据 + 家庭隐私是最高敏感级；评审的"安全/治理"维度会重点查。本地离线之外，还要有确定性的规则护栏，不能只靠模型"自觉"。

## When to use
- 孩子语音转写、家长情境进入任何 kidcomm 技能之前
- 任何准备展示给 5–10 岁孩子的文字生成之后
- 任何可能包含家庭隐私字段的内容

## Workflow
1. 调用 `python scripts/screen.py --text "待检测文本" [--mode input|output]`
2. 读取返回 JSON：
   - `action: "allow"` → 放行
   - `action: "warn"` → 轻度问题（如脏话），标记后可由上层决定
   - `action: "block"` → 严重问题（隐私泄露/诱导），**必须阻断**，不得继续
3. 解码器 SKILL.md 已要求"未过护栏不得继续"。

## Detection rules（确定性，无需模型）
- **隐私泄露**：手机号、身份证号、家庭住址+具体信息、真实姓名+学校、日常行程/独处时间
- **诱导**：索要家庭财务、密码、是否独自在家、父母作息
- **脏话/暴力**：中英文脏话、暴力描写
- **适龄**：给孩子的输出不得含恐怖、色情、自伤、危险行为引导

## Output schema
```json
{
  "safe": false,
  "action": "block|warn|allow",
  "hits": [{"rule": "privacy_phone", "snippet": "138xxxx"}],
  "message": "命中隐私泄露：手机号，已阻断"
}
```

## References / Model
- 确定性规则在 `scripts/screen.py` 内，可独立审计
- 设置 `KIDCOMM_GUARDRAIL_MODEL` 后启用模型复核（可选，默认关闭以保证离线可控）
