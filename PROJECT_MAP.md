# Project Map

This repository is a job-search workspace that started as a Claude Code project and is now being adapted for a UK Codex workflow. The core idea is still strong:

- keep a structured candidate profile
- evaluate each job before applying
- generate tailored CV and application documents
- track outcomes and learning

The main migration work is to remove Claude-specific wiring, replace Danish job-board automation with UK/manual application intake, and keep the reusable LaTeX, tracker, and profiling pieces.

## Folder Map

| Path | What it does | Claude-specific? | Keep? | Remove or replace for UK Codex workflow? |
|---|---|---:|---:|---|
| `CLAUDE.md` | Transitional repo note describing the UK direction and current priorities | Yes, by name and by framing | Keep the content as migration guidance for now | Rename or replace with a Codex-oriented `WORKFLOW.md` or `PROFILE.md`; remove Claude branding once the migration is stable |
| `README.md` | High-level project overview and legacy Claude-oriented usage instructions | Yes, heavily | Keep the project description and structure | Rewrite for UK Codex usage, manual job-ad intake, and British spelling |
| `PROJECT_ARCHITECTURE.md` | Development, hosting, deployment, and portfolio-site policy for the repo | No | Yes | Keep as the authoritative reference for live-site and infrastructure decisions |
| `SETUP.md` | Setup instructions for the legacy workflow | Partly | Keep the installation and LaTeX guidance | Replace Claude-specific startup instructions and any Denmark-specific tooling |
| `.claude/` | Claude Code commands, skills, and agent instructions | Yes | Keep the ideas and content only if they are still useful | Move the useful parts into Codex-friendly docs or prompts; retire the Claude command layer |
| `.claude/settings.local.json` | Claude Code permissions/settings | Yes | Usually no | Remove or archive for Codex workflow |
| `.claude/commands/` | `/setup`, `/apply`, `/expand`, `/reset` command flows for Claude Code | Yes | Keep the workflow logic as reference | Re-express as Codex instructions, task docs, or scripts; remove slash-command dependency |
| `.claude/skills/job-application-assistant/` | Candidate profile, behavioural profile, writing style, evaluation framework, CV and cover-letter guidance, interview prep | Yes by location, but the content is broadly reusable | Yes | Move the reusable content into a neutral location and update references from Claude to Codex |
| `.claude/skills/job-scraper/` | Job-search skill built around Danish search strategy | Yes and Denmark-specific | Keep the pattern, not the implementation | Replace with UK/manual job sourcing and UK boards; `search-queries.md` should be created or replaced as part of that work |
| `.claude/skills/upskill/` | Skill-gap analysis and learning-plan workflow | Mostly no | Yes | Keep, but adjust source lists and examples to UK roles and current Codex instructions |
| `.claude/agents/` | Extra Claude agent instructions, e.g. research helper | Yes | Maybe | Replace with Codex-native guidance or remove if not needed |
| `.agents/skills/` | Legacy search skills for Danish job boards and portal CLIs | Yes, and strongly Denmark-specific | Low priority | Replace with UK-targeted sources or a manual-application workflow; remove the Danish portal assumptions |
| `.agents/skills/*/cli/` | Bun-based command-line scrapers for specific Danish job boards | Yes and region-specific | Low priority | Remove or fully rewrite for UK sources, or drop entirely if manual ad intake is enough |
| `.serena/` | Serena workspace configuration and memories | Not Claude-specific | Optional | Keep only if Serena is still part of the toolchain; otherwise archive later |
| `cv/` | LaTeX CV template and sample | No | Yes | Keep, then tailor content and styling for UK applications |
| `cover_letters/` | Cover-letter LaTeX template and embedded fonts | No | Yes | Keep the template, but check for duplicate or misplaced files before migration |
| `cover_letters/OpenFonts/cover.cls` | Duplicate copy of the cover-letter class file sitting inside the font directory | No, but it looks accidental | Probably not | Remove or relocate this duplicate, because `OpenFonts/` should hold fonts only |
| `documents/` | User-supplied source documents for profile building and application history | No | Yes | Keep, but make sure it supports UK materials and not just the old workflow assumptions |
| `documents/applications/` | Past application folders with job ad, CV draft, cover letter, outcome | No | Yes | Keep and use as the evidence base for what works in the UK market |
| `documents/cv/` | Master CV sources | No | Yes | Keep |
| `documents/linkedin/` | LinkedIn export sources | No | Yes | Keep |
| `documents/diplomas/` | Diplomas, transcripts, official education evidence | No | Yes | Keep |
| `documents/references/` | Reference letters | No | Yes | Keep |
| `job_scraper/` | Runtime state for scraper output and deduplication | No | Maybe | Keep if any scraper remains; otherwise replace with a lightweight manual-search tracker |
| `job_search_tracker.csv` | Main application tracker | No | Yes | Keep, but consider widening the fields to better fit UK applications |
| `tools/` | Supporting utilities such as salary conversion | Mostly no | Yes | Keep the useful tools; reframe them for UK use and current data sources |
| `salary_lookup.py` | Salary benchmarking helper | No | Yes | Keep if you can feed it UK salary data; otherwise make it optional by default |
| `tools/convert_salary_excel.py` | Converts salary spreadsheets into the JSON used by the lookup tool | No | Yes | Keep if salary benchmarking remains useful |
| `portfolio/` | Public static portfolio page for `lozknowles.com` | No | Yes | Keep public-only content here and deploy it separately from private application material |
| `upskill/` | Saved learning plans and gap reports | No | Yes | Keep |
| `claude_animation.gif` | Branding image for the original Claude-based workflow | Yes | Low priority | Remove or replace with neutral project branding |

## What Is Claude-Specific

These parts are clearly tied to Claude and should be treated as legacy migration targets:

- `.claude/`
- `.claude/settings.local.json`
- `.claude/commands/`
- `.claude/skills/`
- `.claude/agents/`
- `CLAUDE.md`
- `claude_animation.gif`
- any file content that says “Claude Code” or assumes slash-command usage

## What We Should Keep

Keep the reusable parts that already solve the real problem:

- the candidate profile structure
- the behavioural profile structure
- the CV and cover-letter LaTeX templates
- the job evaluation framework
- the interview-prep framework
- the application tracker
- the documents folder
- salary benchmarking if you have UK salary data to feed it
- the upskill gap-analysis workflow

## What We Should Remove or Replace for UK Codex

Replace these first:

1. Claude branding and command syntax
2. Danish job-board integrations and scraper assumptions
3. Any workflow that depends on Claude-specific permissions or slash commands
4. Any search logic that assumes Danish portals instead of UK job sources
5. Any duplicate or misplaced template files, especially `cover_letters/OpenFonts/cover.cls`

## Next 5 Practical Steps

1. Freeze the current reusable structure and decide which Claude-era files will stay only as reference.
2. Move the useful profile, evaluation, writing, and interview logic into Codex-facing docs or prompts.
3. Replace Danish job-board search with a UK/manual application intake path.
4. Update the tracker and templates for UK application language, spelling, and hiring conventions.
5. Run one end-to-end test application and use the outcome to refine the workflow.
