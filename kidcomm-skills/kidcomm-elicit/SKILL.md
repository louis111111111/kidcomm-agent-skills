---
name: kidcomm-elicit
description: >
  Use when a parent or caregiver wants to understand a child's (ages 5–10) perspective
  on a topic or question that is too abstract, emotional, or hard for the child to grasp
  directly. The skill takes the adult's question, translates it into child-accessible
  formats — a story stem, a role-play/action scenario, a guided question sequence, or a
  drawing prompt — using academically validated child-interview methods, then helps the
  child express accurately through the robot's/agent's voice and on-screen visuals.
  Finally it returns a parent-readable summary of what the child likely meant, after the
  child has confirmed it (member-check). Trigger when a parent says "ask my child why…",
  "help me understand what my kid thinks about…", or "my child can't explain X, help".
  Do NOT fabricate the child's meaning; always member-check with the child; never diagnose
  or preach; never upload data (process locally on DGX Spark); never suggest a "right"
  answer to the child; keep all content age-appropriate and non-leading.
---

# 亲子引导表达 (Kid Elicitation Skill)

## Overview
面向家长的儿童访谈助手。家长把"孩子不好理解的问题"输入手机，本 Skill 用经学术验证的儿童访谈方法（讲故事 / 角色扮演 / 分步引导提问 / 画图），把成人问题转成孩子能参与的形式，引导孩子准确表达，再把孩子的意思以家长能懂的方式回传——并且**让孩子确认**"是不是这个意思"。

核心原则：不替孩子说话，而是用对的方法让孩子自己说出来、让家长真听懂。

## When to use
- 家长想了解孩子对某件事的看法，但直接问孩子听不懂 / 说不清
- 家长输入："问问孩子为什么最近不想去幼儿园""想知道孩子今天最高兴的事"
- 孩子有情绪但表达通道没发育好，需要适龄引导

## Workflow（按顺序执行）
1. **先跑护栏**：调用 `kidcomm-safety-guardrail` 过滤家长输入（隐私 / 诱导 / 不适龄），未过护栏不得继续
2. **收问题**：读入家长的成人语言问题 / 主题
3. **转译（plan）**：运行 `python scripts/elicit.py --mode plan --question "..." [--age 7]`
   - 选 modality（story_stem / roleplay / guided_questions / drawing / mixed）并生成具体脚本
   - 保证：适龄（5–10）、非诱导、暖场先行、开放→聚焦→细节、不给"标准答案"暗示
4. **引导交付**：机器人 / agent 用**语音 + 屏幕画面**把孩子-facing 内容交付；按 warm_up → open → focused → detail 推进（无物理动作，纯语音+视觉）
5. **采集表达**：孩子的回答（语音转写 / 画图描述 / 选择）
6. **成员核查（summarize）**：运行 `python scripts/elicit.py --mode summarize --child "..." --question "..."`
   - 输出家长可读摘要 + 孩子原话引用 + 让孩子确认的 `member_check_question`
   - 把 `member_check_question` 抛回给孩子；若孩子纠正，用纠正内容重新 summarize
7. **回传家长**：摘要 + 原话 + 置信度 / 边界，让家长理解

## Output schema
plan 模式：
```json
{
  "modality": "story_stem|roleplay|guided_questions|drawing|mixed",
  "age_range": "5-10",
  "warm_up": "一句暖场话",
  "facilitation": { "story_stem": "...", "roleplay_script": "...", "question_sequence": ["..."], "drawing_prompt": "..." },
  "on_screen_visual": "屏幕上展示什么（图/词/卡片）",
  "delivery_notes": "语音+画面交付注意事项，避免诱导"
}
```
summarize 模式：
```json
{
  "summary": "家长可读摘要",
  "child_quotes": ["孩子原话"],
  "member_check_question": "让孩子确认的话",
  "confidence": 0.0,
  "caveats": "边界说明（如孩子只说了片段）"
}
```

## References
- `references/methods.md`：学术验证方法 + 出处（讲故事 / 角色扮演 / 分步不诱导提问 / 画图 / 成员核查）
- `references/prompt-templates.md`：plan / summarize 提示词模板

## Boundaries（评审必查，务必遵守）
- 不替孩子下结论，只引导表达
- 不诊断、不说教、不给"正确育儿法"
- 所有数据本地，禁止云上传（DGX Spark 离线）
- 给孩子的内容必经 `kidcomm-safety-guardrail` + 适龄过滤
- 最终理解权在家长，表达权在孩子
