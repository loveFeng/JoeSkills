#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
adler-counsel 自动路由引擎（确定性、可测试、可演化）
===============================================
输入用户问题 -> 输出应激活的 sub-skill（1 个或组合 2 个）+ 危机标记。

设计目标：
- 用户/上游永远只调用 adler-counsel（一本书 = 一个 skill），本引擎决定内部子 skill，
  使用者不需要在 12 个原子概念里"选哪个"。
- 路由是确定性的（触发短语加权 + 中文 bigram 重叠），不是玄学；
- 可回归：--self-test 读取 test-prompts.json，把每条样本问题跑一遍核对预期，
  路由漂移时补用例即可自动暴露。

用法：
  python route.py --question "孩子不听我的还顶嘴"
  python route.py --question "..." --json
  python route.py --self-test            # 路由回归测试
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUBSKILLS = os.path.join(HERE, "..", "subskills")

# 危机关键词（命中即不路由任何子 skill，直接转专业帮助）
CRISIS_KW = ["自杀", "自伤", "想死", "不想活", "伤害自己", "杀了自己",
             "想杀", "杀人", "伤害别人", "家暴", "被虐待", "性侵", "抑郁发作",
             "精神崩溃", "幻听", "幻觉", "急性发作"]

# 已知组合对（当两个子 skill 同时高分时按此判定为组合而非误判）
COMBO_PAIRS = {
    frozenset(["teleology", "courage-to-be-disliked"]),
    frozenset(["separation-of-tasks", "horizontal-relations"]),
    frozenset(["inferiority-triad", "courage-to-be-disliked"]),
    frozenset(["contribution-happiness", "community-feeling"]),
    frozenset(["live-in-the-now", "life-lies"]),
    frozenset(["teleology", "life-lies"]),
    frozenset(["self-acceptance", "courage-to-be-ordinary"]),
}


def read_md(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def parse_frontmatter(md):
    if not md.startswith("---"):
        return ""
    return md.split("---", 2)[1]


def get_field(fm, key):
    # 块标量 (|,>) 或单行
    m = re.search(rf'^{key}:\s*\|?\s*\n(.*?)(?=\n\w[\w-]*:|---|\Z)', fm, re.S | re.M)
    if m:
        return m.group(1).strip()
    m = re.search(rf'^{key}:\s*(.+)$', fm, re.M)
    return m.group(1).strip() if m else ""


def extract_trigger(fm):
    # trigger 行可能缩进在 description 块内
    for line in fm.splitlines():
        s = line.strip()
        if s.startswith("trigger:"):
            raw = re.findall(r'"([^"]*)"', s)
            # 去掉尾部的省略号/标点，使其能匹配真实语句
            return [ph.strip().rstrip("。，、…；;：: .…") for ph in raw if ph.strip()]
    return []


def bigrams(s):
    cn = re.findall(r'[一-鿿]', s)
    return set(zip(cn, cn[1:])) if len(cn) > 1 else set()


def load_subskills(base=SUBSKILLS):
    out = {}
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        sk = os.path.join(d, "SKILL.md")
        if not os.path.isdir(d) or not os.path.exists(sk):
            continue
        md = read_md(sk)
        fm = parse_frontmatter(md)
        trig = extract_trigger(fm)
        # corpus = 描述 + R 段
        desc = get_field(fm, "description")
        rsec = re.search(r'## R[^\n]*\n(.*?)(?=## )', md, re.S)
        rtxt = rsec.group(1) if rsec else ""
        corpus = f"{desc} {rtxt}"
        out[name] = {"trigger": trig, "corpus": corpus}
    return out


def score(question, sub):
    sc = 0
    for ph in sub["trigger"]:
        if ph and ph in question:
            sc += 3
    pb = bigrams(question)
    cb = bigrams(sub["corpus"])
    if pb:
        sc += len(pb & cb) / len(pb) * 2
    return sc


def crisis_hit(q):
    return any(k in q for k in CRISIS_KW)


def route(question, subs):
    if crisis_hit(question):
        return {"crisis": True, "primary": None, "secondary": None,
                "combo": False, "scores": {}}
    # 精确触发短语命中（强信号，确定性）
    hits = {name: sum(1 for ph in sub["trigger"] if ph and ph in question)
            for name, sub in subs.items()}
    scored = {name: 3 * hits[name] + score(question, sub)
              for name, sub in subs.items()}
    ranked = sorted(scored.items(), key=lambda x: -x[1])
    top_name, top_sc = ranked[0]
    if top_sc == 0:
        return {"crisis": False, "primary": None, "secondary": None,
                "combo": False, "scores": {n: round(s, 2) for n, s in ranked[:3]}}
    # 组合判定（确定性、可演化）：两成员均命中触发短语即视为组合
    combo_pair = None
    for pair in COMBO_PAIRS:
        if hits.get(list(pair)[0], 0) >= 1 and hits.get(list(pair)[1], 0) >= 1:
            combo_pair = pair
            break
    # 退路：top2 形成已知对且次分不低于主分 0.4
    if combo_pair is None:
        for (n2, s2) in ranked[1:]:
            if s2 >= 0.4 * top_sc and frozenset([top_name, n2]) in COMBO_PAIRS:
                combo_pair = frozenset([top_name, n2])
                break
    secondary = None
    combo = False
    if combo_pair is not None:
        a, b = list(combo_pair)
        secondary = b if a == top_name else a
        combo = True
    return {
        "crisis": False,
        "primary": top_name,
        "secondary": secondary,
        "combo": combo,
        "scores": {n: round(s, 2) for n, s in ranked[:3]},
    }


def self_test(subs, test_path):
    if not os.path.exists(test_path):
        print(f"[self-test] 未找到 {test_path}")
        return 1
    data = json.load(open(test_path, encoding="utf-8"))
    cases = data.get("test_cases", [])
    min_pass = data.get("minimum_pass_rate", 0.9)
    fails = 0
    print(f"== adler-counsel 路由自测 ({len(cases)} 用例, 阈值 {min_pass}) ==")
    for c in cases:
        q = c["prompt"]
        exp = set(c.get("expected", []))
        r = route(q, subs)
        if r["crisis"]:
            pred = set()
        else:
            pred = {r["primary"]} | ({r["secondary"]} if r["secondary"] else set())
        ok = exp <= pred and (r["primary"] in exp if exp else True)
        if not ok:
            fails += 1
            print(f"  [FAIL] {c['id']}: exp={exp} got_primary={r['primary']} "
                  f"got_sec={r['secondary']} :: {q[:40]}")
        else:
            print(f"  [PASS] {c['id']}: -> {sorted(pred)}  (exp {sorted(exp)})")
    rate = 1 - fails / len(cases) if cases else 0
    print(f"\n通过率 {rate:.0%}  (>= {min_pass:.0%} {'OK' if rate >= min_pass else 'FAIL'})")
    return 0 if rate >= min_pass else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", help="用户问题")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--subskills-dir", default=SUBSKILLS)
    args = ap.parse_args()

    subs = load_subskills(args.subskills_dir)

    if args.self_test:
        test_path = os.path.join(HERE, "..", "test-prompts.json")
        sys.exit(self_test(subs, test_path))

    if not args.question:
        ap.error("需要 --question 或 --self-test")

    r = route(args.question, subs)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        if r["crisis"]:
            print("⚠️ 危机信号 -> 转专业帮助，不路由任何子 skill")
        else:
            line = f"主: {r['primary']}"
            if r["secondary"]:
                line += f" | 组合: {r['secondary']}"
            print(line)
            print("分: " + ", ".join(f"{k}={v}" for k, v in r["scores"].items()))


if __name__ == "__main__":
    main()
