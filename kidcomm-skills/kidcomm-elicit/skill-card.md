# Skill Card — kidcomm-elicit

| 字段 | 内容 |
|------|------|
| **Skill 名称** | kidcomm-elicit（亲子引导表达） |
| **所属技能族** | kidcomm |
| **版本** | 0.2.0 |
| **一句话定位** | 家长输入难懂问题 → 用验证过的儿童访谈法转成故事/扮演/提问/画图 → 引导孩子说准 → 回传家长（孩子已确认） |
| **触发场景** | 家长想了解孩子视角但孩子听不懂/说不清；输入抽象或情绪化问题 |
| **输入** | 家长的成人语言问题 / 主题 + 孩子年龄（可选） |
| **输出** | plan：适龄引导脚本；summarize：家长可读摘要 + 成员核查 |
| **依赖技能** | kidcomm-safety-guardrail（前置过滤） |
| **交付方式** | 机器人/agent 语音 + 屏幕画面（无物理动作） |

## 治理五件套状态
- [x] Cataloged / [x] Scanned / [x] Evaluated / [ ] Signed / [x] Documented

## 安全边界
- 不替孩子下结论，只引导
- 不诊断、不说教
- 本地离线，禁止云上传
- 必经适龄护栏；表达权在孩子，理解权在家长

## 分发与责任（NVIDIA Verified Skills 规范字段）
| 字段 | 内容 |
|------|------|
| **Owner** | 2026 NVIDIA DGX Spark 黑客松 · kidcomm 队（Louis Beaton 等） |
| **License** | MIT（本仓库代码）；接入的模型权重依各自许可 |
| **Deployment Geography** | 本地优先（DGX Spark / 任意 OpenAI 兼容端点），无云依赖、无数据出境 |
| **Requirements** | Python 3.10+；`KIDCOMM_BASE_URL`/`KIDCOMM_MODEL`/`KIDCOMM_API_KEY` 指向 OpenAI 兼容端点（DGX 本地大模型或开发期任意端点） |
| **Dependencies** | 仅 `requests`（模型调用，惰性导入，无端点时优雅跳过）；前置 `kidcomm-safety-guardrail` |
| **Risks & Mitigations** | 模型可能幻觉/诱导 → 确定性护栏前置 + 成员核查（member-check）；数据隐私 → 全程本地、禁云上传 |
