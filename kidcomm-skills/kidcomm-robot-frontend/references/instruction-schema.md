# 机器人指令 Schema（编译输出契约）

`scripts/compile.py` 把槽位编译成如下 JSON，交给机器人执行端。前端"指令预览组件"应把它可视化给孩子/家长看。

```json
{
  "action": "pick_up | move_to | play | turn | stop",
  "target": {
    "type": "block | ball | person | location | toy | book | cup",
    "color": "red | blue | green | yellow | orange | purple | white | black",  // 可选
    "id": "obj_03"                                                          // 可选，grounding 后由机器人侧回填
  },
  "params": {
    "speed":   0.0–1.0,   // 可选，移动速度比例
    "duration":0–600,     // 可选，秒
    "angle":   -180–180   // 可选，度
  },
  "confirm": true         // 固定 true：必须经确认门后才下发
}
```

## 字段含义
| 字段 | 必填 | 说明 |
|------|------|------|
| `action` | 是 | 机器人可行动作，仅限清单内 |
| `target.type` | 否* | 对象类别；`stop` 可不带对象 |
| `target.color` | 否 | 颜色限定，用于消歧（同画面多同色对象时由 `id` 进一步区分） |
| `target.id` | 否 | grounding 后由机器人感知回填的可交互物体 ID |
| `params.speed/duration/angle` | 否 | 数值参数，超出范围编译失败 |
| `confirm` | 是 | 永远 `true`，提示执行端必须先获确认 |

\* `stop` 以外动作必须带 `target.type`，否则编译失败（退出码 2）。

## 示例
孩子"让机器人去拿红色积木" → 前端选完槽位 →
```json
{ "action": "pick_up", "target": {"type": "block", "color": "red"}, "params": {}, "confirm": true }
```

> **待与机器人侧对齐**：最终字段名、参数单位、动作集与执行端是否一致（见设计文档第 8 节）。
