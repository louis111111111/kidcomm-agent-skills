# Skill Card — kidcomm-robot-designer

| 字段 | 内容 |
|------|------|
| **Skill 名称** | kidcomm-robot-designer（儿童机器人设计：捏脸/捏性格） |
| **所属技能族** | kidcomm（亲子沟通解码 → 机器人设计） |
| **版本** | 0.1.0 |
| **一句话定位** | 儿童草图/自然语言 → 标准化外形+性格 → 技术组可执行的机器人设计规格（甚至代码） |
| **触发场景** | 孩子想从 0 造机器人（画画或描述）；抽象词需具体化；需产出可交付设计稿 |
| **输入** | 孩子草图（图像）/ 自然语言描述 + 已选外形/性格 |
| **输出** | 设计规格 JSON（appearance/personality/build_hint/image_prompt/code_stub） |
| **依赖技能** | kidcomm-safety-guardrail（强制前置） |
| **模型依赖** | 可选：图像生成（ComfyUI/SD/FLUX 本地）、LLM（`KIDCOMM_*`）；无模型走关键词/语料兜底 |

## 治理五件套状态
- [x] Cataloged / [x] Scanned / [x] Evaluated / [ ] Signed / [x] Documented

## 分发与责任（NVIDIA Verified Skills 规范字段）
| 字段 | 内容 |
|------|------|
| **Owner** | 2026 NVIDIA DGX Spark 黑客松 · kidcomm 队（Louis Beaton 等） |
| **License** | MIT（本仓库代码）；接入的模型权重依各自许可 |
| **Deployment Geography** | 本地优先（DGX Spark / 本地图像模型 + LLM），无云依赖、无数据出境 |
| **Requirements** | Python 3.10+；可选 `KIDCOMM_*` 端点（图像/LLM） |
| **Dependencies** | 纯标准库（确定性编译/语料兜底）；图像/LLM 仅部署期接入；前置 kidcomm-safety-guardrail |
| **Risks & Mitigations** | 儿童表达天马行空 → 必填目录兜底 + agent 引导；图像生成需算力 → 开发期先用提示词+草图卡；安全 → 强制护栏前置 |

## 安全边界
- 外形必填项未齐不"完成捏脸"
- 意图仅限机器人外观/性格；超出引导回正题
- 护栏未过绝不继续
- 全程本地、禁云上传
