# Skill Card — kidcomm-robot-frontend

| 字段 | 内容 |
|------|------|
| **Skill 名称** | kidcomm-robot-frontend（儿童机器人前端指令） |
| **所属技能族** | kidcomm（亲子沟通解码 → 机器人指令） |
| **版本** | 0.1.0 |
| **一句话定位** | 儿童自然语言/点选 → 安全可执行的机器人指令（混合架构、全本地免费） |
| **触发场景** | 孩子表达"让机器人做 X"；前端已收集部分槽位需补全/确认 |
| **输入** | 孩子 utterance（语音转写/文本）+ 已收集 slots + 机器人动作清单 |
| **输出** | 机器人指令 JSON（action/target/params/confirm）+ member-check 问句 |
| **依赖技能** | kidcomm-safety-guardrail（强制前置）、可选 kidcomm-elicit（情境包装） |
| **模型依赖** | 可选：KIDCOMM_BASE_URL/MODEL/API_KEY（OpenAI 兼容本地端点）；无模型走关键词兜底 |

## 治理五件套状态
- [x] Cataloged / [x] Scanned / [x] Evaluated / [ ] Signed / [x] Documented

## 分发与责任（NVIDIA Verified Skills 规范字段）
| 字段 | 内容 |
|------|------|
| **Owner** | 2026 NVIDIA DGX Spark 黑客松 · kidcomm 队（Louis Beaton 等） |
| **License** | MIT（本仓库代码）；接入的模型权重依各自许可 |
| **Deployment Geography** | 本地优先（DGX Spark / 本地 Ollama / vLLM），无云依赖、无数据出境 |
| **Requirements** | Python 3.10+；可选 `KIDCOMM_*` 端点启用 LLM 消歧 |
| **Dependencies** | 纯标准库（确定性编译/兜底）；`requests` 仅 LLM 模式惰性导入、无端点时跳过；前置 kidcomm-safety-guardrail |
| **Risks & Mitigations** | 儿童 ASR 弱 → 点选/卡片降语音依赖；小模型弱 → 仅联调、评审用 DGX 大模型；grounding 依赖机器人感知 → 前端只呈现选项+追问，不凭空解析；安全 → 强制护栏前置 + 确认门 |

## 安全边界
- 意图仅限机器人动作清单，超出即 ask/拒绝
- 护栏未过绝不编译下发
- 确认门前不得执行
- 全程本地、禁云上传
