# DGX Spark 黑客松评审标准 × 三份文档对应解读

> 基于官方评审标准截图 + 三份训练营 PDF（刘春晖《NVIDIA Skills 开发实战》、何琨《DGX Spark Agent Skills 黑客松训练营分享》、周旭《StepFun 多模态 × NV-AgentSkills-Harness 演进实践》）整理。

---

## 一、总策略

**选一个具体垂类场景，用 DGX Spark GB10 本地跑通“多模态感知 → Agent 决策 → Skill 执行”的闭环，至少设计 2–3 个协同 skill，补齐 Verified Skills 的治理产物（skill-card / evals / benchmark / 签名），并把 StepFun 模型作为 LLM/VLM backbone。**

---

## 二、评分标准逐项映射

### 1. 项目实用性、行业落地价值与技术创新性（25%）

**官方描述**：技术实现、架构与方案具备创新性，充分体现 DGX Spark 平台优势，突破传统思路并解决技术痛点。

| 维度 | 文档依据 | 具体落点 | 避坑提示 |
|------|---------|---------|---------|
| 行业价值 | 刘春晖 P11–P14 | NVIDIA skills 覆盖 41 条产品线，重点落地场景：**RAG Blueprint（企业知识库/智能客服）、cuOpt（物流调度/量化金融）、VSS（安防/视频运营）、DeepStream（工业视觉/智慧交通）** | 不要只做“能对话的 ChatBot”，要锚定一个可量化业务指标的场景（如“园区视频事件检索从 30 分钟降到 3 分钟”） |
| 技术创新 | 何琨 P8–P12 | 把两个官方 TAO skill（`tao-generate-image-grounding` + `tao-generate-referring-expressions`）串成自研 `local-pedestrian-detector`，展示“多技能协同” | 不要泛泛堆模型，要展示“因为用了 skill，原本需要多名工程师的 pipeline 被压缩成一句话” |
| DGX Spark 优势 | 何琨 P9、刘春晖 P9 | 本地部署：数据不出域、低延迟、离线可用；DGX Spark 用 30081 端口 standalone LLM | 避免把 DGX Spark 当普通云服务器用，要突出“边缘/本地化”带来的差异化价值 |

**建议选题方向**：
- 安防/园区：VSS 视频摘要 + 自然语言检索 + 本地 VLM
- 工业质检：DeepStream 检测跟踪 + TAO 视觉 skill + 缺陷报告生成
- 物流/金融：cuOpt 路由优化 + 自然语言参数输入 + StepFun 模型理解约束

---

### 2. 智能体与模型优化技术深度（25%）

**官方描述**：多智能体协同、模型调优深度、Skills 设计与融合、差异化技术方案。

| 维度 | 文档依据 | 具体落点 | 避坑提示 |
|------|---------|---------|---------|
| 多智能体/多 Skill 协同 | 何琨 P8、P12 | 官方 skill 可组合：Grounding（定位）→ KITTI 转换 → Referring Expressions（语言描述）→ 自研后处理 | 不要把所有逻辑写进一个巨大 prompt，要按能力拆成多个 skill，体现“Skill 即能力资产” |
| Skills 设计与融合 | 刘春晖 P15 | 三条心法：**窄触发强路由、前置提问、安全边界内嵌** | 在 `SKILL.md` 的 `description` 里写清楚 trigger keywords 和 negative triggers（何时不触发），否则 Claude 会出现 silent failure（周旭 P19） |
| 模型调优深度 | 何琨 P9、周旭 P7–P9 | GB10 上 vLLM 需设 `VLLM_USE_DEEP_GEMM=0` 和 `--moe-backend triton`；StepFun 3.7 Flash（198B/11B active，256K 上下文，400 tok/s）原生多模态 + 工具调用合流 | 换模型只改 `base_url` / `model_name` / `api_key` 不够，要做回归评测验证行为等价（周旭 P9、P16） |
| 差异化方案 | 周旭 P6、P11 | 触发工程 + 渐进式披露：常驻 metadata 仅约 100 token，命中才展开正文，< 5K token，按需加载 scripts/references | 避免“343 个 skill 全装”的思路，展示你设计的 skill 如何精准路由、节省 token |

**关键技术点 checklist**：
- [ ] 至少 2 个 skill 有明确输入输出契约
- [ ] 使用 frontmatter 定义触发词和 negative triggers
- [ ] 关键参数缺失时主动提问，不让 Agent 猜测
- [ ] 接入 StepFun 3.7 Flash 或 3.5 Flash 作为模型 backbone
- [ ] 有本地 vLLM/模型部署调优细节

---

### 3. 项目完整性（20%）

**官方描述**：功能完整、运行稳定，前后端完整、文档规范详实，实现逻辑清晰，可顺利完成演示。

| 维度 | 文档依据 | 具体落点 | 避坑提示 |
|------|---------|---------|---------|
| 功能完整 | 何琨 P12 | 自研 skill 目录结构：`SKILL.md` + `scripts/` + `scripts/run.sh` + `scripts/pedestrian_detect.py` | 不要只有 prompt，要有可执行脚本和清晰的数据流 |
| 运行稳定 | 何琨 P9–P10 | 官方 skill 保持原样，环境差异放外部适配层；本地端点和容器适配由 `workspace/tools/run-official-skill.sh` 处理 | 不要直接修改官方 skill，否则签名失效；要提前解决 GB10 上 vLLM 的 DeepGEMM 问题 |
| 文档规范 | 刘春晖 P3、P8 | **Verified Skills 五件套**：Cataloged / Scanned / Evaluated / Signed / Documented；Skill Card 回答 Owner / License / Requirements / Risks & Mitigations 等 | 产出 `skill-card.md`，把治理产物当成项目文档的一部分 |
| 可验证性 | 刘春晖 P5–P7 | `evals/evals.json`（含负向用例）+ `BENCHMARK.md` + `skill.oms.sig` 签名 | 负向用例很重要：测试“正确答案是不调用该 skill”的场景 |

**推荐交付物清单**：
```
project/
├── skills-src/
│   └── your-custom-skill/
│       ├── SKILL.md
│       ├── skill-card.md
│       ├── skill.oms.sig          # 或自签名流程说明
│       ├── evals/
│       │   └── evals.json         # 含负向用例
│       ├── BENCHMARK.md
│       └── scripts/
├── workspace/
│   └── tools/
│       └── run-official-skill.sh  # 适配层
├── demo-video.mp4
└── README.md
```

---

### 4. 平台适配性（15%）

**官方描述**：充分发挥 DGX Spark 平台的全栈能力，合理运用 NVIDIA 技术栈、开源模型和 SDK 等工具以及 StepFun 阶跃星辰模型的使用。

| 维度 | 文档依据 | 具体落点 | 避坑提示 |
|------|---------|---------|---------|
| DGX Spark 全栈 | 何琨 P9 | 硬件：NVIDIA GB10（ARM64/SBSA）；运行时：OpenClaw + TAO 7.1.0 Data Services（ARM64）+ vLLM 0.28.0 + Qwen3.6-35B-A3B-FP8 | 在 README 和 demo 中明确声明“运行在 DGX Spark GB10 本地” |
| NVIDIA 技术栈 | 刘春晖 P11–P14、何琨 P5 | 从 41 条产品线中选：Agentic AI / Training / Inference / Decision Optimization / Data Science / Vision AI / Physical AI & Omniverse | 不要只用通用 Python 库，要调用 NVIDIA 特定工具（TAO、DeepStream、VSS、cuOpt、RAG Blueprint 等） |
| 开源模型 | 何琨 P9 | Qwen3.6-35B-A3B-FP8 约 37.5 GB 权重，国内可从 ModelScope 下载 | 提前测试模型下载和加载流程，避免比赛现场网络问题 |
| StepFun 模型 | 周旭 P7–P9、P16 | Step 3.7 Flash 原生多模态 + 工具调用，Apache-2.0 开源，Day-0 上 NVIDIA NIM；StepAudio-Skills 也已打包 | 如果视觉或 Agent 能力用 StepFun，要展示它如何通过 OpenAI 兼容端点替代或增强 NVIDIA 模型 |

**技术栈 checklist**：
- [ ] 明确使用 DGX Spark GB10（ARM64）
- [ ] 使用至少一个 NVIDIA SDK/Blueprint（TAO / DeepStream / VSS / cuOpt / RAG Blueprint）
- [ ] 接入 StepFun 3.7/3.5 Flash 或 StepAudio
- [ ] 展示本地部署 vs 云端调用的优势

---

### 5. 演示效果（10%）

**官方描述**：Demo 视频演示流畅、展示清晰、逻辑严谨，直观呈现作品价值。

| 维度 | 建议 | 参考 |
|------|------|------|
| 流畅 | 视频 3–5 分钟，提前录制关键路径；现场只做可控的简短展示 | 何琨 P11–P12 的 OpenClaw 提示词可直接借鉴 |
| 清晰 | 分镜脚本：① 业务痛点 ② 一句话指令 ③ Agent 加载 skill ④ 中间产物可视化（grounding 框、resolved.yml、签名验证 PASS）⑤ 最终结果 | 刘春晖 P9 的 VSS Pipeline、何琨 P11 的 grounding/referring 结果截图 |
| 逻辑严谨 | 展示“不带 skill 会怎样”和“带 skill 会怎样”的对比，呼应 SkillEvaluator 的 baseline → with-skill 差值 | 刘春晖 P6 |
| 价值直观 | 用具体数字：准确率提升 X%、耗时减少 Y%、部署步骤从 N 步降到 M 步 | BENCHMARK.md 里的五维评分 |

**建议分镜（3 分钟）**：
1. 0:00–0:30 痛点：传统方式需要 3 个工具 + 5 个脚本 + 参数易错
2. 0:30–1:30 解决方案：一句自然语言 → Agent 加载 skill → 自动路由到官方/自研 skill → 本地模型推理
3. 1:30–2:30 结果展示：可视化结果 + BENCHMARK.md 数据 + 签名验证 PASS
4. 2:30–3:00 价值总结：行业落地价值 + 技术优势

---

### 6. 赛事征文（5%）

**官方描述**：参赛成果记录，DGX Spark 黑客松“十日谈”开发历程。

| 建议 | 内容 |
|------|------|
| 按天记录 | Day 1 选题 → Day 2–3 环境搭建（GB10、vLLM、StepFun 模型下载）→ Day 4–6 skill 设计与联调 → Day 7–8 评测与 benchmark → Day 9–10 Demo 录制与文档 |
| 突出踩坑 | DeepGEMM 报错、skill 不触发、官方 skill 签名验证失败、负向用例设计等 |
| 配截图 | OpenClaw 会话、grounding 结果、resolved.yml、签名验证 PASS/FAILED |
| 体现成长 | 从“手写 glue code”到“技能资产”的认知转变（呼应周旭 P3、P20） |

---

## 三、参赛者行动清单（按优先级）

### 本周必做
1. **确定选题**：从 VSS / DeepStream / cuOpt / RAG Blueprint 中选一个最贴近自己背景的垂类。
2. **跑通环境**：在 DGX Spark GB10 上部署 vLLM + StepFun 3.7 Flash（或 Qwen3.6-35B-A3B-FP8），验证 `VLLM_USE_DEEP_GEMM=0` + `--moe-backend triton`。
3. **安装官方 skill**：`npx skills@latest add nvidia/skills --skill vss-deploy-profile`（或 deepstream / cuopt / rag-blueprint）并跑通最小样例。

### 第二周
4. **设计自研 skill**：基于官方 skill 做组合或扩展，明确输入输出契约和 trigger keywords。
5. **补齐治理产物**：`skill-card.md`、`evals/evals.json`（含负向用例）、`BENCHMARK.md`、签名（或自签名说明）。
6. **接入 StepFun 模型**：把部分 LLM/VLM 调用切到 StepFun 端点，做回归对照。

### 第三周
7. **录制 Demo**：按 3 分钟分镜预录，留出可现场展示的安全环节。
8. **写十日谈**：每天 200–300 字 + 1 张截图。
9. **最终检查**：对照本文件的 6 大评分项 checklist，逐项打勾。

---

## 四、高频避坑速查

| 坑 | 正确做法 | 文档出处 |
|---|---------|---------|
| 直接改官方 skill | 环境差异放适配层，业务逻辑进自研 skill | 何琨 P10 |
| Skill 不被触发 | 检查 `description` 里的 trigger keywords 和 negative triggers | 周旭 P6、P19 |
| GB10 上 vLLM 报 CUDA_ERROR_INVALID_IMAGE | `VLLM_USE_DEEP_GEMM=0` + `--moe-backend triton` | 何琨 P9 |
| 只展示正向 case | 必须设计负向用例：测试“不该调用 skill 时不调用” | 刘春晖 P6 |
| 模型切了但行为变了 | 做回归评测，不要只改 `base_url` | 周旭 P9、P16 |
| 能力全写进一个 prompt | 拆成多个 skill，窄触发、强路由 | 刘春晖 P15 |
| 打印明文 API token | 安全边界内嵌，token 走环境变量或 secrets | 刘春晖 P9、P15 |

---

## 五、总结

**评委想看到的不是"用了很多技术"，而是"用 DGX Spark + NVIDIA Agent Skills + StepFun 模型，把一个有真实痛点的垂类场景，做成了可验证、可复用、可演示的技能资产。"**

---

## 六、往届获奖项目分析（参赛参考）

> 下面是前两届（中国区）的冠亚季军，以及它们透露的评审偏好。

### 第一届 · NVIDIA DGX Spark Sky Hackathon（全栈 AI 开发大赛，超千名开发者）
主题偏向"企业级 AI 落地、系统化工程能力"。
- 🏆 **冠军 Starfire — AI Agent 团队治理系统**：解决多 Agent 协作混乱、权限不可控、记忆越界；DGX Spark + OpenClaw / NemoClaw + CUDA。
- 🥈 **亚军 化工智能巡检助手**：高危场景人工巡检风险高、多模态融合难；DGX Spark + TensorRT-LLM + NemoClaw，工业级本地部署边缘 AI 巡检。
- 🥉 **季军 DragonSlayer 金融轻量化模型**：金融交易超低时延、私有化；NeMo 蒸馏 + TensorRT-LLM + DGX Spark，模型压到 2.8GB、25ms 级决策。

### 第二届 · NVIDIA DGX Spark 黑客松（主题"让 Agent 创作一切"，联合 StepFun 阶跃星辰）
112 支团队、2122 名开发者，13 支入围上海总决赛。
- 🏆 **冠军 卡皮巴拉队 — Super Idol Master（数字角色资产 Agent 流水线）**：把原画 → T-Pose → 3D 建模 → 拓扑 → 绑骨串成可恢复 / 可检查 / 可回退的 Agent 工作流；StepFun 处理语言与图像，DGX Spark + CUDA‑X 跑 GPU 密集 2D/3D。
- 🥈 **亚军 注意力算得队（上海交大 DDST 实验室）— PLLM HiberFlow 负载感知推理框架**：前台忙时让出资源、闲时恢复；NVML 采集状态 + 分级休眠 + HiberCache 持久化；底层跑 Nemotron 3 Super 120B。
- 🥉 **季军 树状图设计者队 — E-MARS 自主消防救援机器人**：火灾断网环境端侧自主决策；三 Agent 分时间尺度（InternVLA 眼前动作 / Step3‑VL 综合判断 / Step 3.7 Flash 维护目标），权重冻结直接接入机器人闭环，Jetson + Isaac 仿真。

### 往届共性规律（给本届的启示）
1. **多 Agent / 多 Skill 工作流编排**是高频胜点（Starfire 治理、Super Idol Master 流水线、E-MARS 三层 Agent）。本届的 Agent Skills 正好把"能力封装成 skill"，直接呼应这一点。
2. **把 DGX Spark 的本地算力用满**：128GB 统一内存跑 70B/120B 级模型、本地推理、隐私 / 离线优势，是评委反复强调的差异化。
3. **深度用 NVIDIA 技术栈**：NemoClaw（安全沙箱）、TensorRT-LLM、NeMo 蒸馏、CUDA‑X、Isaac（具身）反复出现。
4. **真实场景 + 工程完成度**：工业巡检、金融、救援、数字内容生产——都有明确业务指标和可演示 demo，不是玩具 prompt。
5. **StepFun 模型集成**（第二届起）：用 Step 系列做语言 / 多模态 backbone，叠加 NVIDIA 本地算力。

> **一句话公式**：往届冠军 = 一个真实痛点 + DGX Spark 本地算力 + NVIDIA 技术栈深度 + 多 Agent/多 Skill 编排 + 可演示工程。本届把"Skill"从加分项变成了核心赛题，正好用 Verified Skills 五件套（skill-card / evals / benchmark / 签名）去对齐往届"治理 + 工程化"的评分偏好。

> 注：NVIDIA 也在美国 Austin、Seattle 等地办过 DGX Spark 卫星黑客松（偏边缘 AI / 本地推理），与国内这三届是不同系列，不作本届参考。

---

## 七、机器人方向专属建议

### 本届主题对机器人赛道的直接利好
- 第三届主题 = **"Agent Skills 驱动的 Agent 应用"**，作品方向文案里**明确列出"具身智能"**——机器人正是具身智能的主场，方向完全对口，不用硬蹭。
- 核心命题 **"从会回答走向能完成"**：机器人天生就是"完成"物理任务的载体，比纯对话 Agent 更契合这个叙事。
- 新合作伙伴 **华硕 ASUS**：本届算力节点可选 **DGX Spark 或 华硕 Ascent GX10**（往届只有 DGX Spark），机器人团队可据此做"端-边"算力分工。
- 算力支持：限量开放 DGX Spark 云节点，也可**自备** DGX Spark / 相近 NVIDIA 硬件——及早申请或确认算力。

### 对标往届：第二届季军 E-MARS 就是机器人，要借鉴更要超越
- E-MARS（树状图设计者队）用三层 Agent（InternVLA 眼前动作 / Step3‑VL 综合判断 / Step 3.7 Flash 维护目标）+ Jetson + Isaac 仿真，拿下季军。
- 你们要超越它的点：**它当时没用 Agent Skills 封装能力**（那还不是赛题）。你们应把每个机器人能力拆成可复用的 Skill，让"任意兼容 Agent 都能驱动这台机器人"——这正是第三届的题眼。

### 按评分标准逐条给机器人团队的建议

**① 实用性 / 落地 / 创新（25%）**
- 选有量化业务价值的场景：工业巡检、仓储分拣、家庭 / 养老陪护、救援、农业。避免"通用机器人"这种大而空。
- 创新点建议：把机器人**运动学 / API / 安全规程封装成一个"机器人驱动 Skill"**——自然语言指令 → Skill 翻译成机器人可执行计划，无需手写 glue code（呼应周旭"从手写 glue 到技能资产"）。
- 突出 DGX Spark **边缘 / 离线**优势：断网也能跑（救援、工厂内网），这是云端机器人做不到的差异化。

**② 智能体与模型优化技术深度（25%）**
- 多 Agent 分层（借鉴 E-MARS）：感知 Agent / 规划 Agent / 控制 Agent / 监控 Agent，每个 Agent 调用对应 Skill。
- 技能设计：导航 Skill、抓取 Skill、视觉 Grounding Skill（复用何琨的 TAO image-grounding）、语音指令 Skill；组合官方 NVIDIA skill + 自研机器人 skill。
- 触发工程：写清 **negative triggers——"什么指令绝不执行"**（危险动作、越界区域）。
- 模型优化：TensorRT / TensorRT-LLM 量化部署视觉与语言模型；StepFun 3.7 Flash 作 VLM / 规划 backbone，换端点做回归评测（周旭 P9）。
- 安全：把"前置提问 + 安全边界内嵌"（刘春晖心法）做成机器人 Skill 的硬约束——**拒绝不安全指令本身就是技术深度，也是评委加分项**。

**③ 项目完整性（20%）**
- 交付物含：机器人驱动 Skill 全套（`SKILL.md` + `scripts` + `evals` 含**安全负向用例** + `skill-card` + `BENCHMARK.md` + 签名）。
- 仿真 + 实机：用 Isaac Sim / Lab 做验证（E-MARS 同款），有实机 / Jetson 更好；文档写清"仿真 → 真机"迁移。
- 稳定 demo：机器人 live demo 风险高，预录主路径 + 现场只做可控安全环节。

**④ 平台适配性（15%）**
- 算力分工：DGX Spark GB10（或华硕 Ascent GX10）做重推理，Jetson 做机载轻量推理（端-边协同，E-MARS 路线）。
- NVIDIA 栈：Isaac（Sim / Lab / ROS）、TAO、DeepStream、CUDA‑X、TensorRT。
- StepFun 模型接入：把部分 LLM / VLM 换成 StepFun 端点。

**⑤ 演示效果（10%）**
- 3–5 分钟分镜：自然语言指令 → Agent 加载机器人 Skill → 中间产物可视化（grounding 框、规划树、签名验证 PASS）→ 机器人执行 → 结果。
- 安全桥段：演示一次"危险指令被 Skill 拒绝"，既出彩又呼应治理主题。

**⑥ 赛事征文（5%）**
- 十日谈重点写：机器人 + Skills 的认知转变、仿真到真机的坑、安全设计权衡、StepFun 模型切换。

### 一句话定位
**不要只做"一台会动的机器人"，而要做"一台能力被封装成 Agent Skills、能被任意兼容 Agent 用自然语言驱动、在 DGX Spark 上离线可靠运行、且懂得拒绝危险指令的具身智能体"。** 这正好把本届主题（Agent Skills × 具身智能）、往届机器人季军经验（E-MARS）和评分标准（治理 + 工程化 + 落地）全部吃满。

---
