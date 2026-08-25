#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""<book> 自动路由引擎（确定性、可测试、可演化）。

由 epub-to-skills 的 make_book_skill.py 复制而来，通用版本：
- 子 skill 自动从 subskills/ 发现；
- 组合对从 combos.json 读取（默认空 = 不自动组合）；
- 危机关键词通用。

用法:
  python route.py --question "..."
  python route.py --question "..." --json
  python route.py --self-test
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK_DIR = os.path.abspath(os.path.join(HERE, ".."))
SUBSKILLS = os.path.join(BOOK_DIR, "subskills")

CRISIS_KW = ["自杀", "自伤", "想死", "不想活", "伤害自己", "杀了自己", "想杀", "杀人",
             "伤害别人", "家暴", "被虐待", "性侵", "抑郁发作", "精神崩溃", "幻听", "幻觉", "急性发作"]


def load_combos(book_dir):
    p = os.path.join(book_dir, "combos.json")
    if os.path.isfile(p):
        try:
            return {frozenset(c) for c in json.load(open(p, encoding="utf-8"))}
        except Exception:
            return set()
    return set()


def read_md(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def parse_fm(md):
    if not md.startswith("---"):
        return ""
    return md.split("---", 2)[1]


def extract_trigger(fm):
    for line in fm.splitlines():
        s = line.strip()
        if s.startswith("trigger:"):
            raw = re.findall(r'"([^"]*)"', s)
            return [ph.strip().rstrip("。，、…；;：: .…") for ph in raw if ph.strip()]
    return []


def bigrams(s):
    cn = re.findall(r'[一-鿿]', s)
    return set(zip(cn, cn[1:])) if len(cn) > 1 else set()


def load_subskills(base=SUBSKILLS):
    out = {}
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        sk = os.path.join(d, "SKILL.md")
        if not os.path.isdir(d) or not os.path.isfile(sk):
            continue
        fm = parse_fm(read_md(sk))
        trig = extract_trigger(fm)
        desc = ""
        m = re.search(r'description:\s*\|?\s*\n(.*?)(?=\n\w[\w-]*:|---|\Z)', fm, re.S | re.M)
        if m:
            desc = m.group(1)
        rsec = re.search(r'## R[^\n]*\n(.*?)(?=## )', read_md(sk), re.S)
        rtxt = rsec.group(1) if rsec else ""
        out[name] = {"trigger": trig, "corpus": f"{desc} {rtxt}"}
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


def route(question, subs, combos):
    if crisis_hit(question):
        return {"crisis": True, "primary": None, "secondary": None, "combo": False, "scores": {}}
    hits = {name: sum(1 for ph in sub["trigger"] if ph and ph in question) for name, sub in subs.items()}
    scored = {name: 3 * hits[name] + score(question, sub) for name, sub in subs.items()}
    ranked = sorted(scored.items(), key=lambda x: -x[1])
    top_name, top_sc = ranked[0]
    if top_sc == 0:
        return {"crisis": False, "primary": None, "secondary": None, "combo": False,
                "scores": {n: round(s, 2) for n, s in ranked[:3]}}
    combo_pair = None
    for pair in combos:
        a, b = list(pair)
        if hits.get(a, 0) >= 1 and hits.get(b, 0) >= 1:
            combo_pair = pair
            break
    if combo_pair is None:
        for (n2, s2) in ranked[1:]:
            if s2 >= 0.4 * top_sc and frozenset([top_name, n2]) in combos:
                combo_pair = frozenset([top_name, n2])
                break
    secondary = None
    combo = False
    if combo_pair is not None:
        a, b = list(combo_pair)
        secondary = b if a == top_name else a
        combo = True
    return {"crisis": False, "primary": top_name, "secondary": secondary, "combo": combo,
            "scores": {n: round(s, 2) for n, s in ranked[:3]}}


def self_test(subs, combos, test_path):
    if not os.path.exists(test_path):
        print(f"[self-test] 未找到 {test_path}")
        return 1
    data = json.load(open(test_path, encoding="utf-8"))
    cases = data.get("test_cases", [])
    min_pass = data.get("minimum_pass_rate", 0.9)
    fails = 0
    print(f"== 路由自测 ({len(cases)} 用例, 阈值 {min_pass}) ==")
    for c in cases:
        q = c["prompt"]
        r = route(q, subs, combos)
        if c.get("crisis"):
            ok = bool(r["crisis"])
            pred = set()
        else:
            exp = set(c.get("expected", []))
            pred = {r["primary"]} | ({r["secondary"]} if r["secondary"] else set())
            ok = exp <= pred and (r["primary"] in exp if exp else True)
        if not ok:
            fails += 1
            print(f"  [FAIL] {c.get('id')}: exp={c.get('expected')} crisis={c.get('crisis')} "
                  f"got={r['primary']}/{r['secondary']} :: {q[:40]}")
        else:
            print(f"  [PASS] {c.get('id')}: -> {sorted(pred) if pred else 'CRISIS'}")
    rate = 1 - fails / len(cases) if cases else 0
    print(f"\n通过率 {rate:.0%}  (>= {min_pass:.0%} {'OK' if rate >= min_pass else 'FAIL'})")
    return 0 if rate >= min_pass else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--subskills-dir", default=SUBSKILLS)
    args = ap.parse_args()
    subs = load_subskills(args.subskills_dir)
    combos = load_combos(BOOK_DIR)
    if args.self_test:
        test_path = os.path.join(BOOK_DIR, "test-prompts.json")
        sys.exit(self_test(subs, combos, test_path))
    if not args.question:
        ap.error("需要 --question 或 --self-test")
    r = route(args.question, subs, combos)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        if r["crisis"]:
            print("CRISIS -> 转专业帮助，不路由任何子 skill")
        else:
            line = f"primary: {r['primary']}"
            if r["secondary"]:
                line += f" | combo: {r['secondary']}"
            print(line)
            print("scores: " + ", ".join(f"{k}={v}" for k, v in r["scores"].items()))


if __name__ == "__main__":
    main()
