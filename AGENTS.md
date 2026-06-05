# AGENTS.md

This repository is a UK-focused job-search workspace for Codex agents.

## Working Principles

- Read `PROJECT_MAP.md` first when you need to understand the repo.
- Use the existing source documents as the ground truth, not assumptions.
- Prefer British English spelling and UK hiring conventions in new content.
- Keep edits narrow and targeted. Do not rewrite large files unless the task truly needs it.
- Preserve user-written content. If something looks unexpected, assume it may be intentional and check before changing it.
- Use `apply_patch` for file edits.

## What to Treat as Legacy

- `.claude/`
- `CLAUDE.md`
- any slash-command workflow
- the Danish job-board tooling in `.agents/skills/`

These files can still be useful as reference material, but they should not define the future workflow.

## Current Workflow Shape

1. Build or update the candidate profile from documents and past applications.
2. Evaluate each job against the profile before drafting anything.
3. Draft a UK-appropriate CV and supporting statement or cover letter.
4. Check that the document language matches the job ad and the role level.
5. Track the application and capture the outcome.
6. Feed lessons back into the profile, evaluation rules, and upskilling notes.

## Repository Conventions

- Keep the LaTeX templates in `cv/` and `cover_letters/` unless there is a strong reason to replace them.
- Keep `job_search_tracker.csv` as the central application record.
- Keep `documents/` as the source of truth for actual career evidence.
- Prefer manual pasted job ads or UK-friendly sources over region-specific scrapers.
- If you add new planning or workflow docs, make them neutral and Codex-friendly.

## Migration Notes

- Replace Claude references with Codex references where they are user-facing.
- Replace Danish search assumptions with UK job-source assumptions.
- Remove duplicate or accidental template files when you confirm they are not needed.
- Keep anything that helps with application quality, evidence tracking, or review.

