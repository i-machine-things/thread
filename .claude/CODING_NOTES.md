# Coding Best Practices & Reminders

> **Style rule:** Notes must be clear and concise — 300 characters or less each. Group by topic, not by date. Whenever a PR review (CodeRabbit or human) catches a mistake, add or amend a note here right away so it isn't repeated.

## Findings from initial dev-standards sync (2026-08-12)

- Original `tkTHREAD.py` had `import Sys` (capital S) at module level — not a real module, would `ModuleNotFoundError` on any run from source. Removed; nothing in the file used it.
- ~20 module-level globals (`units = None`, `pitch = None`, etc.) were dead — `generate_code()` set same-named locals without `global`, so the module-level ones were never read or written. Removed entirely rather than wiring up `global` — they served no purpose even shadowed correctly.
- Lesson: when a variable is assigned inside a function but never declared `global` there, treat the module-level "initializer" as suspect — grep for real reads/writes before assuming it's load-bearing.

## Repo structure

- Renamed `tkTHREAD.py`/`tkTHREAD.spec`/`tkthread.ui` → `main.py`/`main.spec`/`main.ui` for consistency with other repos in this org. `TkthreadApp` class name intentionally left as-is (file rename only, not an identifier rename).
- `dist/` (PyInstaller build output) and `output/` (generated `.nc` G-code files) are gitignored, not tracked — ship binaries as GitHub Release assets instead of committing them.
- `main.ui` (pygubu-designer source) is kept even though nothing loads it at runtime — it's the editable GUI design source, not dead code.
