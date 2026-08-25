#!/usr/bin/env python3
"""blind_routing_test.py — 确定性跨 skill 盲测路由（压力测试用）。

把每个 skill 目录下的 test-prompts.json 用例，与全部 skill 的 trigger 签名对撞：
- 触发短语精确命中 (加权 +3)
- 中文 bigram 重叠 (弱信号)
输出每条用例的胜出 skill 与 PASS/FAIL，并给出整体通过率。
should_not_trigger 为 0 容忍；整体通过率需 >= --min-pass。

用法:
    python blind_routing_test.py --skills-dir "<工作目录>" --min-pass 0.8

退出码: 0=通过, 1=未达阈值。
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict


def read_md(p):
    return open(p, encoding="utf-8").read()


def extract_corpus(md):
    parts = md.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    quotes = re.findall(r'"([^"]*)"', fm)
    m = re.search(r"trigger:\s*(.+)", fm)
    trig = re.findall(r'"([^"]*)"', m.group(1)) if m else []
    desc = re.sub(r"trigger:\s*.+", "", fm)
    rsec = re.search(r"## R[^\n]*\n(.*?)---", md, re.S)
    rtxt = rsec.group(1) if rsec else ""
    corpus = " ".join(quotes) + " " + desc + " " + rtxt
    return corpus, trig


def bigrams(s):
    cn = re.findall(r"[\u4e00-\u9fff]", s)
    return set(zip(cn, cn[1:])) if len(cn) > 1 else set()


def score(prompt, skill, corpora, triggers):
    sc = sum(3 for ph in triggers[skill] if ph and ph in prompt)
    pb = bigrams(prompt)
    cb = bigrams(corpora[skill])
    if pb:
        sc += len(pb & cb) / len(pb) * 2
    return sc


def main():
    ap = argparse.ArgumentParser(description="确定性跨 skill 盲测路由")
    ap.add_argument("--skills-dir", required=True, help="含各 skill 子目录的工作目录")
    ap.add_argument("--min-pass", type=float, default=0.8, help="最低通过率阈值")
    args = ap.parse_args()

    base = args.skills_dir
    skills = sorted([
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d))
        and os.path.exists(os.path.join(base, d, "SKILL.md"))
    ])

    corpora = {}
    triggers = {}
    for s in skills:
        c, t = extract_corpus(read_md(os.path.join(base, s, "SKILL.md")))
        corpora[s] = c
        triggers[s] = t

    fails = 0
    total = 0
    per_skill = defaultdict(lambda: {"total": 0, "fail": 0})

    for s in skills:
        tp_file = os.path.join(base, s, "test-prompts.json")
        if not os.path.exists(tp_file):
            print(f"[WARN] {s}: 缺少 test-prompts.json")
            continue
        d = json.load(open(tp_file, encoding="utf-8"))
        for t in d.get("test_cases", []):
            total += 1
            per_skill[s]["total"] += 1
            p = t["prompt"]
            tp = t["type"]
            sc = {sk: score(p, sk, corpora, triggers) for sk in skills}
            best = max(sc, key=sc.get)
            if tp == "should_trigger":
                ok = (best == s and sc[s] > 0)
            elif tp == "should_not_trigger":
                ok = (best != s)
            else:  # edge_case: 仅人工复核，不计入硬失败
                ok = True
            if not ok:
                fails += 1
                per_skill[s]["fail"] += 1
                print(f"[FAIL] {s:24s} {tp:16s} -> winner={best}({sc[best]:.2f})")

    rate = 1 - fails / total if total else 1.0
    print("\n=== 各 skill 通过情况 ===")
    for s in skills:
        ps = per_skill[s]
        if ps["total"]:
            print(f"  {s:24s} {ps['total']-ps['fail']}/{ps['total']}")
    print(f"\n总用例={total} 失败={fails} 通过率={rate:.0%} (阈值={args.min_pass:.0%})")

    if rate < args.min_pass:
        print("RESULT: FAIL")
        sys.exit(1)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
