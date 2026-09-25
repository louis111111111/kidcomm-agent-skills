# 签名（OMS）说明 — kidcomm

> 评分标准"完整性"要求 Skill 带 OMS 签名（`skill.oms.sig`）。本文说明签名怎么来、现在什么状态。

## 什么是 OMS 签名
NVIDIA Verified Skills 治理五件套之一：用 OpenSSF Model Signing / OMS 对 `SKILL.md` 生成**分离签名**（`skill.oms.sig`），可对照信任锚 `nv-agent-root-cert.pem` 验证"这个 Skill 没被篡改"。签名由**发布到技能目录时的同步流水线**自动产生，不是手写文件。

## 当前状态
- 本仓库的 Skill 已具备签名前的全部工件：`SKILL.md` + `skill-card.md` + `evals/` + `BENCHMARK.md`。
- `skill.oms.sig` **尚未生成**（被列入 `.gitignore`，避免提交占位假签名）。
- 待治理流水线 / 本地 OMS 工具就位后，对每个 Skill 目录执行签名，再把 `.sig` 加入。

## 若要在本地生成（示意）
```bash
# 需 OMS 签名工具与 NVIDIA 信任锚；具体命令以官方 signing 工具为准
oms sign kidcomm-skills/kidcomm-elicit/SKILL.md \
     --root nv-agent-root-cert.pem \
     --out kidcomm-skills/kidcomm-elicit/skill.oms.sig
```
> 注意：签名绑定具体文件哈希，**提示词改动后需重新签名**。这也是我们把提示词集中在 `references/prompt-templates.md`、结构模块化的原因——改一处、重签一次即可。

## 诚实声明
未签名前，Skill 处于"已编目/已扫描/已评测/已文档"四件套状态；签名是发布到目录前的最后一步，不影响本地与 DGX 上的功能运行。
