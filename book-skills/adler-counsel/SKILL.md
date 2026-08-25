---
name: adler-counsel
version: 2.0.0
description: |
  一本书 = 一个 skill。本 skill 是《被讨厌的勇气》(岸见一郎/古贺史健) 的蒸馏总入口，内部含 12 个原子"子 skill"（目的论/课题分离/被讨厌的勇气/横向关系/自我接纳/他者信赖/幸福即贡献感/共同体感觉/活在当下/人生谎言/自卑情结/甘于平凡），用户无需在 12 个概念里挑选——本 skill 通过 scripts/route.py 自动路由到正确的子 skill（或组合）。当用户在自我价值、人际关系、人生意义、情绪归因、当下/未来焦虑等议题上表达困扰、痛苦、内耗或迷茫时自动激活，按子 skill 的 R/I/A1/A2/E/B 给出回应。不替代专业心理咨询。
source_book: 《被讨厌的勇气》岸见一郎；古贺史健
type: book-skill
---

# adler-counsel — 《被讨厌的勇气》一本书·一个 skill

## 核心原则（回应"12 个 skill 怎么选"的痛点）
- **一本书 = 一个 skill**。本目录 `adler-counsel/` 就是唯一入口，对外只暴露这一个 skill。
- **12 个原子概念 = 子 skill（sub-skills）**，全部嵌套在 `subskills/` 下，**不作为独立 skill 注册/暴露**。用户和上游只需要调用 `adler-counsel`，由内部路由决定哪个子 skill 生效。
- **自动路由，不让人选**。用户抛一个问题，本 skill 跑 `scripts/route.py` 得出 `{primary, secondary?, crisis?}`，直接加载对应子 skill 执行，使用者零决策成本。

## 目录结构
```
adler-counsel/
├── SKILL.md                 # 本文件（书级总入口 + 路由规则）
├── scripts/route.py        # 确定性路由引擎（可测试/可演化）
├── test-prompts.json       # 路由层回归测试（由 route.py --self-test 执行）
└── subskills/              # 12 个原子子 skill（非独立 skill）
    ├── teleology/SKILL.md (+test-prompts.json +test-results.md)
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

## 何时激活
用户出现以下任一信号即激活（判断核心：是否处于阿德勒框架内的"烦恼/内耗/逃避课题"）：
- 关系内耗（亲子/伴侣/上下级/朋友）："他不听我的""我都是为你好""凭什么管我"
- 自我攻击/价值焦虑："我太差了""没价值""活着没意义"
- 怕被否定/讨好："怕他生气""怕被说闲话""寻求认可"
- 归因过去/创伤决定论："都是小时候...""过去决定一切""我有创伤所以"
- 当下/未来焦虑："等以后...""如果当初...""焦虑未来"
- 自卑/优越/平凡焦虑："我不如别人""必须出人头地""不想平庸"

若用户只是查书的内容/作者/金句，或做纯事实查询，**不激活**。

## 路由流程（严格执行，无需人工挑选）
1. **跑路由引擎**：用 Python 3 执行
   `python scripts/route.py --question "<用户原话>" --json`
   得到 `{"crisis":bool, "primary":slug, "secondary":slug|null, "combo":bool}`。
   - 若 `crisis=true` → 跳转第 5 步（护栏），不加载任何子 skill。
2. **加载主子 skill**：`Read subskills/<primary>/SKILL.md`，按其 `R / I / A1 / A2 / E / B` 段组织回应。
3. **若为组合（combo=true）**：再 `Read subskills/<secondary>/SKILL.md`，将两个子 skill 的方法论融合（顺序：先归因/边界，再行动/勇气），不要只给一个。
4. **回退**：若某子 skill 的 `Read` 失败，直接在对话中按其 SKILL.md 内容（已注入上下文时）执行；本目录即唯一数据源，不会丢失。
5. **护栏（硬性）**：检测到真实危机（自伤/伤人计划、急性精神症状、明确受虐待、需医学/法律诊断）→ 不调用任何子 skill，明确建议寻求专业帮助（心理热线/医院/律师），并说明本 skill 不替代专业服务。

## 12 子 skill 速查（仅供内部路由参考，用户不必记）
| 主轴 | 子 skill | 关键触发词 |
|---|---|---|
| 归因过去/创伤决定论 | teleology | 控制不住自己、都是小时候、过去决定一切、原生家庭、创伤所以 |
| 人际边界/越界干预 | separation-of-tasks | 他不听我的、我都是为你好、凭什么管我、这是为你好 |
| 怕被否定/讨好/求认可 | courage-to-be-disliked | 怕他生气、怕被说闲话、不敢表达、寻求认可、怕得罪人 |
| 评价/纵向关系 | horizontal-relations | 鼓励孩子、表扬批评、我比你强、立威、你怎么这么笨 |
| 自我攻击/自我接纳 | self-acceptance | 我太差了、接受不了自己、必须变强、自我怀疑 |
| 不敢信任他人 | trust-others | 不敢信他、怕被出卖、被坑了不信人 |
| 价值/人生意义/幸福 | contribution-happiness | 没价值、活着没意义、人生意义、对别人没用 |
| 归属/孤独/世界中心 | community-feeling | 没归属、别人是竞争者、融不进去、孤独 |
| 过去/未来焦虑/拖延 | live-in-the-now | 等以后、如果当初、焦虑未来、总说以后 |
| 借口/人生谎言 | life-lies | 要不是因为、我有XX所以没法、都是原生家庭害的、给自己找借口 |
| 自卑/自负/优越情结 | inferiority-triad | 我不如别人、因为学历低所以、他好自负、优越感 |
| 必须特别/平凡焦虑 | courage-to-be-ordinary | 不想平庸、必须出人头地、不能平庸、拒绝普通 |

## 组合模式（已知 7 类，由 route.py 自动识别）
- 原生家庭创伤+不敢表达 → `teleology` + `courage-to-be-disliked`
- 孩子不听还反抗 → `separation-of-tasks` + `horizontal-relations`
- 不如人又怕被讨厌 → `inferiority-triad` + `courage-to-be-disliked`
- 找不到意义又觉没用 → `contribution-happiness` + `community-feeling`
- 总说等以后+找借口 → `live-in-the-now` + `life-lies`
- 原生家庭害的改不了 → `teleology` + `life-lies`
- 接受不了自己又必须出头 → `self-acceptance` + `courage-to-be-ordinary`

## 演化链路（可回归、可生长）
本 skill 的路由是**确定性且可测试的**，这是它优于"凭感觉选 skill"的关键：
- **路由回归**：`python scripts/route.py --self-test` 读取 `test-prompts.json`（20 条样本问题→预期子 skill），当前 **100% 通过**。新增混淆场景时，往 `test-prompts.json` 加用例即可自动暴露漂移。
- **子 skill 演化**：每个 `subskills/<slug>/test-prompts.json` 为统一测试格式（should_trigger/should_not_trigger/edge_case）。若某子 skill 误触发或漏触发，补用例后重跑即可回炉。
- **加新组合**：在 `scripts/route.py` 的 `COMBO_PAIRS` 增加一对（frozenset），并在 `test-prompts.json` 补一条样本，重跑 `--self-test` 验证。
- **加新书**：复制本目录为 `<new-book-skill>/`，替换 `subskills/` 内容并重写路由表/组合对，即可复用同一套确定性路由框架。

## 与生态关系
- `cangjie-skill` 负责把书蒸馏成原子 skill（阶段 0–3/5）；本 skill 是蒸馏产物的**聚合与路由层**。
- `epub-to-skills` 负责 EPUB 摄取与跨 skill 盲测；本 skill 复用其思路做确定性路由。
- 不重复任何子 skill 的方法论，只做"识别→加载→融合"。
