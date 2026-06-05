# Setup Guide

This guide gets the JobGarden workspace ready for use.

## 1. Prerequisites

### Python

Python 3.10+ is recommended for the salary helper and any future scripting.

Check your version:

```bash
python --version
```

### LaTeX

Install a LaTeX distribution so the CV and cover-letter templates can be compiled to PDF.

- Windows: MiKTeX
- macOS: MacTeX
- Linux: TeX Live

The CV template expects `lualatex`. The cover-letter template expects `xelatex`.

### Optional: Bun

Only install Bun if you plan to keep using the legacy job-board tooling in `.agents/skills/`.

## 2. Clone the repository

```bash
git clone <your-fork-or-repo-url>
cd JobGarden
```

## 3. Review the workflow docs

Read these first:

- `PROJECT_MAP.md`
- `AGENTS.md`
- `WORKFLOW.md`

They explain what to keep, what to replace, and how the UK workflow should work.

## 4. Add your source material

Populate `documents/` with the following if you have them:

- `documents/cv/` for your master CV
- `documents/linkedin/` for a LinkedIn export
- `documents/diplomas/` for degree certificates or transcripts
- `documents/references/` for reference letters
- `documents/applications/` for past application folders

See `documents/README.md` for the folder layout.

## 5. Optional salary benchmarking

If you want salary benchmarking, create `salary_data.json` in the repo root or convert an Excel sheet with:

```bash
python tools/convert_salary_excel.py path/to/salary-data.xlsx --source "My Salary Data 2025"
```

This is optional. If you do not have salary data, skip it.

## 6. Compile the templates

```bash
cd cv && lualatex -interaction=nonstopmode main_example.tex
cd ../cover_letters && xelatex -interaction=nonstopmode cover_<company>_<role>.tex
```

The exact filenames will change when you generate a tailored application, but these commands confirm the toolchain is installed and ready.

## 7. Check the layout

When you generate a CV or cover letter:

- the CV should fit on two pages
- the cover letter should fit on one page
- the content should stay grounded in the evidence you provided

## Troubleshooting

- If the salary file is missing, skip the salary step.
- If LaTeX fails, confirm `lualatex` and `xelatex` are installed and on your path.
- If the fonts do not render correctly, check the files under `cover_letters/OpenFonts/fonts/`.
