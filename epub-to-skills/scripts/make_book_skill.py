#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把平铺的 N 个原子 skill 组装成 adler-counsel 风格的书级 skill bundle。

输入: 一个目录，里面是 N 个原子 skill 子目录（每个含 SKILL.md + test-prompts.json）。
输出: <out-root>/<book-slug>/ 书级 skill：
  <book-slug>/
    SKILL.md            # 书级总入口（自动路由说明 + 危机护栏）
    scripts/route.py    # 通用确定性路由引擎（从本 skill 复制）
    combos.json         # 组合对配置（默认空，后续可声明）
    test-prompts.json   # 路由回归锚点（自动抽样生成）
    subskills/<slug>/   # 原子概念 = 子 skill（frontmatter 加 parent_skill/type）
"""
import argparse, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = r"""---
name: {slug}
version: 1.0.0
description: {title} 的拆解 skill 包。一本书 = 一个 skill，原子概念作为内部子 skill 嵌套，由确定性路由引擎自动挑选，使用者不需在多个概念间手动选择。当用户提出与《{title}》主题相关的困惑、关系议题、人生/成长/情绪议题时调用；危机信号（自伤/伤人/受虐）直接转专业帮助。
---

# {title} — 书级 skill（自动路由到原子概念子 skill）

## 使命
把《{title}》蒸馏出的 {n} 个原子概念封装为一个书级入口。上游/用户只调本 skill，由 scripts/route.py 决定激活哪个（或哪两个组合）子 skill，再由本 skill 加载 subskills/<slug>/SKILL.md 按其 R/I/A1/A2/E/B 与边界段执行。

## 子 skill（原子概念）
{sublist}

## 执行流程（被调用时）
1. 取用户问题，跑路由：
   ```bash
   python scripts/route.py --question "<用户问题>" --json
   ```
2. 读返回：
   - crisis: true -> 不路由任何子 skill，直接告知转专业帮助（心理危机热线/就医/报警），并停止。
   - 否则取 primary（必选）+ secondary（组合时存在）。
3. 加载并遵循对应子 skill：
   - Read subskills/<primary>/SKILL.md 按其 R/I/A1/A2/E/B 给出回应；
   - 若有 secondary，融合两子 skill 的视角（先 primary 主线，secondary 补充）。
4. 若路由返回 primary: null 且非危机（无强信号命中）-> 向用户追问一个区分性问题定位主轴，不要凭空二选一。

## 演化链路（回归测试兼容）
- test-prompts.json：路由回归锚点。新对话暴露误路由 -> 在该文件补样例（含 expected:[slug] 或 crisis:true）-> 重跑 python scripts/route.py --self-test 即回炉。
- combos.json：声明组合对（[["slugA","slugB"], ...]），当两概念同时出现即判为组合。
- 子 skill 各自 test-prompts.json 仍是其自身的回归测试集。

## 工程注意
- 子 skill 的 trigger: 短语是路由强信号，新增/补强概念时务必写好触发短语。
- 不单独把子 skill 注册为独立 skill；统一由本入口经文件读取加载，避免被当独立 skill 暴露。
"""


def read_md(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def parse_fm(md):
    if not md.startswith("---"):
        return ""
    return md.split("---", 2)[1]


def get_desc_summary(fm):
    m = re.search(r'description:\s*\|?\s*\n(.*?)(?=\n\w[\w-]*:|---|\Z)', fm, re.S | re.M)
    if m:
        return m.group(1).strip().split("。")[0][:60]
    m = re.search(r'description:\s*(.+)', fm)
    return (m.group(1).strip() if m else "")[:60]


def tag_subskill(skill_dir, parent):
    p = os.path.join(skill_dir, "SKILL.md")
    t = read_md(p)
    if "parent_skill:" in t and "type: sub-skill" in t:
        return
    parts = t.split("---\n", 2)
    if len(parts) == 3:
        fm = parts[1].rstrip("\n") + f"\nparent_skill: {parent}\ntype: sub-skill\n"
        t = "---\n" + fm + "---\n" + parts[2]
    else:
        parts = t.split("---", 2)
        if len(parts) != 3:
            print("  [skip-tag] frontmatter 异常:", p)
            return
        fm = parts[1].rstrip("\n") + f"\nparent_skill: {parent}\ntype: sub-skill\n"
        t = "---\n" + fm + "---\n" + parts[2]
    open(p, "w", encoding="utf-8").write(t)


def build_test_prompts(sub_dir):
    cases = []
    cid = 1
    for name in sorted(os.listdir(sub_dir)):
        tp = os.path.join(sub_dir, name, "test-prompts.json")
        if not os.path.isfile(tp):
            continue
        try:
            data = json.load(open(tp, encoding="utf-8"))
        except Exception:
            continue
        st = [c for c in data.get("test_cases", []) if c.get("type") == "should_trigger"]
        for c in st[:2]:
            cases.append({"id": f"auto{cid:02d}", "prompt": c["prompt"], "expected": [name]})
            cid += 1
    cases.append({"id": "auto-crisis", "prompt": "我最近总想死，感觉活着没意思",
                  "crisis": True})
    return {"minimum_pass_rate": 0.9, "test_cases": cases}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills-dir", required=True, help="含 N 个原子 skill 子目录的工作目录")
    ap.add_argument("--book-slug", required=True, help="ASCII 书级 slug")
    ap.add_argument("--book-title", required=True, help="书名")
    ap.add_argument("--out-root", required=True, help="安装/输出根目录（如 ~/.skills）")
    args = ap.parse_args()

    book_dir = os.path.join(args.out_root, args.book_slug)
    sub_dir = os.path.join(book_dir, "subskills")
    os.makedirs(sub_dir, exist_ok=True)

    subs = []
    for name in sorted(os.listdir(args.skills_dir)):
        sd = os.path.join(args.skills_dir, name)
        if not os.path.isdir(sd) or not os.path.isfile(os.path.join(sd, "SKILL.md")):
            continue
        tag_subskill(sd, args.book_slug)
        dst = os.path.join(sub_dir, name)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.move(sd, dst)
        subs.append(name)
        print(f"[move] {name} -> subskills/{name}")

    os.makedirs(os.path.join(book_dir, "scripts"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "route.py"), os.path.join(book_dir, "scripts", "route.py"))

    items = []
    for name in subs:
        fm = parse_fm(read_md(os.path.join(sub_dir, name, "SKILL.md")))
        summary = get_desc_summary(fm)
        items.append(f"- `{name}` — {summary}\n")
    sublist = "\n".join(items)

    skill_md = TEMPLATE.format(slug=args.book_slug, title=args.book_title,
                               n=len(subs), sublist=sublist)
    open(os.path.join(book_dir, "SKILL.md"), "w", encoding="utf-8").write(skill_md)

    open(os.path.join(book_dir, "combos.json"), "w", encoding="utf-8").write("[]\n")

    tp = build_test_prompts(sub_dir)
    json.dump(tp, open(os.path.join(book_dir, "test-prompts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"\n[完成] 书级 skill 已生成: {book_dir}")
    print(f"  子 skill 数: {len(subs)}")
    print("\n=== 路由自测 ===")
    rp = os.path.join(book_dir, "scripts", "route.py")
    import subprocess
    rc = subprocess.run([sys.executable, rp, "--self-test"]).returncode
    sys.exit(rc)


if __name__ == "__main__":
    main()