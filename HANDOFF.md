# 给组长的交接说明 · kidcomm Agent Skills

## 这是什么
面向「家长 ↔ 5–10 岁孩子」沟通壁垒的 Agent Skill 套装（第三届 NVIDIA DGX Spark 黑客松）。家长把"孩子难懂的问题"输入手机，机器人用学术验证方法（讲故事 / 角色扮演 / 分步提问 / 画图）经**语音 + 屏幕画面**引导孩子表达，再回传经**成员核查**的家长摘要。数据全程本地，不上云。

## 取代码
```
git clone https://github.com/louis111111111/kidcomm-agent-skills
```
运行时只用 `kidcomm-skills/` 子目录（两个 Skill + `requirements.txt`）。根目录其余 `.md` 是给评委看的，不用。

## 在 DGX Spark 上跑（4 步）
1. 装依赖：`pip install -r kidcomm-skills/requirements.txt`
2. 设本地模型端点（唯一 DGX 专属步骤，代码无需改）：
   ```
   export KIDCOMM_BASE_URL="http://localhost:端口/v1"
   export KIDCOMM_MODEL="本地模型名"
   export KIDCOMM_API_KEY=""   # 本地可留空
   ```
3. 把 `kidcomm-safety-guardrail/` 和 `kidcomm-elicit/` 丢进 Agent 的 skills 目录（自动识别 `SKILL.md`）。
4. 跑。

## 怎么触发
家长输入"问问孩子为什么… / 帮我理解孩子怎么想…" → Agent 自动调 `kidcomm-elicit` → **先过护栏** → `plan` 出引导脚本 → 语音+屏幕给孩子 → 孩子回答 → `summarize` 回传家长摘要（带 member-check 让孩子确认）。

## 评委要看的验证
- 护栏离线评测（无需模型）：`cd kidcomm-skills/kidcomm-safety-guardrail && python evals/run_eval.py` → **5/5 通过**
- 模型自对弈（需端点）：`cd kidcomm-skills && python validate.py` → 产出 `validation_report.json`
- elicit 评测：`cd kidcomm-skills/kidcomm-elicit && python evals/run_eval.py`（接模型后出分，无端点自动跳过）

## 边界
- 护栏是**强制前置闸门**，未过不得继续。
- 不替孩子下结论、不诊断、不说教、不给"标准答案"暗示。
- 本地处理，禁止云上传。
