# JobGarden

JobGarden is a UK-focused AI job-search workspace for Lawrence. It helps turn real career evidence into tailored job applications, interview prep, and learning plans.

## What this is

This repository keeps the useful parts of the original job-search system:

- a structured candidate profile
- job-fit evaluation before drafting
- tailored CV and supporting documents
- interview preparation
- application tracking
- skill-gap and upskilling notes

The workflow is designed for Codex and for UK applications. It prefers pasted or manually collected job ads first, then uses the profile and templates to draft the right documents.

## Typical workflow

1. Gather source material in `documents/`
2. Update the candidate profile and evaluation notes
3. Create a job workspace from a saved or pasted job ad
4. Review the generated fit evaluation and decide whether it is a sensible fit
5. Draft a UK-appropriate CV and cover letter or supporting statement
6. Track the application and capture the outcome
6. Feed the result back into the profile and learning plan

## Getting started

### 1. Read the guidance docs

- [PROJECT_MAP.md](/fast/repos/JobGarden/PROJECT_MAP.md)
- [AGENTS.md](/fast/repos/JobGarden/AGENTS.md)
- [DECISIONS_LOG.md](/fast/repos/JobGarden/DECISIONS_LOG.md)
- [WORKFLOW.md](/fast/repos/JobGarden/WORKFLOW.md)

### 2. Add your source documents

Place your CV, LinkedIn export, diplomas, references, and past applications in `documents/`.

See [documents/README.md](/fast/repos/JobGarden/documents/README.md) for the expected layout.

### 3. Review the templates

- `cv/main_example.tex` for the CV structure
- `cover_letters/cover.cls` for the cover-letter template
- `.claude/skills/job-application-assistant/` for the reusable evaluation and writing guidance

### 4. Use the CLI workflow

Import a saved advert first:

```bash
python3 jobgarden_cli.py import \
  --input-file /path/to/saved-job.html \
  --create
```

Create an application workspace from a job advert:

```bash
python3 jobgarden_cli.py create \
  --company "Example HR Ltd" \
  --role "Product Manager" \
  --channel "LinkedIn" \
  --source "https://example.com/jobs/123" \
  --job-ad-file /path/to/job-ad.txt
```

Record a submission in the tracker:

```bash
python3 jobgarden_cli.py submit \
  --application-dir documents/applications/2026-06-05-example-hr-ltd-product-manager \
  --status submitted \
  --cv-file cv/output/example-cv.pdf \
  --cover-letter-file documents/applications/.../cover-letter.pdf
```

List tracked applications:

```bash
python3 jobgarden_cli.py list
```

## Repository layout

| Path | Purpose |
|---|---|
| `PROJECT_MAP.md` | Folder-by-folder migration guide |
| `AGENTS.md` | Operating rules for Codex agents |
| `DECISIONS_LOG.md` | Durable workflow decisions and lessons learned |
| `WORKFLOW.md` | Current job-application workflow |
| `README.md` | Entry point and repo overview |
| `SETUP.md` | Environment and source-document setup |
| `CLAUDE.md` | Legacy transition note |
| `cv/` | LaTeX CV template and examples |
| `cover_letters/` | LaTeX cover-letter template and fonts |
| `documents/` | Candidate source documents and past applications |
| `.claude/` | Legacy workflow commands and guidance, still useful as reference |
| `.agents/` | Legacy job-board tooling, mostly Danish and likely to be replaced |
| `job_search_tracker.csv` | Application tracker |
| `jobgarden_cli.py` | Local CLI for creating job workspaces and recording submissions |
| `upskill/` | Saved learning plans and gap reports |
| `tools/` | Supporting utilities, including salary conversion |
| `salary_lookup.py` | Optional salary benchmarking helper |

## Notes

- Use British English in new content.
- Prefer manual job ads or UK-friendly sources over region-specific scrapers.
- Saved HTML adverts, recruiter notes, and imported intake files stay out of Git by default.
- Keep claims grounded in the documents and tracker, not in guesswork.
- If a job asks for a supporting statement rather than a cover letter, use the same evidence-first approach and adapt the format.

## License

MIT
