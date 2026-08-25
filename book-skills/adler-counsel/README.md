# adler-counsel —— 《被讨厌的勇气》· 一本书一个 skill

把《被讨厌的勇气》（岸见一郎 / 古贺史健）蒸馏为一个 agent skill。核心思想：**一本书 = 一个 skill**；书里的 12 个原子概念（目的论 / 课题分离 / 被讨厌的勇气 / 横向关系 / 自我接纳 / 他者信赖 / 幸福即贡献感 / 共同体感觉 / 活在当下 / 人生谎言 / 自卑情结 / 甘于平凡）作为**嵌套子 skill**，由确定性路由引擎自动挑选，使用者无需在多个概念间手动选择。

## 它能做什么

当用户在自我价值、人际关系、人生意义、情绪归因、当下 / 未来焦虑等议题上表达困扰、痛苦、内耗或迷茫时自动激活，按对应子 skill 的 `R / I / A1 / A2 / E / B` 段组织回应。

> ⚠️ 本 skill 不替代专业心理咨询。检测到真实危机（自伤 / 伤人计划、急性精神症状、明确受虐待、需医学 / 法律诊断）时，不路由任何子 skill，明确建议寻求专业帮助。

## 目录结构

```
adler-counsel/
├── SKILL.md                 # 书级总入口 + 路由规则 + 危机护栏
├── scripts/route.py         # 确定性路由引擎（可测试 / 可演化）
├── test-prompts.json        # 路由层回归测试（由 route.py --self-test 执行）
└── subskills/               # 12 个原子子 skill（非独立 skill）
    ├── teleology/SKILL.md (+ test-prompts.json + test-results.md)
    ├── separation-of-tasks/SKILL.md
    ├── courage-to-be-disliked/SKILL.md
    ├── horizontal-relations/SKILL.md
    ├── self-acceptance/SKILL.md
    ├── trust-others/SKILL.md
    ├── contribution-happiness/SKILL.md
    ├── community-feeling/SKILL.md
    ├── live-in-the-now/SKILL.md
    ├── life-lies/SKILL.md
    ├── inferiority-triad/SKILL.md
    └── courage-to-be-ordinary/SKILL.md
```

## 安装

把整个 `adler-counsel/` 目录放到你的 agent 加载 skills 的位置，例如：

- 用户级：`~/.skills/adler-counsel/`
- 项目级：`<repo>/skills/adler-counsel/`

> 安装目录名由你的 agent 决定；`~/.skills` 仅是通用占位示例，请指向你实际使用的 skills 根目录。

## 使用

对话中出现关系内耗、自我攻击、怕被否定、归因过去、当下 / 未来焦虑、自卑 / 平凡焦虑等信号即触发。内部执行：

```bash
python scripts/route.py --question "孩子不听我的还顶嘴" --json
```

返回：

```json
{ "crisis": false, "primary": "separation-of-tasks", "secondary": "horizontal-relations", "combo": true, "scores": { "...": 0 } }
```

- `crisis: true` → 不路由任何子 skill，直接转专业帮助。
- 否则读取 `subskills/<primary>/SKILL.md`，按其 `R / I / A1 / A2 / E / B` 段回应；
- `combo: true` 时再融合 `secondary` 子 skill 的视角。

## 路由引擎

`scripts/route.py` 是**确定性、可测试、可演化**的路由：

- **触发短语精确命中**（强信号，加权）+ **中文 bigram 重叠**（弱信号）打分；
- 已知 7 类组合（如「原生家庭创伤 + 不敢表达」→ `teleology` + `courage-to-be-disliked`）；
- 运行回归测试：

```bash
python scripts/route.py --self-test
# == 路由自测 (20 用例, 阈值 0.9) ==  → 通过率 100%
```

## 演化

- 误路由 → 在 `test-prompts.json` 补样例（`expected:[slug]` 或 `crisis:true`）→ 重跑 `--self-test` 回炉；
- 子 skill 各自 `test-prompts.json` 是其回归测试集，误触发 / 漏触发时补用例即可暴露。

## 依赖

仅 Python 3 标准库，无需安装任何第三方包。

## 许可证

MIT
