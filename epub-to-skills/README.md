# epub-to-skills —— 把 EPUB 蒸馏成可执行 skill 的流水线

把「拿到一本 EPUB → 产出一组可安装、经压力测试验证的 agent skill」做成**确定性、可复用**的流程。在 [cangjie-skill](https://github.com/) 蒸馏引擎之上，补齐两块工程能力：「可靠的 EPUB 文本提取」与「自动化跨 skill 混淆压力测试」，并固化中文书名 / Windows 路径 / 沙箱隔离等坑位的规避方法。

> 本 skill 不重复 cangjie-skill 的蒸馏方法论，只做它工程层面缺的两块，并把踩过的坑固化下来。

## 与 cangjie-skill 的关系

- **cangjie-skill**：蒸馏引擎（RIA-TV++：理解 / 提取 / 验证 / 构造 / 链接 / 交付）。
- **本 skill**：① 可靠的 EPUB→文本摄取；② 阶段 4 的**确定性**跨 skill 盲测路由（替代「靠 sub-agent 盲测」的不稳定做法）；③ 串联整条流水线 + 安装；④ 组装「一本书 = 一个 skill」的书级 bundle。

## 目录结构

```
epub-to-skills/
├── SKILL.md                       # 流水线总入口
├── references/workflow.md         # 完整编排细节 + 各脚本参数 + 测试报告模板
└── scripts/
    ├── extract_epub.py            # EPUB → 纯文本（spine 感知 + 中文路径安全）
    ├── blind_routing_test.py      # 确定性跨 skill 盲测路由（压力测试）
    ├── route.py                   # 通用书级路由引擎（确定性、可测试）
    └── make_book_skill.py         # 把平铺原子 skill 组装成书级 skill bundle
```

## 安装

把 `epub-to-skills/` 放到你的 agent 加载 skills 的位置（如 `~/.skills/epub-to-skills/` 或 `<repo>/skills/epub-to-skills/`）。

## 快速开始

### 阶段 A — EPUB 摄取

```bash
python scripts/extract_epub.py \
  --epub "D:/Downloads/被讨厌的勇气.epub" \
  --out "./books/bei-taoyan-de-yongqi" \
  --slug bei-taoyan-de-yongqi
```

输出 `./books/bei-taoyan-de-yongqi/_book_text.txt`（章节以 `=== <relpath> ===` 分隔），并打印章节数 / 总字数。

### 阶段 B — 蒸馏核心

把 `_book_text.txt` 交给 cangjie-skill，按其 RIA-TV++ 跑阶段 0–3（整书理解 → 提取器 → 三重验证 → RIA++ 构造 → 链接）。本 skill 不覆盖这部分。

### 阶段 C — 自动化压力测试

```bash
python scripts/blind_routing_test.py --skills-dir "./books/bei-taoyan-de-yongqi" --min-pass 0.8
```

脚本对每条 prompt 与全部 skill 的 `trigger` 签名对撞（触发短语精确命中 + 中文 bigram 重叠打分），输出每个用例的胜出 skill 与 PASS / FAIL。未过则补强 `trigger` 短语或 `description`，复跑直到全绿。

### 阶段 D / E — 交付与组装书级 skill

```bash
python scripts/make_book_skill.py \
  --skills-dir "./books/bei-taoyan-de-yongqi" \
  --book-slug "bei-taoyan-de-yongqi" \
  --book-title "被讨厌的勇气" \
  --out-root "~/.skills"
```

组装器会：
- 为每个原子 skill 的 frontmatter 加 `parent_skill` + `type: sub-skill`，移入 `<book-slug>/subskills/<slug>/`；
- 复制通用路由引擎 `scripts/route.py`；
- 生成书级 `SKILL.md`（总入口 + 路由规则 + 危机护栏）；
- 自动抽样生成 `<book-slug>/test-prompts.json` 并写空 `combos.json`；
- 立即跑 `route.py --self-test` 核对路由回归（应 100% 通过）。

## 质量红线

- 每个 skill 必须过三重验证 + 完整 `R / I / A1 / A2 / E / B`；
- 盲测路由通过率 **≥ 0.8**（`should_not_trigger` 0 容忍）；
- `test-prompts.json` 必须含兄弟 skill 混淆诱饵；
- 安装后才算交付完成。

## 工程注意（必读）

- **中文 / 沙箱路径**：在部分隔离运行环境（沙箱）下，Python 写入含中文字符的路径时，列举与读取可能读不到。规避：工作目录与产物一律用 **ASCII slug**（如 `books/bei-taoyan-de-yongqi`）。
- **Windows 路径**：用 `glob.glob('*.epub')` 定位或全程传绝对路径；脚本内部用 `pathlib` 处理，避免反斜杠混乱。
- **EPUB 章节顺序**：优先按 OPF `spine`；失败回退文件名自然排序；避免按 zip 内默认顺序（常乱序）。
- **Python 环境**：脚本仅依赖标准库（`zipfile` / `html.parser` / `xml.etree`），用任意 Python 3 运行即可，无需安装依赖。

## 依赖

仅 Python 3 标准库。

## 许可证

MIT
