# adler-counsel — "The Courage to Be Disliked" · one book, one skill

Distills the book *The Courage to Be Disliked* (Ichiro Kishimi / Fumitake Koga) into a single agent skill. Core idea: **one book = one skill**; the book's 12 atomic concepts (teleology / separation of tasks / courage to be disliked / horizontal relations / self-acceptance / trust in others / happiness as contribution / community feeling / living in the now / life-lies / inferiority triad / courage to be ordinary) are **nested sub-skills** selected automatically by a deterministic routing engine, so the user never has to pick among concepts manually.

## What it does

Activates automatically when the conversation touches self-worth, relationships, meaning of life, emotional attribution, present / future anxiety, etc., and responds following the matched sub-skill's `R / I / A1 / A2 / E / B` sections.

> ⚠️ This skill does not replace professional counseling. On real crisis signals (self-harm / harm to others, acute psychiatric symptoms, clear abuse, need for medical / legal diagnosis) it routes nothing and explicitly recommends seeking professional help.

## Structure

```
adler-counsel/
├── SKILL.md                 # book-level entry + routing rules + crisis guardrail
├── scripts/route.py         # deterministic routing engine (testable / evolvable)
├── test-prompts.json        # routing regression set (run by route.py --self-test)
└── subskills/               # 12 atomic sub-skills (not standalone skills)
    ├── teleology/SKILL.md (+ test-prompts.json + test-results.md)
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

## Install

Place the whole `adler-counsel/` directory wherever your agent loads skills from, e.g.:

- user-level: `~/.skills/adler-counsel/`
- project-level: `<repo>/skills/adler-counsel/`

> `~/.skills` is just a generic placeholder; point it at the actual skills root your agent uses.

## Usage

Triggers on signals like relationship friction, self-attack, fear of disapproval, past-based attribution, present / future anxiety, inferiority / ordinary-anxiety. Internally:

```bash
python scripts/route.py --question "my kid won't listen and talks back" --json
```

Returns:

```json
{ "crisis": false, "primary": "separation-of-tasks", "secondary": "horizontal-relations", "combo": true, "scores": { "...": 0 } }
```

- `crisis: true` → route nothing, redirect to professional help.
- otherwise read `subskills/<primary>/SKILL.md` and respond per its `R / I / A1 / A2 / E / B` sections;
- when `combo: true`, also blend the `secondary` sub-skill's perspective.

## Routing engine

`scripts/route.py` is **deterministic, testable, evolvable**:

- exact trigger-phrase hit (strong signal, weighted) + Chinese bigram overlap (weak signal) scoring;
- 7 known combos (e.g. "childhood trauma + afraid to speak" → `teleology` + `courage-to-be-disliked`);
- run the regression:

```bash
python scripts/route.py --self-test
# == routing self-test (20 cases, threshold 0.9) ==  → 100% pass
```

## Evolution

- mis-route → add a case to `test-prompts.json` (`expected:[slug]` or `crisis:true`) → re-run `--self-test`;
- each sub-skill's own `test-prompts.json` is its regression set; missing / false triggers surface by adding cases.

## Dependencies

Python 3 standard library only; no third-party packages required.

## License

MIT
