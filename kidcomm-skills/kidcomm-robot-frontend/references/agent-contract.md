# Agent 对话层接口契约（scripts/agent.py）

混合架构中"对话层"的输入/输出。可在**无模型**时用中文关键词兜底跑通，也可接本地 LLM 做细粒度消歧。

## 输入
```json
{
  "utterance": "让机器人去拿红色积木",     // 孩子最新一句（语音转写/文本）
  "slots": { "action": "pick_up" },        // 前端脚手架已收集的槽位（可能不完整）
  "actions": ["pick_up","move_to","play","turn","stop"]  // 机器人可行动作清单
}
```
CLI：`python scripts/agent.py --utterance "..." --slots '{...}' [--actions ...] [--model]`
（`--model` 时尝试 `KIDCOMM_BASE_URL/MODEL/API_KEY` 端点，失败自动回退兜底。）

## 输出（严格 JSON）
```json
{
  "next_action": "ask | fill | ready",
  "missing_slot": "action | target | null",
  "question": "你说的是哪个呀？能指给我看吗？",   // 仅 ask 时
  "slots": { "action": "pick_up", "target": {"type": "block", "color": "red"} },
  "member_check": "你想让机器人拿红色积木，对吗？"  // 仅 ready 时
}
```

## 状态机
- `ask`：信息不足，抛出 `question` 让孩子补槽位（前端高亮对应卡片）。
- `fill`：本层补全了槽位，返回更新后的 `slots`（本实现把 fill 并入 ready 前的 ask/ready 两态，补全即进 ready）。
- `ready`：槽位齐备，**必须先经 `member_check` 确认**才允许编译下发。

## 约束
- 意图只能落在 `actions` 清单内；超出即 `ask`（引导点选）或拒绝。
- 关键词兜底覆盖常见中文动词/颜色/物体；接 LLM 后处理口语化、指代、省略。
- 绝不输出"已编译指令"——编译是 `compile.py` 的职责，分层解耦。
