# kidcomm — 亲子引导表达技能族

## 这是什么
一套 **Agent Skill**（符合 Anthropic 开源规范）。解决一个真实痛点：
**家长想了解孩子对某件事的看法，但直接问孩子听不懂、说不清。** 家长把问题输入手机，机器人/agent 用**经学术验证的儿童访谈方法**（讲故事 / 角色扮演 / 分步提问 / 画图），通过**语音 + 屏幕画面**引导孩子准确表达，再把孩子的意思以家长能懂的方式回传——并且**让孩子确认**"是不是这个意思"。

四个 Skill（含机器人前端指令、儿童捏脸/捏性格两个新方向）：
```
家长输入"孩子难懂的问题"
      │
      ▼
[0] kidcomm-safety-guardrail   ← 安全闸门
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
├── kidcomm-safety-guardrail/      # [0] 安全护栏（离线）
├── kidcomm-elicit/                # [1] 亲子引导表达（主）
├── kidcomm-robot-frontend/        # [2] 儿童自然语言 → 机器人指令（混合架构）
└── kidcomm-robot-designer/        # [3] 儿童捏脸/捏性格 → 技术组设计稿
```
每个 Skill：`SKILL.md`（Agent 读）、`skill-card.md`（治理卡）、`scripts/`（可运行代码）、`evals/`（评测）。

## 第一步：装环境
```bash
pip install requests
```

## 第二步：本地怎么测
护栏不需要模型，直接测：
```bash
cd kidcomm-safety-guardrail
python scripts/screen.py --text "我爸爸电话是13800138000"   # 输出 action: block
```
解码/引导需要模型端点：
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

## 第四步：跑评测
```bash
cd kidcomm-safety-guardrail && python evals/run_redteam.py --guardrail .   # 离线红队 44/44
cd ../kidcomm-elicit && python evals/run_eval.py          # 接模型后出通过率；无端点优雅跳过
```

## 第五步：测新前端 Skill（儿童自然语言 → 机器人指令）
无需模型即可离线跑通混合架构核心链路（护栏→Agent→编译），含负向安全用例：
```bash
cd kidcomm-robot-frontend
python evals/run_eval.py          # 离线 8/8：编译 / Agent 兜底 / 护栏拦截 / 非法拒绝

# 单步演示
python scripts/agent.py --utterance "让机器人去拿红色积木"        # 关键词兜底 → ready + member_check
python scripts/compile.py --slots '{"action":"pick_up","target":{"type":"block","color":"red"}}'  # → 指令 JSON
```
接本地 LLM（Ollama/vLLM）做细粒度消歧：`--model` 并设 `KIDCOMM_BASE_URL/MODEL/API_KEY`。

## 第六步：测设计 Skill（儿童捏脸/捏性格 → 技术组设计稿）
无需模型即可离线跑通设计逻辑（抽象→具体引导 + 必填校验 + 性格映射 + 编译）：
```bash
cd kidcomm-robot-designer
python evals/run_eval.py          # 离线 5/5：guide 引导 / compile 校验 / 性格合法性

# 单步演示
python scripts/design.py guide --text "我想要一个可爱的会飞的小机器人"   # 抽象词 → 具体属性 + 追问
python scripts/design.py compile --spec '{"appearance":{"shape":"round","color_primary":"green","size":"medium","parts":["翅膀"]},"personality":"brave","source":"text"}'  # → 设计规格 JSON（含 code_stub / image_prompt）
```
> 接入方式：队友直接调用 `scripts/design.py`（guide/compile 两个子命令）并改 `corpus/corpus.json` 即可扩展映射，**无需前端**。本仓库不含在线交互原型（那只是本地体验用，不随 Skill 发布）。


