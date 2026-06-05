# Job Application Assistant

**name:** job-application-assistant
**description:** Assists with job applications by evaluating job postings, tailoring CVs, writing cover letters or supporting statements, and preparing for interviews.
**allowed-tools:** Read, Glob, Grep, WebFetch, WebSearch, Edit, Write, AskUserQuestion

---

## Workflow

When the user provides a job posting (URL or text), follow the current workflow in [WORKFLOW.md](/fast/repos/JobGarden/WORKFLOW.md).

Use the reference files in this folder for:

| File | Purpose |
|------|---------|
| `01-candidate-profile.md` | Education, experience, skills, publications, awards |
| `02-behavioral-profile.md` | Behavioural assessment, strengths, ideal environments |
| `03-writing-style.md` | Tone, structure, do's and don'ts |
| `04-job-evaluation.md` | Scoring framework for job fit |
| `05-cv-templates.md` | LaTeX CV structure and tailoring rules |
| `06-cover-letter-templates.md` | LaTeX cover letter structure and tailoring rules |
| `07-interview-prep.md` | STAR examples, tough questions, roleplay guidelines |

This folder is now the reusable reference layer. The active workflow lives in `WORKFLOW.md`.
