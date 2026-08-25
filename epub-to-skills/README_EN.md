# epub-to-skills — EPUB → executable skills pipeline

An end-to-end pipeline that turns "take an EPUB → produce a set of installable, stress-tested agent skills" into a **deterministic, reusable** flow. On top of the [cangjie-skill](https://github.com/) distillation engine, it adds two engineering capabilities — reliable EPUB text extraction and automated cross-skill confusion stress testing — and bakes in fixes for pitfalls around Chinese book titles, Windows paths, and sandbox isolation.

> This skill does not re-implement cangjie-skill's distillation methodology; it only fills the two engineering gaps and hardens the lessons learned.

## Relation to cangjie-skill

- **cangjie-skill**: the distillation engine (RIA-TV++: understand / extract / verify / construct / link / deliver).
- **This skill**: ① reliable EPUB → text ingestion; ② a **deterministic** cross-skill blind-routing test at stage 4 (replacing the flaky "sub-agent blind test" approach); ③ pipeline orchestration + install; ④ assembling a "one book = one skill" book-level bundle.

## Structure

```
epub-to-skills/
├── SKILL.md                       # pipeline entry point
├── references/workflow.md         # full orchestration details + script flags + report template
└── scripts/
    ├── extract_epub.py            # EPUB → plain text (spine-aware + Chinese-path safe)
    ├── blind_routing_test.py      # deterministic cross-skill blind-routing test (stress test)
    ├── route.py                   # generic book-level routing engine (deterministic, testable)
    └── make_book_skill.py         # assemble flat atomic skills into a book-level bundle
```

## Install

Place `epub-to-skills/` wherever your agent loads skills from (e.g. `~/.skills/epub-to-skills/` or `<repo>/skills/epub-to-skills/`).

## Quick start

### Stage A — EPUB ingestion

```bash
python scripts/extract_epub.py \
  --epub "D:/Downloads/the-courage-to-be-disliked.epub" \
  --out "./books/bei-taoyan-de-yongqi" \
  --slug bei-taoyan-de-yongqi
```

Outputs `./books/bei-taoyan-de-yongqi/_book_text.txt` (chapters separated by `=== <relpath> ===`) and prints chapter count / total characters.

### Stage B — distillation core

Hand `_book_text.txt` to cangjie-skill and run its RIA-TV++ stages 0–3 (book understanding → extractors → triple verification → RIA++ construction → linking). This skill does not cover that part.

### Stage C — automated stress test

```bash
python scripts/blind_routing_test.py --skills-dir "./books/bei-taoyan-de-yongqi" --min-pass 0.8
```

The script collides every prompt against every skill's `trigger` signature (exact trigger-phrase hit + Chinese bigram overlap scoring) and reports the winning skill and PASS / FAIL per case. If it fails, strengthen the `trigger` phrases or `description`, then re-run until all green.

### Stage D / E — deliver & assemble book-level skill

```bash
python scripts/make_book_skill.py \
  --skills-dir "./books/bei-taoyan-de-yongqi" \
  --book-slug "bei-taoyan-de-yongqi" \
  --book-title "The Courage to Be Disliked" \
  --out-root "~/.skills"
```

The assembler will:
- add `parent_skill` + `type: sub-skill` to each atomic skill's frontmatter and move it into `<book-slug>/subskills/<slug>/`;
- copy the generic routing engine `scripts/route.py`;
- generate the book-level `SKILL.md` (entry + routing rules + crisis guardrail);
- auto-sample `<book-slug>/test-prompts.json` and write an empty `combos.json`;
- immediately run `route.py --self-test` to confirm routing regression (should be 100%).

## Quality gates

- every skill must pass triple verification + full `R / I / A1 / A2 / E / B`;
- blind-routing pass rate **≥ 0.8** (`should_not_trigger` is zero-tolerance);
- `test-prompts.json` must include sibling-skill confusion bait;
- delivery is only complete after install.

## Engineering notes (read first)

- **Chinese / sandbox paths**: in some isolated (sandboxed) runtimes, Python writing to paths with Chinese characters may be unreadable on list/read. Mitigation: always use **ASCII slugs** for working dirs and outputs (e.g. `books/bei-taoyan-de-yongqi`).
- **Windows paths**: locate files with `glob.glob('*.epub')` or pass absolute paths throughout; scripts use `pathlib` internally to avoid backslash mangling.
- **EPUB chapter order**: prefer OPF `spine`; fall back to natural filename sort; avoid the zip's default order (often shuffled).
- **Python**: scripts depend only on the standard library (`zipfile` / `html.parser` / `xml.etree`); run with any Python 3, no install needed.

## Dependencies

Python 3 standard library only.

## License

MIT
