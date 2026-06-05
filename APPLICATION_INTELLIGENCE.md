# Application Intelligence

This file defines how JobGarden should learn from real application forms, ATS workflows, and employer-specific questions over time.

It is not just about drafting better documents. It is about understanding how applications are actually filtered, scored, and progressed.

## Purpose

JobGarden should learn from:

- the advert itself
- the application form fields
- the screening questions
- the upload requirements
- any mandatory supporting statement prompts
- the ATS or vendor behaviour we can observe
- the eventual outcome

The goal is to build a feedback loop so future applications are better targeted and less wasteful.

## Scope

Application intelligence includes:

- what questions are repeatedly asked
- how different ATS platforms structure forms
- where employers ask knockout or gating questions
- what evidence is most often required
- what file formats and naming rules appear
- whether the workflow prefers CV-first, form-first, or supporting-statement-first applications
- whether a role is likely to be filtered by location, salary, notice period, or seniority

## What to capture

For each real application flow, capture as much of this as is practical:

### 1. Source and platform

- employer
- role
- source URL
- job board or direct employer site
- ATS vendor or platform, if identifiable

Examples:

- Workday
- Greenhouse
- Lever
- Taleo
- SuccessFactors
- Teamtailor
- SmartRecruiters
- Applied
- Jobtrain
- Recruitee
- Indeed-hosted flow
- custom employer form

### 2. Form structure

- number of steps
- whether account creation is required
- whether CV parsing is used
- whether LinkedIn import is offered
- whether there is a mandatory cover letter
- whether there is a mandatory supporting statement
- whether there are free-text competency questions
- whether there are equal opportunities or diversity sections

### 3. Screening and gating questions

Capture the exact question where possible, plus the likely purpose.

Common examples:

- right to work
- visa sponsorship
- location or commute
- salary expectations
- notice period
- years of experience
- payroll / HRIS / product domain experience
- management experience
- sector experience
- willingness to travel
- hybrid or remote expectations

### 4. Likely weighting or filtering signals

Record observed or inferred signals such as:

- knockout questions
- role-family mismatch
- seniority mismatch
- location mismatch
- mandatory domain experience
- required certifications or qualifications
- file-format constraints

### 5. Outcome

- submitted
- rejected
- progressed
- interview invited
- no response
- withdrawn

Record time-to-response where possible.

## Storage approach

Private operational captures should stay out of Git by default.

Recommended private working area:

- `job_scraper/forms/`

Use it for:

- copied question sets
- screenshots or manually typed field lists
- ATS observations
- per-role form notes

Durable, reusable lessons should then be summarised in:

- `DECISIONS_LOG.md`
- `TODO.md`
- workflow/code changes

## Learning loop

The intended loop is:

1. Import the advert
2. Evaluate the role
3. Inspect the real form
4. Capture the form questions and ATS characteristics
5. Tailor the CV and supporting statement to the advert and form
6. Complete or prepare the application
7. Record the outcome
8. Update the repo's scoring, prompts, and decisions

## Working rules

- Do not assume the advert contains everything needed for the application.
- Do not assume all Product Manager titles are equivalent.
- Do not assume ATS filters are neutral; capture patterns that look biased or overly simplistic.
- Do not submit an application unless the user explicitly wants to proceed for that role.
- Do summarise durable patterns in `DECISIONS_LOG.md` so they are not lost.

## Next implementation direction

Future JobGarden workflow should likely include explicit steps for:

- `form-review`
- `form-capture`
- `form-fill`
- `submit`

That would sit on top of the current intake and evaluation workflow, rather than replacing it.

## Current CLI support

Current supported commands now include:

- `python3 jobgarden_cli.py import ...`
- `python3 jobgarden_cli.py create ...`
- `python3 jobgarden_cli.py form-review --application-dir ...`
- `python3 jobgarden_cli.py submit ...`

`form-review` is the current bridge between advert analysis and any future form-fill automation.
