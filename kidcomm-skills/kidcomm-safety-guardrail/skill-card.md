# Skill Card — kidcomm-safety-guardrail

| 字段 | 内容 |
|------|------|
| **Skill 名称** | kidcomm-safety-guardrail（适龄安全护栏） |
| **所属技能族** | kidcomm（亲子沟通解码） |
| **版本** | 0.1.0 |
| **一句话定位** | kidcomm 技能族的强制前置安全闸门，拦截隐私泄露/诱导/脏话/不适龄内容 |
| **触发场景** | 任何 kidcomm 文本进入处理前；任何给孩子的输出生成后 |
| **输入** | 任意待检测文本 + mode(input/output) |
| **输出** | `{safe, action(allow/warn/block), hits, message}` |
| **模型依赖** | 无（确定性规则）；可选模型复核 |

## 治理五件套状态
- [x] **Cataloged**：已编目
- [x] **Scanned**：纯规则脚本，无外部调用
- [x] **Evaluated**：`evals/evals.json`（命中率 + 误杀率）
- [ ] **Signed**：待 OMS 签名
- [x] **Documented**：本 Card

## 安全边界
- 只拦截、不生成
- 严重命中（隐私/诱导）必须阻断，不可绕过
- 离线可用，不依赖网络

## 分发与责任（NVIDIA Verified Skills 规范字段）
| 字段 | 内容 |
|------|------|
| **Owner** | 2026 NVIDIA DGX Spark 黑客松 · kidcomm 队（Louis Beaton 等） |
| **License** | MIT（本仓库代码）；接入的模型权重依各自许可 |
| **Deployment Geography** | 本地优先（DGX Spark / 任意 OpenAI 兼容端点），无云依赖、无数据出境 |
| **Requirements** | Python 3.10+；可选 `KIDCOMM_GUARDRAIL_MODEL` 启用模型复核 |
| **Dependencies** | 无第三方包（纯标准库，可独立审计） |
| **Risks & Mitigations** | 规则无法穷尽语义变体 → 红队持续对抗（44 条，误杀率 0%）+ 可选模型复核；误杀 → 双模式 + 负向用例评测约束 |
