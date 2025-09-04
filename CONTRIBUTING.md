# Contributing to SoundSystemBasic

Thanks for your interest in contributing! This project aims to provide a lightweight Windows audio controller, with optional VoiceMeeter integration.

## Getting Started
- Prereqs: Windows 10/11, Python 3.11 recommended.
- Use a virtual env — do not install globally.
- Setup (PowerShell):
  - `py -3.11 -m venv .venv`
  - `.\\.venv\\Scripts\\Activate`
  - `pip install -r requirements.txt`

## Development Flow
- Branching:
  - Create a feature branch from `dev` (preferred) or `main` if `dev` doesn’t exist.
  - Naming: `feat/<short>`, `fix/<short>`, `chore/<short>`.
- Commits:
  - Keep messages concise; Conventional Commits style encouraged (e.g., `feat: add default device star`).
- Running locally:
  - Doctor: `python -m app.cli /doctor`
  - Init (files/folders): `python -m app.cli /init --no-install`
  - UI: `python -m app.ui_tk`
  - CLI helpers: `python -m app.cli win list|volume|mute|test-tone|set-default-*`
- Dependencies:
  - Pin in `requirements.txt` where possible.
  - Optional Stufe‑2 deps (e.g., `pyVoicemeeter`) can be added commented first, then un-commented when used.

## Code Style & Scope
- Python style: follow PEP 8 heuristically; keep modules small and focused.
- Avoid heavy frameworks; keep the app lightweight.
- Prefer native COM solutions; allow tool fallbacks only as optional.

## Pull Requests
- Include:
  - Summary (what/why)
  - Changes (bulleted)
  - Testing (CLI/UI steps, expected results)
  - Screenshots (if UI changes)
- Checklist (before opening):
  - [ ] Built and ran UI locally (`python -m app.ui_tk`)
  - [ ] `/doctor` passes
  - [ ] No stray debug prints, no secrets
  - [ ] Updated docs (README/README_DEV) if needed
- Small, focused PRs are easier to review.

## Releasing
- Tag stable milestones: `git tag -a v0.x.0 -m "Stage x: ..." && git push origin v0.x.0`.
- Attach short release notes summarizing key changes.

## Questions / Help
- Open an issue describing context, steps to reproduce (if a bug), and expected vs actual behavior. Include console output or screenshots where relevant.

