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
