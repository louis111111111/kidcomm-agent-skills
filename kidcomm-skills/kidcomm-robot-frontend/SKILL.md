---
name: kidcomm-robot-frontend
description: >
  Use when a child (ages 5–10) expresses, in natural language or by tapping on-screen
  cards, what they want a companion robot to do — and you must turn that fuzzy input
  into an executable robot instruction. The skill runs a hybrid pipeline: a front-end
  scaffolding layer (action/target/param cards, story or role-play frame) lets the child
  SELECT slots with low latency; a local LLM (or offline keyword fallback) resolves the
  residual ambiguity, grounds references, and produces a member-checked instruction;
  kidcomm-safety-guardrail screens every child utterance; then slots compile to a robot
  instruction JSON with a confirm-before-execute gate. Trigger when a child says or taps
  "让机器人去拿红色积木", "帮我去那边", "停下来", or any "robot do X" intent.
  Not for: adult robot-teaching/programming interfaces, industrial robot scripting,
  clinical or diagnostic scenarios, or generating content unrelated to robot commands.
---

# 儿童机器人前端指令 Skill（自然语言 → 可执行指令）

## Overview
把 5–10 岁儿童的模糊表达（语音/点选）转成机器人可执行的指令 JSON。整条链路**离线本地、零 API 费用**（本地 LLM / Ollama / vLLM，ASR/TTS 本地）。核心思路是**混合架构**：前端脚手架先让孩子"选"出大部分槽位（低延迟、降模糊），Agent 对话层只处理残差歧义，最后确定性编译成指令。

## When to use
- 孩子说/点："让机器人去拿红色积木""帮我去那边""停下来""转个圈"
- 前端已收集到部分槽位（动作/对象/参数），需要补全或确认
- 任何要把"儿童意图"安全转成"机器指令"的环节

## Workflow（按序）
1. **护栏前置**：对孩子输入跑 `kidcomm-safety-guardrail`（`--mode input`），`block` 则立即终止、绝不继续。
2. **脚手架收集**：前端按 `references/scaffolding.md` 渲染动作卡/对象卡/参数控件 + 故事外框，孩子点选即填充 `slots`。
3. **Agent 对话层**：`python scripts/agent.py --utterance "..." --slots '{...}'` 做消歧/grounding/member-check，返回 `next_action: ask|fill|ready`。
   - 无模型时点选+关键词兜底即可跑通（见 `references/agent-contract.md`）。
   - 接 `KIDCOMM_BASE_URL/MODEL/API_KEY`（OpenAI 兼容，本地 Ollama/vLLM）时启用 LLM 细粒度消歧。
4. **确认门（member-check）**：`ready` 时把 `member_check` 问句抛回孩子/家长确认，**确认前不得下发**。
5. **编译**：`python scripts/compile.py --slots '{...}'` → 机器人指令 JSON（`confirm:true`）。
6. **下发执行**：指令预览给孩子/家长看后，交给机器人执行端。

## Output schema（机器人指令，见 references/instruction-schema.md）
```json
{
  "action": "pick_up|move_to|play|turn|stop",
  "target": { "type": "block|ball|person|location|toy", "color"?: "red", "id"?: "obj_03" },
  "params": { "speed"?: 0.5, "duration"?: 3, "angle"?: 30 },
  "confirm": true
}
```

## Reuse（复用既有 kidcomm 资产）
- `kidcomm-safety-guardrail`：步骤 1 强制复用，确定性离线。
- `kidcomm-elicit` 的 story_stem / roleplay 方法：步骤 2 的"情境包装"外框。
- 端点解耦 `KIDCOMM_*`：开发期指本地 Ollama，DGX 期指本地大模型，代码零改。

## Boundaries（评审必查）
- 意图只能落在 `action` 清单内；超出能力一律 `ask` 或拒绝。
- 绝不绕过护栏；绝不把隐私/危险指令编译下发。
- 全程本地、禁云上传；最终确认权在孩子/家长。
