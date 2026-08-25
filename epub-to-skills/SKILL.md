---
name: epub-to-skills
version: 1.0.0
description: 把一本 EPUB 电子书蒸馏成一组可执行 agent skill 的一站式流水线封装。在 cangjie-skill 蒸馏引擎之上，补齐「可靠的 EPUB 文本提取」与「自动化跨 skill 混淆压力测试」两块工程能力，并固化中文书名 / Windows 路径 / 沙箱隔离等坑位的规避方法。 当用户给出 EPUB 路径并要求「拆书 / 把 XX 书做成 skill / 蒸馏成 skill」时使用；也适用于任何需要把长文本稳定导入 cangjie-skill 的场景。
---

# epub-to-skills — EPUB 一键蒸馏为可执行 skill 的流水线封装

## 使命

把"拿到一本 EPUB → 产出一组可安装、可调用、经压力测试验证的 agent skill"做成**确定性、可复用**的流程。本 skill **不重复** cangjie-skill 的 RIA-TV++ 蒸馏方法论，而是补齐它在工程层面缺的两块，并把踩过的坑固化下来。

## 与 cangjie-skill 的关系

- **cangjie-skill** 是蒸馏引擎（RIA-TV++：阶段 0–3 理解 / 提取 / 验证 / 构造 / 链接，阶段 5 交付）。
- **本 skill** 负责：① 可靠的 EPUB→文本摄取（含中文路径规避）；② 阶段 4 的**确定性**跨 skill 盲测路由（替代"靠 sub-agent 盲测"的不稳定做法）；③ 串联整条流水线 + 安装。
- 调用顺序：用 `scripts/extract_epub.py` 拿到纯文本 → 交给 cangjie-skill 跑阶段 0–3 与阶段 5 → 在阶段 4 用 `scripts/blind_routing_test.py` 做自动化混淆回归。

## 何时调用

- 用户给出 EPUB 路径并要求"拆书 / 蒸馏 / 把 XX 书做成 skill"。
- 已知长文本（EPUB / 已提取的 txt），想稳定灌入 cangjie-skill 而不被路径 / 编码坑绊住。

## 输入

1. EPUB 绝对路径（可含中文）。
2. 书名 + 作者 + 出版年（用于目录 slug 与审计；**slug 必须 ASCII**）。
3. 安装位置（用户级 `~/.skills/` 或项目级 `<repo>/skills/`）。

## 执行流程

### 阶段 A — EPUB 摄取（本 skill 提供）

1. 用 `scripts/extract_epub.py` 提取：

   ```bash
   python scripts/extract_epub.py \
     --epub "<EPUB路径>" \
     --out "<ASCII工作目录>" \
     --slug "<ascii-slug>"
   ```

2. 脚本输出 `out/_book_text.txt`（含 `=== <relpath> ===` 章节分隔）并打印章节数 / 总字数。
3. **验证可读性**：直接打开读取 `_book_text.txt` 确认（见"工程坑"）。
4. 把纯文本喂给 cangjie-skill，从阶段 0 续跑。

### 阶段 B — 蒸馏核心（委托 cangjie-skill）

严格按 cangjie-skill 的 RIA-TV++ 跑阶段 0–3（整书理解 → 5 提取器 → 三重验证 → RIA++ 构造 → Zettelkasten 链接）。本 skill 不覆盖这部分内容。

### 阶段 C — 自动化压力测试（本 skill 提供，替代 sub-agent 盲测）

1. 每个 skill 目录需含 `test-prompts.json`（统一测试格式：≥3 should_trigger + ≥2 should_not_trigger[含≥1 兄弟混淆诱饵] + ≥1 edge_case）。
2. 运行确定性盲测路由：

   ```bash
   python scripts/blind_routing_test.py --skills-dir "<工作目录>" --min-pass 0.8
   ```

3. 脚本对所有 skill 的 `trigger` 签名做"触发短语精确命中 + 中文 bigram 重叠"打分，把每条 prompt 与全部 skill 对撞，输出每个用例的胜出 skill 与 PASS/FAIL。
4. **未过则回炉**：should_trigger 被判给别人 → 补强该 skill 的 `trigger` 短语或 `description`；should_not_trigger 误激活 → 重写诱饵，去除与"不适用"负例的表面词重叠。改完复跑直到全绿。
5. 每个 skill 生成 `test-results.md`（模板见 `references/workflow.md`）。

### 阶段 D — 交付（cangjie-skill 阶段 5 + 安装）

1. 生成 `DIGEST.md` 精华长文（cangjie-skill 阶段 5）。
2. 询问用户安装位置，把通过测试的 skill 复制过去（覆盖同名则先删后拷）：

   ```python
   import shutil, os
   dst = os.path.expanduser("~/.skills")
   for s in skills:
       src = os.path.join(work_dir, s)
       target = os.path.join(dst, s)
       if os.path.exists(target):
           shutil.rmtree(target)
       shutil.copytree(src, target)
   ```

3. 更新各 SKILL.md 审计信息"测试通过率"。

### 阶段 E — 组装书级 skill（adler-counsel 风格）

> 目标：**一本书 = 一个 skill**，原子概念作为内部子 skill 嵌套，用户/上游只调书级 skill，由确定性路由引擎挑子 skill。彻底消除“N 个 skill 该用哪个”的挑选成本。

1. 前置：阶段 C 已让每个原子 skill 通过盲测，且每个目录含 `SKILL.md` + `test-prompts.json`。
2. 运行组装器（把平铺的 N 个 skill 收进书级 bundle）：

   ```bash
   python scripts/make_book_skill.py      --skills-dir "<工作目录(含原子 skill 子目录)>"      --book-slug "<ascii-book-slug>"      --book-title "<书名>"      --out-root "$(python -c 'import os;print(os.path.expanduser("~/.skills"))')"
   ```

3. 组装器会：
   - 为每个原子 skill 的 frontmatter 加 `parent_skill: <book-slug>` + `type: sub-skill`，移入 `<book-slug>/subskills/<slug>/`；
   - 复制通用路由引擎 `scripts/route.py` 到 `<book-slug>/scripts/route.py`；
   - 生成 `<book-slug>/SKILL.md`（书级总入口 + 路由规则 + 危机护栏）；
   - 自动从各子 skill 的 `should_trigger` 抽样生成 `<book-slug>/test-prompts.json`，并写空 `combos.json`；
   - 立即跑 `route.py --self-test` 核对路由回归（应 100% 通过）。
4. 组装完成后安装：把整个 `<book-slug>/` 目录复制到目标 skills 目录（用户级或项目级）。
5. **演化链路**：
   - 书级 `test-prompts.json` 是路由回归锚点——新对话暴露误路由 → 补样例 → 重跑 `--self-test` 即回炉；
   - 组合模式：编辑 `<book-slug>/combos.json`（一对 slug 数组）声明“两概念同时出现”的组合，路由自动识别；
   - 新书蒸馏完直接产出本结构，cangjie-skill 仍是蒸馏引擎（不改动），本阶段只做“书级封装”。

## 工程坑（必读，曾导致整轮返工）

- **中文/沙箱路径**：在部分隔离运行环境（沙箱）下，Python 写入含**中文字符**的路径时，文件列举与读取可能读不到。规避：① 工作目录与所有产物用 **ASCII slug**（如 `books/bei-taoyan-de-yongqi`）；② 若需确认 Python 是否真的写出，让它 `print` 到 stdout 再读，或直接用文件写入方式落盘交付物。
- **Windows 路径 mangling**：在 Git Bash 里 `os.path.join('D:/Downloads', 'x.epub')` 会产生反斜杠混乱。规避：用 `glob.glob('*.epub')` 在目标盘根目录定位，或全程传绝对路径字符串；脚本内部用 `pathlib` 处理。
- **EPUB 章节顺序**：优先按 OPF `spine` 顺序；解析失败则回退按文件名自然排序（取前导数字）。避免按 zip 内默认顺序（常乱序）。
- **Python 环境**：脚本仅依赖标准库（`zipfile` / `html.parser` / `xml.etree`），无需安装任何第三方包；用任意 Python 3 运行即可（如 `python3`），避免污染用户环境。

## 质量红线

- 每个 skill 必须过 cangjie-skill 的三重验证 + 完整 R / I / A1 / A2 / E / B。
- 盲测路由通过率 **≥ 0.8**（should_not_trigger 0 容忍）。
- `test-prompts.json` 必须含兄弟 skill 混淆诱饵。
- 安装后才算交付完成。

## 参考

- `references/workflow.md` — 完整编排细节 + 各脚本参数 + test-results 模板。
- `scripts/extract_epub.py` — EPUB→txt 提取（spine 感知 + 中文路径安全）。
- `scripts/blind_routing_test.py` — 确定性跨 skill 盲测路由。
- `scripts/route.py` — 通用书级路由引擎（确定性、可测试、可演化）。
- `scripts/make_book_skill.py` — 把平铺原子 skill 组装成 adler-counsel 风格书级 skill。
