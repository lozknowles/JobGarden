# Workflow

This is the current operating workflow for JobGarden.

## 1. Build the profile

Use the source material in `documents/` to keep the candidate profile grounded in evidence.

Useful sources:

- master CV
- LinkedIn export
- diplomas and transcripts
- reference letters
- past applications and outcomes

## 1a. Import the advert cleanly

If the role is saved as HTML, copied from LinkedIn, or forwarded from a recruiter, import it first.

Suggested command:

```bash
python3 jobgarden_cli.py import --input-file /path/to/saved-job.html --create
```

This keeps a cleaned plain-text version in `job_scraper/imports/` and can also create the application workspace immediately.

## 2. Evaluate the job first

Before drafting anything, create a job workspace and compare the job ad against the profile.

Suggested command:

```bash
python3 jobgarden_cli.py create --company "Company" --role "Role" --job-ad-file /path/to/job-ad.txt
```

This creates:

- an application folder under `documents/applications/`
- a saved copy of the advert
- `application.json`
- `evaluation.md`
- `submission.md`

The generated `evaluation.md` now includes:

- a first-pass fit score
- strengths and gaps
- logistics notes
- UK supporting-statement prompts
- a suggested supporting-statement structure

Check:

- skill match
- experience match
- behavioural fit
- location and logistics
- career alignment

If the role is a weak fit, say so early rather than forcing a generic application.

## 3. Draft the application

When the role is worth pursuing, draft:

- a UK-appropriate CV
- a cover letter or supporting statement
- interview notes and likely questions

Keep every claim tied to the source material.

## 4. Review and refine

Check the draft for:

- factual accuracy
- role-specific targeting
- tone and clarity
- UK spelling and conventions

If the role asks for a supporting statement, adapt the same evidence-first approach to that format instead of forcing a cover-letter shape.

## 5. Track the result

Record the application in `job_search_tracker.csv` and add notes about:

- what was submitted
- what the employer seemed to value
- what to improve next time

Suggested command:

```bash
python3 jobgarden_cli.py submit --application-dir documents/applications/<application-id>
```

## 6. Feed lessons back in

Use the outcome to update:

- the candidate profile
- the evaluation framework
- the interview prep notes
- the upskill plan
