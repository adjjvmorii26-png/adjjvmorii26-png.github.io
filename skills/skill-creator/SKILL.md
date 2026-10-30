---
name: skill-creator
description: Create and validate skills for this repository. Use when the user asks to add a skill, capture a workflow as a reusable procedure, or turn a repeated multi-step task into something the agent can find and follow again.
---

# Skill creator

A skill is a small, self-contained procedure the agent can discover and follow.
It is not documentation for humans and not a prompt dump: it is the shortest
reliable path from "task X appeared" to "task X is done correctly".

Scaffold with `python3 scripts/new-skill.py <slug> --description "..."`, then
validate with `python3 scripts/check-skills.py`. Both are also run by
`scripts/check-all.sh`.

## When to create a skill

- The same multi-step task has been done twice and will happen again.
- A procedure has non-obvious ordering, tool choice, or failure modes.
- Something must never be done a particular way (a guardrail worth repeating).

Do **not** create one for a single command — that belongs in a README.

## Layout

```
skills/<slug>/
  SKILL.md          required; frontmatter + procedure
  references/       optional; long-form detail loaded only when needed
  scripts/          optional; helpers the skill runs
```

One directory per skill, named with lowercase words and single hyphens
(`pdf-report`, not `PDF_Report` or `pdf--report`).

## Frontmatter

```yaml
---
name: pdf-report
description: Build a PDF report from tabular data. Use when the user asks for a
  printable or shareable report from a table, CSV, or query result.
---
```

Rules the validator enforces:

| Rule | Why |
|---|---|
| `name` equals the directory name | Skills are looked up by name; drift breaks discovery. |
| `description` 20–1024 chars | Too short is useless, too long buries the trigger. |
| `description` says when to use it | This is the only text used to decide whether to open the skill. |
| Body at least 120 chars | A heading alone is not a procedure. |
| Relative links resolve | A skill pointing at a missing file fails exactly when it matters. |

Write the description in the third person and lead with the action: "Build…",
"Audit…", "Convert…". Include the words a user would actually type.

## Writing the procedure

1. **Start with the outcome.** What must be true when the skill finishes?
2. **Number the steps.** Each step is one action with one verification.
3. **Name the exact commands**, not "run the tests" — the reader may be a
   different model or a future you with no memory of this conversation.
4. **State the failure modes.** What goes wrong most often, and what to do then.
5. **Say how to prove it worked.** "Verified by X" beats "looks correct".

Prefer 15–60 lines. If it needs more, move detail into `references/` and link it,
so the body stays scannable.

## Anti-patterns

- **Restating the prompt.** A skill that repeats "you are a helpful assistant"
  adds nothing and costs context.
- **Secrets or tokens.** Never. They belong in a secret store, and
  `scripts/check-secrets.py` will fail the build.
- **Untestable claims.** "Ensures correctness" cannot be verified; "runs
  `scripts/check-all.sh` and requires exit 0" can.
- **Duplicating another skill.** Check `skills/` first; extend instead of cloning.

## Checklist before finishing

1. `python3 scripts/check-skills.py` exits 0.
2. `python3 scripts/check-all.sh` still passes.
3. The description contains the phrase a user would search for.
4. Every command in the body was actually run at least once.
