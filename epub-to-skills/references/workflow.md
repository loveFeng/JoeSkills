# epub-to-skills 完整工作流参考

本文件是 `SKILL.md` 的展开，给出可直接照抄的命令、参数与模板。

## 0. 前置

- Python 3（标准库即可，无需安装依赖，避免污染用户环境）：
  `python3`
- 工作目录用 **ASCII slug**，例如：`./books/<ascii-slug>/`
- 不要在工作目录路径里放中文，否则 Python 写出的文件 Git Bash `ls` / Read 可能读不到。

## 1. 阶段 A — EPUB 提取

```bash
PY="python3"
$PY scripts/extract_epub.py \
  --epub "D:/Downloads/被讨厌的勇气_【日】岸见一郎；古贺史健.epub" \
  --out "./books/bei-taoyan-de-yongqi" \
  --slug bei-taoyan-de-yongqi
```

输出：`./books/bei-taoyan-de-yongqi/_book_text.txt`（章节以 `=== <relpath> ===` 分隔）。

**验证**：直接打开读取 `_book_text.txt` 确认可读（这一步能直接暴露中文路径问题）。

## 2. 阶段 B — 蒸馏（委托 cangjie-skill）

把 `_book_text.txt` 交给 cangjie-skill，严格按其 RIA-TV++ 跑：

- 阶段 0 `BOOK_OVERVIEW.md`
- 阶段 1 5 个 extractor 候选池
- 阶段 1.5 三重验证 → `verified.md`
- 阶段 2 RIA++ 构造每个 `SKILL.md`（R/I/A1/A2/E/B）
- 阶段 3 `INDEX.md` + `GLOSSARY.md` + 回填 related_skills

阶段 2 结束后，每个 skill 目录结构应为：

```
<slug>/<skill-slug>/
├── SKILL.md              # 含 frontmatter: name/description/trigger/source_chapter/related_skills
├── test-prompts.json     # 阶段 4 输入
└── test-results.md       # 阶段 4 输出
```

## 3. 阶段 C — 自动化压力测试

### 3.1 写 test-prompts.json（每个 skill 一份）

统一测试格式，字段：`minimum_pass_rate` + `test_cases[]`（每条含 `id` / `type` / `prompt` / `expected_behavior` / `notes`）。

`type` 取值：
- `should_trigger`（≥3）：应激活本 skill 的真实场景。
- `should_not_trigger`（≥2）：**0 容忍**；其中至少 1 条是"应触发同书另一个 skill"的兄弟混淆诱饵（notes 注明"兄弟 skill 混淆诱饵"）。
- `edge_case`（≥1）：边界模糊但本 skill 应守住护栏的场景。

触发短语要写进 SKILL.md frontmatter 的 `trigger: "短语1""短语2"...`，盲测路由会精确匹配这些短语。

### 3.2 跑盲测

```bash
$PY scripts/blind_routing_test.py \
  --skills-dir "./books/bei-taoyan-de-yongqi" \
  --min-pass 0.8
```

脚本对每条 prompt 与全部 skill 打分（触发短语 +3，中文 bigram 重叠弱信号），输出胜出 skill 与 PASS/FAIL。

### 3.3 回炉规则

| 现象 | 处置 |
|---|---|
| should_trigger 被判给兄弟 | 补强本 skill `trigger` 短语 / `description` 的区分词 |
| should_not_trigger 误激活本 skill | 重写诱饵，去掉与其"不适用"负例重叠的表面词（如制度/法律/绩效） |
| should_trigger 得分 0（无 skill 胜出） | prompt 缺少触发词，或 skill 签名太弱，补 `trigger` |

改完复跑直到 `RESULT: PASS`，通过率需 ≥ 0.8。

### 3.4 写 test-results.md（模板）

```markdown
# <skill-slug> — 压力测试报告

- 测试框架: 跨 skill 盲测路由（中文 bigram + 触发短语加权）
- 用例总数: N = a should_trigger / b should_not_trigger / c edge_case
- 自动路由通过率: 100%（≥ minimum_pass_rate 0.8）
- 兄弟 skill 混淆诱饵: <id 列表>
- 结论: **PASS**

## 用例明细
| id | 类型 | prompt | 实际胜出(skill) | 判定 |
|---|---|---|---|---|
| ... | ... | ... | ... | PASS |

## 备注
- should_not_trigger 0 容忍；edge_case 需人工结合预期行为复核。
- 跨 skill 混淆：每条 prompt 与全部 skill 的 trigger 签名打分，确认最优归属。
```

## 4. 阶段 D — 交付

```bash
$PY - <<'PY'
import shutil, os
src_base = "./books/bei-taoyan-de-yongqi"
dst_base = os.path.expanduser("~/.skills")
skills = [d for d in os.listdir(src_base)
          if os.path.isdir(os.path.join(src_base,d))
          and os.path.exists(os.path.join(src_base,d,"SKILL.md"))]
for s in skills:
    src = os.path.join(src_base, s)
    dst = os.path.join(dst_base, s)
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print("安装:", s)
PY
```

安装后更新各 `SKILL.md` 审计信息"测试通过率"。产出 skill 已采用统一测试格式，可直接接入回归测试与自动演化流程。

## 6. 阶段 E — 组装书级 skill（adler-counsel 风格）

让“一本书 = 一个 skill”，原子概念作为嵌套子 skill，用户不必在 N 个概念间手动挑。

```bash
PY="python3"
$PY scripts/make_book_skill.py   --skills-dir "./books/<ascii-slug>"   --book-slug "<ascii-book-slug>"   --book-title "<书名>"   --out-root "$($PY -c 'import os;print(os.path.expanduser("~/.skills"))')"
```

组装器产物：

```
<book-slug>/
├── SKILL.md            # 书级总入口（路由说明 + 危机护栏）
├── scripts/route.py    # 通用确定性路由引擎
├── combos.json         # 组合对配置（默认空）
├── test-prompts.json   # 路由回归锚点（自动抽样）
└── subskills/<slug>/   # 原子概念 = 子 skill（含 parent_skill/type 标记）
```

**路由回归**：组装完立即 `python scripts/route.py --self-test`，应 100% 通过（子 skill 的自身 `should_trigger` 样本天然命中其 trigger 短语）。

**演化**：
- 误路由 → 在 `test-prompts.json` 补样例（`expected:[slug]` 或 `crisis:true`）→ 重跑 `--self-test` 回炉；
- 组合概念 → 在 `combos.json` 写 `[["slugA","slugB"], ...]`；
- 子 skill 各自 `test-prompts.json` 仍是其回归测试集。

## 5. 断点续跑

`books/<slug>/PIPELINE_STATE.md` 记录当前阶段 + 各 skill 状态。中断后先读它再从记录的阶段续跑，不要从头重来。
