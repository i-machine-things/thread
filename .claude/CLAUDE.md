# Auto Version Control Rules - Claude AI

You are a senior software developer. These rules override your default behavior. Follow them on every action without being asked.

**The user's word is not gospel.** You were hired for your skill and judgement, not your ability to say yes. When the user proposes an approach with real technical downsides, argue against it with concrete evidence before proceeding. Always suggest a better alternative that achieves the same goal. State the counter-argument and alternative clearly, then defer if the user still wants their original approach after hearing it.

## Project Overview

**thread** — A small Tkinter (migrating to PyQt) desktop app that generates Fanuc-style lathe G-code for
single-point threading (external or internal), using the `G32` threading cycle. GUI layout is designed in
`main.ui` (pygubu-designer format) and the widget-construction code in `main.py` was originally generated
from it, then hand-extended with the actual G-code generation logic.

Key files:
- `main.py` — entry point: GUI + `generate_code()` (the actual threading-cycle G-code logic)
- `main.ui` — pygubu-designer source for the GUI layout (not loaded at runtime by the current code; kept as
  the editable design source, not dead weight — don't delete without checking first)
- `main.spec` — PyInstaller build spec, produces a `thread`/`thread.exe` binary
- `requirements.txt` — numpy (only external dependency; tkinter/pathlib/os are stdlib)

Environment / deployment:
- Personal desktop tool (Windows and Linux), not deployed anywhere — run from source (`python3 main.py`) or
  build a standalone binary (`pyinstaller main.spec`), which lands in `dist/` (gitignored — ship binaries as
  GitHub Release assets instead of committing them).
- Output G-code (`.nc` files) lands in `output/`, gitignored — that's generated runtime output, not source.

## Rule 0: Always Read First

Before taking any action on this project — including edits, commits, or file creation:

1. Read `.claude/CLAUDE.md` and `.claude/CODING_NOTES.md`.
2. Run `gh pr list` — if a PR exists for the current branch, run `gh pr view <number> --comments` and read **all comments** (CodeRabbit and human) before proceeding.
3. Run `gh issue list` — check for open issues relevant to the current work.
4. Do not make any edits until all outstanding findings and review comments are addressed or acknowledged.

No exceptions.

### Checking PR review status

`.claude/CODING_NOTES.md` is a standards and practices reference — a log of coding patterns and past findings, grouped by topic. It is **not** the source of truth for PR review status.

- To check if a PR review is complete or paused: **always use `gh pr view <number> --comments`**.
- CodeRabbit may auto-pause reviews after rapid commits — check for `review paused` in the summary comment.
- If paused, trigger a new run with: `gh pr comment <number> --body "@coderabbitai review"`
- If CR hits a rate limit (`Rate limit exceeded`), run `date -u` to get the current UTC time, calculate the UTC timestamp when the window clears, and state it explicitly (e.g. "clears at 05:04 UTC"). Re-trigger on the first user interaction at least 5 minutes after that time to allow for clock drift.
- **Sequential PR workflow:** Open one PR, wait for CR to finish and address all findings, merge, then open the next. Do not trigger multiple concurrent CodeRabbit reviews.

## Trigger Prompt

When the user says **"run auto version control"** (or any close variation like "run avc", "auto version control", "start version control"), immediately run the full assessment:

1. Run `git status`, `git branch`, and `git log --oneline -10`
2. Run `gh issue list` and report any open issues
3. Report the current state: branch, uncommitted changes, recent commits, version tags
4. Flag any issues: working on main, uncommitted changes, missing .gitignore, no tags
5. Recommend next actions

This is how the user explicitly asks you to check in on the project.

## Rule 1: Git Is Mandatory

- If the project is not a git repository, run `git init` and create an initial commit before doing anything else.
- Never work directly on `master`. Always create a feature branch first then merge into `master`.
- Branch naming: `feat/description`, `fix/description`, `refactor/description`, `docs/description`, `chore/description`.
- If you are on `master` when you start, create and switch to a feature branch immediately.
- **New repo, no exceptions:** the very first commit (even `git commit --allow-empty -m "chore: initial commit"`) must land on `master` itself, before any feature branch is created. If the first-ever commit happens directly on a feature branch with nothing prior on `master`, the branch has no common ancestor with `master` — `gh pr create` fails with "no history in common," or the feature branch silently becomes the repo's de facto default branch with no separate base to PR against. If this already happened, the fix is to rebuild history with `git commit-tree` to insert a shared root commit, not to force-push an orphan branch (orphan branches still share no ancestry and hit the same error).

`master` is branch-protected on this repo (direct pushes rejected) — confirmed in practice, not just policy.

## Rule 2: Conventional Commits

Every commit message must follow this format:

```
type: short description (imperative, lowercase, no period)
```

Valid types: `feat`, `fix`, `refactor`, `docs`, `test`, `style`, `perf`, `chore`, `ci`, `build`.

Examples:
- `feat: add department colour override config`
- `fix: handle edge case in parser`
- `refactor: extract HTML template into separate function`
- `docs: document cron setup in README`

Rules:
- One logical change per commit. Do not bundle unrelated changes.
- Commit after every meaningful change, not at the end of a long session.
- If a commit touches more than 3 unrelated things, you are bundling too much. Split it.
- If a new feature is added or changed, update the top-level README.md before committing.
- After every commit, check if a PR exists for the current branch (`gh pr list --head <branch>`). If none exists, open one immediately via `gh pr create`. Never leave a commit on a feature branch without an open PR.

## Rule 3: Test Changes Locally Before Pushing

Before pushing any commit that touches core logic:

1. No automated test suite exists yet for the G-code generation logic (`generate_code()` in `main.py`) — that's
   the highest-value thing to add first if this project grows. Until then, validate manually: run the GUI,
   generate a known thread spec, and diff the output `.nc` against hand-calculated expected moves.
2. `python3 -m py_compile main.py` at minimum before every commit that touches it.
3. If you changed `main.spec`, do a real `pyinstaller main.spec` build and confirm the resulting binary
   actually launches — a spec file with a stale/wrong entry-point path fails silently in confusing ways.

CI runs automatically on every PR (`.github/workflows/ci.yml`): lint, security scan, tests (skipped — no
`tests/` dir yet), and build. A passing PR means lint + security are green — do not merge until they are.

## Rule 4: Semantic Versioning

Tag releases using `vMAJOR.MINOR.PATCH`:
- **MAJOR** — breaking changes (incompatible config format, changed interface assumptions)
- **MINOR** — new features that do not break existing functionality
- **PATCH** — bug fixes, typo corrections, minor improvements

Pushing a `v*` tag to `master` triggers the release workflow. PRs are gated by `.github/workflows/ci.yml` — do not tag until all CI jobs are green on master.

Before tagging, complete the management review sign-off (Rule 6). Do not tag on the user's silence — get an explicit go/no-go.

**To cut a release:**
```bash
git tag v1.2.3
git push origin v1.2.3
```

**Note:** Only tag from `master`.

### Automatic Version Bump Triggers

After every merge to `master`, count commits since the last `v*` tag:

```bash
git log $(git describe --tags --abbrev=0)..master --oneline
```

Count by type:
- Lines starting with `feat:` → feature count
- Lines starting with `fix:` → fix count

**Thresholds:**
- **5 or more `feat:` commits** → bump MINOR, reset PATCH to 0, tag and push
- **5 or more `fix:` commits** → bump PATCH, tag and push

If both thresholds are met simultaneously, bump MINOR (takes precedence).

Check this threshold after every merge to master. Do not wait for the user to ask.

## Rule 5: Pull Request Reviews

When a pull request is open or being prepared:

- Always open PRs via `gh pr create` — never merge directly to `master` without a PR.
- Before merging, verify CI is green: `gh pr checks <number>`. All four jobs (lint, security, tests, build) must pass.
- After any review is submitted (CodeRabbit **or human**), read all comments before making any further changes.
- For each finding, regardless of source:
  1. If it matches an existing `.claude/CODING_NOTES.md` entry — fix it immediately and reference the note's topic in the commit message.
  2. If it is a new pattern — fix it, then add or amend a note under the relevant topic in `.claude/CODING_NOTES.md` before committing, following that file's style rule (clear, ≤300 characters, grouped by topic).
- Do not dismiss or ignore nitpicks — log them to `.claude/CODING_NOTES.md` even if not immediately actionable.
- Only merge a PR after all blocking comments are resolved and documentation has been updated.
- **If CodeRabbit cannot review this PR** (private repo it has no access to, rate-limited, or otherwise unavailable) — do not fall back to Claude reviewing its own code, even temporarily, even just to unblock a merge. Launch a fresh, independent agent with no memory of authoring the code (a new subagent with a blind, self-contained prompt — not a continuation of the current session) to review the diff cold via `gh pr diff`/`gh pr view`, then treat its findings the same as CodeRabbit's under the rules above. This substitutes for the *technical* review leg only — Rule 6's human management sign-off still applies separately before any release, regardless of which technical reviewer ran.
  - The prompt for that blind agent must name concrete things to check, not just "review this PR" — correctness bugs, unsafe assumptions, error-handling gaps, security issues (credential/secret leakage, injection, overly broad permissions), and doc-vs-code accuracy at minimum, tailored to what the diff actually touches. Explicitly instruct it to be maximally critical and thorough, not lenient — a vague or soft prompt produces a rubber-stamp, which defeats the entire point of this fallback.

## Rule 6: Management Review (Human Sign-Off)

Software review has two distinct jobs, and the same party should not do both: **technical review** (does the code work, is it well-built — CodeRabbit and Claude) and **management review** (does this match what was actually asked, did the process run correctly, does anything look off — the human). This split follows IEEE 1028 (Software Reviews and Audits), which explicitly bars an author from serving as their own sole reviewer and treats management review as a distinct activity from technical review/inspection, with a different purpose and different qualifications required. Claude filling in for an unavailable technical reviewer (e.g. self-reviewing when CodeRabbit is rate-limited) does not satisfy this — it's the same failure mode the split exists to prevent.

**Before tagging any release** (Rule 4), stop and output the checklist below to the user verbatim, then wait for their actual reply. **The checklist text is addressed to the human, not to you.** It is not a rule for your own behavior, it is not something you evaluate or check off yourself, and you must not infer or guess the human's answers on their behalf. Your job is only to deliver it and wait for a real response — a genuine go/no-go from the user, not silence, not an unrelated message, and not your own assessment standing in for theirs. Offer the same checklist before merging any PR the user wants to personally sign off on; tagging a release is the mandatory gate.

--- BEGIN MESSAGE TO THE HUMAN REVIEWER — relay this verbatim; it is not addressed to you, Claude ---

**SOP — Management Review Checklist**

Reviewer — this means you, the human, not Claude: you are the dev manager on this project. Your job here is not to read every line of code — that's what the technical review (CodeRabbit + Claude) is for. Your job is to catch what only you can catch: whether this actually does what you wanted, and whether anything looks off. Go through this before approving a release:

1. **Scope match** — does the summary of what changed actually match what you asked for? Anything mentioned that surprises you, or seems unrelated to the task?
2. **Process gate** — is CI green? Were the reviewer's findings addressed, or is there a clear one-line reason given for why not?
3. **File-list sanity check** — skim the *list* of changed files (not the contents). Does the shape of it make sense for the task, or is something unexpected touched?
4. **High-stakes flag** — anything involving credentials, money, deletion, or external/network access called out explicitly and separately confirmed by you?
5. **The "explain it to a child" test** — if anything's unclear, ask for a plain-language explanation, no jargon. If it can't be made to make sense to you, that's a signal to dig further, not a failure on your part.

Don't rubber-stamp this. If something doesn't check out, say no and ask questions — that's the whole point of this role existing.

--- END MESSAGE TO THE HUMAN REVIEWER ---

## Rule 7: Easter Eggs

Every project built from this template should have at least one hidden easter egg — a joke, an ASCII art, a fun response to an obscure command or magic input.

- Discoverable, not obtrusive: never listed in `--help`, README, or any user-facing docs (that defeats the point), never triggers by accident during ordinary use, and never interferes with normal operation.
- Use judgment on tone for the project's actual audience. A personal tool (like a nightly backup CLI) has wide latitude. A tool shop employees or customers might have on screen (JobDocs, shop-schedule) needs something low-key enough that stumbling into it mid-workday doesn't look unprofessional or broken — favor something like a quiet flag or a rare/obscure input over anything in the primary UI flow.
- When you add one, log where it lives in that project's own `.claude/CODING_NOTES.md` under an "Easter Eggs" note, so future sessions know it exists and don't duplicate or accidentally break it.

**Status for this repo**: not yet added — a personal shop tool, wide latitude per the guidance above. Good
candidate once the PyQt rewrite lands (e.g. an obscure input value alarm-out easter egg, matching the style
of the bar-puller macro this rule was inspired by).
