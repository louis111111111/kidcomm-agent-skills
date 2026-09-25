# kidcomm — 亲子引导表达（第三届 NVIDIA DGX Spark 黑客松 · Agent Skills）

> 面向家长的儿童访谈助手。家长把"孩子难懂的问题"输入手机，机器人/agent 用**经学术验证的儿童访谈方法**（讲故事 / 角色扮演 / 分步提问 / 画图），通过**语音 + 屏幕画面**引导孩子准确表达，再把孩子的意思以家长能懂的方式回传——并且**让孩子确认**（member-check）。
> 核心卖点：**本地离线，孩子声音最敏感数据不出户**（DGX Spark）。

## 这个仓库是什么
- `kidcomm-skills/` —— 两个符合 Agent Skills 规范的 Skill：`kidcomm-safety-guardrail`（安全护栏，离线可跑）+ `kidcomm-elicit`（亲子引导表达，主）。
- 设计/评分/验证文档（根目录）：
  - `亲子引导表达Skill设计.md` —— 设计方案
  - `评分标准映射.md` —— 6 项评分标准逐条对齐（含诚实的"不适用"标注）
  - `BENCHMARK.md` —— 评测与验证报告
  - `pilot-protocol.md` —— Wizard-of-Oz 真人体验方案（无 DGX 即可做）
  - `demo-storyboard.md` —— 3–5 分钟演示分镜 + 安全桥段
  - `征文-十日谈.md` —— 参赛征文

## 快速开始
```bash
pip install -r kidcomm-skills/requirements.txt
# 护栏（离线，无需模型）
cd kidcomm-skills/kidcomm-safety-guardrail && python evals/run_eval.py
# 引导（需模型端点：开发期任意 OpenAI 兼容；DGX 上本地大模型）
export KIDCOMM_BASE_URL="..." KIDCOMM_MODEL="..." KIDCOMM_API_KEY="..."
cd ../kidcomm-elicit && python scripts/elicit.py --mode plan --question "问问孩子为什么不想去幼儿园" --age 6
```

## 验证（可验证性维度）
- 自动化：`evals/`（护栏 5/5 离线通过）
- 真人 pilot：`pilot-protocol.md`（Wizard-of-Oz，无需 DGX）
- 自对弈仿真：`kidcomm-skills/validate.py`（**由组长在 DGX 执行**，输出量化报告）

## 安全边界
数据全程本地，禁止云上传；不替孩子下结论、不诊断、不说教；给孩子的内容必经护栏。表达权在孩子，理解权在家长。

## 评分对应（详见 `评分标准映射.md`）
实用性·创新(25%) / 技术深度(25%) / 完整性(20%) / 平台适配(15%) / 演示(10%) / 征文(5%)——命中"形"（离线、自然语言→计划、negative triggers、多 Skill、evals+card+benchmark+签名、演示安全桥段、征文），机器人专属项（运动学/TAO/Isaac/Jetson）如实标注不适用。
