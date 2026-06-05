# AGENTS.md

This repository is a UK-focused job-search workspace for Codex agents.

Before making infrastructure, deployment, credential, GitHub, or portfolio-site changes, read `PROJECT_ARCHITECTURE.md` as well as this file.

## Working Principles

- Read `PROJECT_MAP.md` first when you need to understand the repo.
- Read `PROJECT_ARCHITECTURE.md` before any deployment or hosting changes.
- Read `DECISIONS_LOG.md` before changing workflow, intake, evaluation, or tracking behaviour.
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
3. Review the real application form when possible, not just the advert.
4. Draft a UK-appropriate CV and supporting statement or cover letter.
5. Check that the document language matches the job ad, the application form, and the role level.
6. Track the application and capture the outcome.
7. Feed lessons back into the profile, evaluation rules, ATS learning, and upskilling notes.

## Repository Conventions

- Keep the LaTeX templates in `cv/` and `cover_letters/` unless there is a strong reason to replace them.
- Keep `job_search_tracker.csv` as the central application record.
- Keep `documents/` as the source of truth for actual career evidence.
- Prefer manual pasted job ads or UK-friendly sources over region-specific scrapers.
- Treat ATS and application-form behaviour as first-class workflow inputs, not optional extras.
- If you add new planning or workflow docs, make them neutral and Codex-friendly.
- Treat `https://lozknowles.com` as a public portfolio site hosted on `cottageserver`.
- Keep public portfolio material separate from private application notes, tracker data, generated CVs, and statements of interest.
- Ask for confirmation before deploying anything to `cottageserver`.
- Update `DECISIONS_LOG.md` when a durable workflow decision changes.

## Portfolio Site

- The public portfolio page for this project lives at `https://lozknowles.com`.
- It is hosted on `cottageserver`, so deployment changes should follow the same careful process used for any other live site.
- Public portfolio content may include selected CV/profile highlights, project work, application-support tooling, public examples, and links to relevant projects.
- Never publish private job applications, personal profile notes, tracker data, generated CVs, or statements of interest without explicit approval.
- Update `NEXT_STEPS.md` after portfolio, infrastructure, or deployment changes.

## Migration Notes

- Replace Claude references with Codex references where they are user-facing.
- Replace Danish search assumptions with UK job-source assumptions.
- Remove duplicate or accidental template files when you confirm they are not needed.
- Keep anything that helps with application quality, evidence tracking, or review.
