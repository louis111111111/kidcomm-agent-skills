# kidcomm — 亲子引导表达技能族（第三届 NVIDIA DGX Spark 黑客松）

> 给"不会写代码"的你的使用手册。照着做就行。

## 这是什么
一套 **Agent Skill**（符合 Anthropic 开源规范 / NVIDIA 本届标准）。解决一个真实痛点：
**家长想了解孩子对某件事的看法，但直接问孩子听不懂、说不清。** 家长把问题输入手机，机器人/agent 用**经学术验证的儿童访谈方法**（讲故事 / 角色扮演 / 分步提问 / 画图），通过**语音 + 屏幕画面**引导孩子准确表达，再把孩子的意思以家长能懂的方式回传——并且**让孩子确认**"是不是这个意思"。

两个 Skill 串成一条流水线：
```
家长输入"孩子难懂的问题"
      │
      ▼
[0] kidcomm-safety-guardrail   ← 安全闸门（必过，离线规则，不需要模型）
      │
      ▼
[1] kidcomm-elicit            ← 主 Skill：转译问题→引导表达→成员核查→回传家长
      │
      ├─ plan 模式：成人问题 → 适龄引导脚本（故事/扮演/提问/画图）
      └─ summarize 模式：孩子表达 → 家长摘要 + 成员核查
```

## 目录结构
```
kidcomm-skills/
├── README.md                      # 本文件
├── requirements.txt               # 依赖：requests
├── kidcomm-safety-guardrail/      # [0] 安全护栏
└── kidcomm-elicit/                # [1] 亲子引导表达（主）
```
每个 Skill：`SKILL.md`（Agent 读）、`skill-card.md`（治理卡）、`scripts/`（可运行代码）、`evals/`（评测）。

## 第一步：装依赖（一次）
```bash
pip install requests
```

## 第二步：本地怎么测（没有 DGX 也能测）
护栏不需要模型，直接测：
```bash
cd kidcomm-safety-guardrail
python scripts/screen.py --text "我爸爸电话是13800138000"   # 输出 action: block
```
解码/引导需要模型端点。开发期设成任意 OpenAI 兼容 API；组长在 DGX 上换成**本地地址**，代码一行不改：
```bash
export KIDCOMM_BASE_URL="https://你的端点/v1"
export KIDCOMM_MODEL="模型名"
export KIDCOMM_API_KEY="你的key"   # 本地 DGX 可留空
```

## 第三步：跑一遍主流程（示例）
```bash
# 1) 护栏先过滤（家长输入）
cd kidcomm-safety-guardrail
python scripts/screen.py --text "问问孩子为什么不想去幼儿园" --mode input

# 2) plan：把家长问题转成适龄引导脚本
cd ../kidcomm-elicit
python scripts/elicit.py --mode plan --question "问问孩子为什么不想去幼儿园" --age 6

# 3) （机器人用语音+屏幕把孩子-facing 内容交付，采集孩子回答后）summarize：回传家长
python scripts/elicit.py --mode summarize --child "我不想去了，因为小朋友不跟我玩" --question "为什么不想去幼儿园"
```

## 第四步：跑评测（评审要看）
```bash
cd kidcomm-safety-guardrail && python evals/run_eval.py   # 离线 5/5
cd ../kidcomm-elicit && python evals/run_eval.py          # 接模型后出通过率；无端点优雅跳过
```

## 怎么交给组长 / 提交比赛
整个 `kidcomm-skills/` 文件夹打包发出即可。组长：在 DGX Spark 起本地 OpenAI 兼容服务 → 设 `KIDCOMM_*` 环境变量 → 把两个 Skill 目录放进 Agent 的 skills 目录（Hermes/OpenClaw 都认），Agent 按 `SKILL.md` 自动调用。

## 评分对应
- **实用性·创新(25%)**：真实沟通痛点 + "用验证方法引导孩子表达"新角度
- **技术深度**：多模态交付 + 自适应非诱导提问 + 成员核查闭环
- **安全/治理**：确定性护栏 + 五件套（编目/扫描/评测/签名/文档）
- **可验证**：每个 Skill 带 evals 数据集 + 运行器

## 安全边界
- 数据全程本地，禁止云上传（对云端儿童产品的核心卖点）
- 不替孩子下结论、不诊断、不说教
- 给孩子的内容必经护栏 + 适龄过滤
- 表达权在孩子，理解权在家长
