# 前端脚手架组件模式（Louis 的地盘 · React/Vite）

把"儿童自然语言 → 机器人指令"的模糊问题，先用**可视化脚手架**降维：让孩子"点选"出大部分槽位，Agent 只处理残差。下面是给前端实现的组件清单与设计要点。

## 1. 引导脚手架组件
- **动作卡（ActionCards）**：`pick_up / move_to / play / turn / stop` 五个大按钮，图标+拟声词，点选即填 `action`。
- **对象选择器（ObjectPicker）**：结合摄像头画面的可选物体缩略图（由机器人侧 `grounding` 回传 `id`+缩略），点选填 `target.type`/`id`；颜色作为次级筛选。
- **参数控件（ParamControls）**：速度/时长/方向滑杆，填 `params`，带童趣图标与语音播报当前值。
- **故事/角色扮演外框（StoryFrame）**：把指令包装成"帮小机器人完成任务"的情境（复用 kidcomm-elicit 的 story_stem / roleplay），降低认知负担、避免生硬命令。

## 2. 语音输入组件（VoiceInput）
- 录音 → 本地 Whisper/faster-whisper 端点 → 文本，回填对话框。
- 一句话经 `agent.py` 兜底解析；识别不准时降级为"点选卡片"，不强迫语音。

## 3. 对话气泡组件（DialogBubble）
- 只展示**任务型**追问（`agent.py` 的 `question`），不是闲聊。气泡带动效，配合语音 TTS 播报。

## 4. 确认弹层（MemberCheck）
- `ready` 时弹出 `member_check` 问句（"你想让机器人拿红色积木，对吗？"）。
- **确认前任何指令都不下发**；提供"对/不对（重新选）"两个大按钮。

## 5. 指令预览组件（InstructionPreview）
- 执行前把 `compile.py` 输出的 JSON 可视化（动作图标 + 对象图 + 参数），给孩子/家长一眼看懂"机器人要做什么"。

## 设计铁律
- 低延迟、大按钮、少文字；认知负荷在"选"不在"说"。
- 所有数据本地，禁云上传；语音/画面不离开设备。
- 与 `agent.py` / `compile.py` 通过 JSON 契约对接，前端不内嵌业务逻辑。
