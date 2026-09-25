# 机器人 Skill 创意清单（DGX Spark 黑客松 · 第三届）

> 机器人 Skill = 把"让机器人做某件事"的能力，写成 Agent 能读的操作手册（SKILL.md + scripts + evals + skill-card）。
> 思路：先复用 NVIDIA 官方 Skill，再在其上写"机器人专属"Skill 把它们串起来。每个 Skill 都按治理五件套写，对齐评分。

## 一、先复用官方 Skill（别从零写）
- `tao-generate-image-grounding`：看图，框出指定物体（workshop 已教）。
- `tao-generate-referring-expressions`：给框加语言描述。
- `deepstream-*`：摄像头实时检测 / 视频 pipeline。
- `vss-*`：视频检索与摘要。
- 你们的工作 = 在这些之上写机器人专属 Skill，组合成工作流。

## 二、可写的机器人 Skill（按能力分层）
| 层 | Skill 名字（举例） | 干什么 | 复用 / 技术 |
|----|----|----|----|
| 感知 | 场景理解 Skill | 图 → 文字描述（"前方有台阶和行人"） | StepFun 3.7 Flash / Qwen3.6-VL 原生多模态 |
| 感知 | 障碍物识别 Skill | 框出障碍物并分类 | TAO grounding / DeepStream |
| 导航 | 避障指令 Skill | 识别障碍 → 输出"左转/停" | 规则 + VLM |
| 导航 | 目标导航 Skill | "去门口" → 路径步骤 | LLM 规划 |
| 操作 | 抓取规划 Skill | 物体 → 抓取位姿 | Isaac 仿真验证 |
| 操作 | 语音 / 手势指令 Skill | 语音 → 机器人指令 | StepFun / ASR |
| 规划 | 任务拆解 Skill | 自然语言任务 → 步骤计划 | LLM / StepFun |
| 规划 | 机器人驱动 Skill（元技能） | 封装机器人 SDK / 运动学，任意 Agent 能用自然语言驱动它 | 你们机器人的 API |
| 安全 | 安全护栏 Skill | negative triggers 拒绝危险指令（"不要靠近楼梯 / 不要抓人"） | 规则 + 前置提问 |
| 巡检 | 异常检测 Skill | 识别设备异常 / 读表盘 / 烟火焰 | TAO + VLM |

## 三、三个能直接当作品的"组合包"
1. **园区 / 工厂巡检机器人**（最稳，对应第一届亚军）
   - 技能：场景理解 + 异常检测 + 表盘读取 + 安全护栏
   - 价值：替代高危人工巡检，有量化指标（漏检率 / 响应时间）
   - 演示：摄像头画面 → Agent 识别异常 → 报警 + 报告
2. **室内服务 / 养老陪护机器人**（演示友好，贴近生活）
   - 技能：视觉 Grounding + 语音指令 + 任务规划 + 安全护栏
   - 价值：易理解，评委一眼看懂
3. **断网救援机器人**（差异化最大，对标 E-MARS 但加 Skills）
   - 技能：三层 Agent 各调一 Skill + 离线运行 + 安全护栏
   - 价值：DGX Spark 边缘 / 离线优势，云端做不到
   - 关键超车点：用 Agent Skills 封装能力（E-MARS 当时没做，这是你们的机会）

## 四、我的建议（从哪开始）
- **必做两个**：① 机器人驱动 Skill（元技能，本届题眼）② 安全护栏 Skill（差异化 + 评委加分）。
- **感知核心**：把 workshop 的官方 TAO grounding 改造成"机器人视觉感知 Skill"（直接复用模式）。
- 先用仿真（Isaac）或简单机器人验证，不必一开始就有真机。
- 每个 Skill 都按治理五件套写（skill-card / evals 含负向用例 / benchmark / 签名）。

## 五、下一步
我可以帮你把"机器人驱动 Skill + 安全护栏 Skill"的骨架直接搭出来（按本届规范写好 SKILL.md 模板），你们往里填场景和机器人 API 即可。
