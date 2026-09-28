# 儿童机器人前端 Skill 设计 · 自然语言 → 可执行指令（混合架构 / 全免费本地）

> 负责人：Louis（前端）。目标：把儿童的模糊自然语言输入，转成机器人可执行的指令。
> 约束：**不花钱**（全部本地开源、离线），同时复用语料/护栏等已有资产。

## 0. 成本结论（为什么免费可行）
| 组件 | 免费方案 | 是否花钱 |
|---|---|---|
| 对话 Agent（槽位填充 chatbot） | 本地开源 LLM（Ollama/vLLM，DGX 跑大模型 / Mac 跑 3–7B 小模型开发） | 0 API 费 |
| 语音识别 ASR | Whisper（faster-whisper / whisper.cpp，本地） | 0 |
| 语音合成 TTS | Piper / ChatTTS（本地）或浏览器 Web Speech | 0 |
| 前端 | Vite + React（或原生），静态托管 | 0 |
| 护栏 / 引导方法 | 复用 kidcomm-safety-guardrail + 既有引导研究 | 0 |

结论：整条链路可 100% 离线本地跑，既免费又构成"数据不出户"的隐私卖点。

## 1. 整体架构（混合）
```
儿童输入 (语音 via Whisper  /  屏幕点选)
   │
   ▼
[前端脚手架层] 卡片/故事/角色扮演引导，让孩子"选"动作+对象+参数  ← Louis 主责，降模糊、低延迟
   │   已收集 slots（可能不完整）
   ▼
[Agent 对话层] 本地 LLM 做：残差消歧 + 指代 grounding + 自由说法兜底 + member-check
   │   输出：补全的 slots / 下一个追问 / “可编译”信号
   ▼
[护栏层] kidcomm-safety-guardrail 复用（确定性，离线）
   ▼
[编译层] intent + slots → 机器人指令 JSON/DSL
   ▼
[确认层] 回给孩子/家长："你想让机器人去拿红色积木，对吗？" → 执行
```

## 2. 前端组件拆分（Louis 的地盘）
1. **引导脚手架组件**
   - 动作卡（move_to / pick_up / play / turn / stop …）
   - 对象选择器（结合摄像头画面的可选物体缩略图）
   - 参数控件（速度/时长/方向滑杆）
   - 故事/角色扮演外框（把指令包装成"帮小机器人完成任务"的情境，降低孩子认知负担）
2. **语音输入组件**：录音 → 本地 Whisper 端点 → 文本，回填到对话框。
3. **对话气泡组件**：展示 Agent 的追问（任务型，不是闲聊）。
4. **确认弹层（member-check）**：执行前一句确认，防误操作。
5. **指令预览组件**：执行前把编译出的 JSON 可视化给孩子/家长看。

## 3. Agent 接口契约（对话层）
- **输入**：`{slots: 已收集槽位, utterance: 孩子最新一句, actions: 机器人可行动作清单}`
- **输出（严格 JSON）**：
  ```json
  {
    "next_action": "ask" | "fill" | "ready",
    "missing_slot": "target" | "param_speed" | null,
    "question": "你说的是桌上那个红色积木吗？",   // 仅 ask 时
    "slots": { "action": "pick_up", "target": {"color":"red","type":"block"} },
    "member_check": "你想让机器人去拿红色积木，对吗？"
  }
  ```
- **约束**：意图只能落在 `actions` 清单内；必须用 member-check 确认后才置 `ready`。

## 4. 机器人指令 schema 草案（需与机器人侧最终对齐）
```json
{
  "action": "pick_up" | "move_to" | "play" | "turn" | "stop",
  "target": { "type": "block"|"person"|"location", "color"?: "red", "id"?: "obj_03", "grounding_ref"?: "camera_frame@t" },
  "params": { "speed"?: 0.5, "duration"?: 3, "angle"?: 30 },
  "confirm": true
}
```
示例：孩子"让机器人去拿红色积木" →
```json
{ "action":"pick_up", "target":{"type":"block","color":"red"}, "params":{}, "confirm":true }
```

## 5. 端到端示例（同一场景串一遍）
1. 孩子说/点："让机器人去拿红色积木"。
2. 前端脚手架：高亮 `pick_up` 卡 + 红色 + 积木（已收 2/3 槽位）。
3. Agent：发现画面里有两个红积木 → `ask`："你说的是左边那个还是右边那个？"
4. 孩子点左边 → `fill` target.id=obj_03，`ready`。
5. 护栏：通过。
6. 编译：输出上面 JSON。
7. 确认层："你想让机器人去拿左边红色积木，对吗？" → 孩子确认 → 下发执行。

## 6. 免费技术栈清单
- **LLM**：Ollama + Qwen2.5 / Llama3.1 / Gemma2（小模型本地；DGX 上可跑 70B+）
- **ASR**：faster-whisper 或 whisper.cpp（本地，支持中文）
- **TTS**：Piper / ChatTTS（本地）或浏览器 SpeechSynthesis（零接入成本）
- **前端**：Vite + React（免费）
- **编排**：轻量 Python/Node 脚本，复用 elicit.py 的 `KIDCOMM_*` 端点解耦模式，指向本地 Ollama

## 7. 与既有 kidcomm 资产的关系
- `kidcomm-safety-guardrail`：直接复用，过滤孩子输入。
- 引导方法（story_stem / roleplay / guided_questions）：复用到前端脚手架的"情境包装"。
- `KIDCOMM_BASE_URL/MODEL/API_KEY` 端点解耦：复用，开发期指向本地 Ollama，DGX 期指向本地大模型，代码零改。

## 8. 待与机器人侧确认
- 指令 schema 的最终字段与机器人执行端是否一致。
- grounding 如何拿到可交互物体清单（摄像头 / 场景图接口）。
- 动作集（actions）的最终清单与参数范围。

## 9. 已知风险
- 儿童 ASR 准确率低于成人：用"点选/卡片"降低语音依赖；Whisper 对儿童口音需实测。
- 本地小模型（开发期）对话能力弱于云端：仅作联调；评审/演示用 DGX 大模型。
- 指代 grounding 最终依赖机器人感知，前端只能"呈现选项 + 追问"，不能凭空解析。
