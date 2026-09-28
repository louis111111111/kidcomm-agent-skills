# 设计规格输出契约（Design Spec Contract）

`scripts/design.py --mode compile` 产出的 JSON，是**技术组可直接执行甚至直接接入代码**的交付物。

```json
{
  "design": {
    "appearance": {
      "shape": "dinosaur", "color_primary": "green", "size": "medium",
      "parts": ["wings", "tail"]            // 可选
    },
    "personality": {
      "type": "brave",
      "expression": "坚定眼神 + 微笑",
      "actions": ["大步前进", "张开双臂", "保护姿态"],
      "tone": "稳"
    },
    "source": "drawing | text"
  },
  "build_hint": "技术组请按此外形(...)与性格(brave)建模/编程。",
  "image_prompt": "a medium green dinosaur robot, with wings, tail, brave expression ...",
  "code_stub": "const robot = new RobotDesign({...}); robot.mount(scene);",
  "generated_by": "kidcomm-robot-designer v1"
}
```

## 字段说明
| 字段 | 用途 |
|------|------|
| `design.appearance` | 建模/3D 所需的最小外形描述 |
| `design.personality` | 表情/动作/语气，驱动机器人行为 |
| `build_hint` | 给技术组的一句话自然语言说明 |
| `image_prompt` | 送图像模型（ComfyUI/SD/FLUX）生成正式机器人图的提示词；**画画路径的"成像"也走这里** |
| `code_stub` | 可直接粘贴的初始配置代码（伪 three.js / RobotDesign） |

## 为什么直接给代码
用户原话："把不规则自然语言变成可以发给技术组执行的具体指令**甚至直接可接入的代码**"。因此输出同时给：结构化 JSON（机器读）+ 代码 stub（程序员贴）+ 提示词（图像生成）+ 自然语言 hint（人读）。四件套覆盖技术组全部接入方式。

## 校验规则
- `appearance` 必填三件套（shape/color_primary/size）缺一 → 编译失败。
- `personality.type` 必须在六类之内，否则编译失败。
- 由 `compile_design()` 强制，前端与脚本双重校验。
