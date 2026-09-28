---
name: kidcomm-robot-designer
description: >
  Use when a child (ages 5–10) wants to design and personalize their companion robot's
  appearance (face/body) and personality from scratch — via drawing or natural language —
  and you must turn that irregular input into a concrete, machine-actionable build spec the
  tech team can execute (or directly integrate as code). The skill runs a hybrid pipeline:
  a drawing panel lets the child sketch freely (then an image model renders a real robot);
  an agent guides children who describe in words from abstract wishes ("cute", "cool") to
  concrete attributes (shape/color/size/parts); a required attribute catalog enforces the
  minimum外形特征 needed to finish "捏脸"; then personality is chosen from a multiple-choice
  menu mapped via corpus to expressions/actions/tone; finally everything compiles to a design
  spec JSON (appearance + personality + build_hint + image prompt + code stub). Trigger when a
  child says or taps "我想造一个机器人", "帮我画一个会飞的小恐龙", "我想要可爱的", or any
  "design my robot" intent.
  Not for: adult CAD/3D-modeling or engineering tools, generating non-robot content, clinical
  or diagnostic scenarios, or anything unrelated to robot appearance/personality design.
---

# 儿童机器人设计 Skill（捏脸 / 捏性格 → 可交付设计稿）

## Overview
把 5–10 岁儿童的**天马行空**表达（一张草图，或一个抽象词"可爱的"）转成技术组能直接用的机器人设计规格。两大阶段：**捏脸/身体**（外形必填目录）+ **捏性格**（语料映射）。整条链路离线可跑（图像生成在真实部署接本地 ComfyUI/SD/FLUX）。

## When to use
- 孩子想"造一个自己的小机器人"，从 0 开始、天马行空（会飞的恐龙等）
- 孩子用画 / 用话描述外形，需要先把抽象词变成具体属性
- 需要把"不规则自然语言"变成可执行的规格甚至代码，交给技术组

## Workflow（按序）
1. **护栏前置**：对孩子输入跑 `kidcomm-safety-guardrail`（`--mode input`），`block` 立即终止。
2. **选路径**：画画（草图 → 成像提示词送图像模型）或 文字描述。
3. **收集外形（必填目录）**：`shape`（形状）/ `color_primary`（颜色）/ `size`（大小）为**必填**，`parts`（特征部件）可选。文字路径用 `scripts/design.py --mode guide` 把抽象词映射成具体属性并追问缺的项。
4. **选性格**（选择题）：从 `references/personality-corpus.md` 的 6 类里选，经语料映射成表情/动作/语气。
5. **编译**：`python scripts/design.py --mode compile --spec '{...}'` → 设计规格 JSON（含 `build_hint`、`image_prompt`、`code_stub`）。

## Output schema（设计规格，见 references/design-contract.md）
```json
{
  "design": {
    "appearance": { "shape": "dinosaur", "color_primary": "green", "size": "medium", "parts": ["wings","tail"] },
    "personality": { "type": "brave", "expression": "坚定眼神 + 微笑", "actions": ["大步前进","张开双臂","保护姿态"], "tone": "稳" },
    "source": "drawing | text"
  },
  "build_hint": "技术组请按此外形与性格建模/编程。",
  "image_prompt": "a medium green dinosaur robot, with wings, tail, brave expression ...",
  "code_stub": "new RobotDesign({...})"
}
```

## Reuse（复用既有 kidcomm 资产）
- `kidcomm-safety-guardrail`：步骤 1 强制复用，确定性离线。
- 抽象→具体 语料、性格语料：见 `references/`。
- 端点解耦 `KIDCOMM_*`（图像模型/LLM 本地端点）：开发期任意 OpenAI 兼容，DGX 期本地大模型，代码零改。

## Boundaries（评审必查）
- 外形必填项未齐不得"完成捏脸"。
- 意图仅限机器人外观/性格设计；超范围引导回正题或拒绝。
- 绝不绕过护栏；全程本地、禁云上传。
