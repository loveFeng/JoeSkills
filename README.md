# JoeSkills

> 一组可直接在 agent 中使用的 **skill**（技能）集合，聚焦「把书变成可执行技能」与「心理/成长领域的对话咨询」。
> A collection of ready-to-use agent **skills**, focused on turning books into executable skills and on psychology/growth conversational counseling.

本仓库中的 skill 已去除任何平台专有内容，可在任意兼容 Skill 协议的 agent 中安装使用。
All skills in this repo have been stripped of any platform-specific content and can be installed in any agent that supports the Skill protocol.

---

## 目录 / Skills

### 1. `book-skills/adler-counsel` — 阿德勒心理学咨询 / Adler Psychology Counseling

- 一本书 = 一个 skill：以《被讨厌的勇气》为蒸馏入口，内含 12 个原子「子 skill」（目的论、课题分离、被讨厌的勇气、横向关系、自我接纳、他者信赖、共同体感觉、活在当下等）。
- 内置路由引擎 (`scripts/route.py`)，按用户原话确定性分发到最合适的子 skill，并带 self-test。
- A book = one skill: distills *The Courage to Be Disliked* into 12 atomic sub-skills, with a deterministic router and self-test.

📄 文档 / Docs: [中文 README](book-skills/adler-counsel/README.md) · [English README](book-skills/adler-counsel/README_EN.md)

### 2. `epub-to-skills` — EPUB 蒸馏为 Skill 流水线 / EPUB-to-Skills Pipeline

- 把一本 EPUB 电子书蒸馏成一组可执行 agent skill 的一站式流水线封装。
- 在通用蒸馏引擎之上补齐「可靠的 EPUB 文本提取」与「自动化跨 skill 盲测路由」两块工程能力，并固化中文书名 / 非 ASCII 路径的工程坑规避方法。
- One-stop pipeline that distills an EPUB into a set of executable agent skills, adding reliable text extraction and automated blind-routing on top of a generic distiller.

📄 文档 / Docs: [中文 README](epub-to-skills/README.md) · [English README](epub-to-skills/README_EN.md)

---

## 安装 / Installation

不同 agent 的 skills 根目录约定不同，请将 skill 目录放到你 agent 实际的 skills 根目录（通用占位为 `~/.skills`）：

```bash
# 例：复制到用户级 skills 目录
cp -r book-skills/adler-counsel ~/.skills/
cp -r epub-to-skills            ~/.skills/
```

Install the skill directories into your agent's actual skills root (generic placeholder: `~/.skills`):

```bash
cp -r book-skills/adler-counsel ~/.skills/
cp -r epub-to-skills            ~/.skills/
```

> 脚本依赖仅 Python 3 标准库（无需 `pip install`）。
> Scripts depend only on the Python 3 standard library (no `pip install` required).

---

## 许可证 / License

MIT — 详见各 skill 目录内许可证说明。 / See license notes inside each skill directory.
