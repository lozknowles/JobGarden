# TODO

## Immediate

- [ ] Keep the first MVP tightly scoped to the 80/20 workflow.
- [ ] Decide whether `CLAUDE.md` stays as a transitional note or becomes a Codex-oriented `WORKFLOW.md`.
- [ ] Replace Claude-specific references in repo docs with Codex wording where user-facing.
- [ ] Audit `.claude/` and `.agents/` to separate reusable ideas from legacy Claude-only wiring.

## MVP Scope

- [ ] Monitor job sources
- [ ] Rank opportunities
- [ ] Reject poor matches
- [x] Generate a tailored CV
- [x] Generate a tailored cover letter
- [ ] Update an application tracker
- [x] Prepare interview questions

## UK Workflow Migration

- [x] Replace Danish job-board search logic with UK sources or a manual pasted-job-ad workflow.
- [x] Update the job-evaluation guidance for UK application norms, including supporting statements and CV expectations.
- [x] Check the application tracker fields against the way UK applications are actually managed.
- [ ] Confirm the CV and cover-letter templates still fit UK conventions and target roles.
- [x] Create a simple portfolio page on `lozknowles.com` that highlights HR software leadership, implementation assurance, and selected projects.

## Clean-up

- [ ] Review `cover_letters/OpenFonts/cover.cls` and remove or relocate it if it is just a duplicate.
- [ ] Decide whether `claude_animation.gif` still has a purpose.
- [ ] Decide whether `salary_lookup.py` should stay optional or be updated with UK salary data.

## Validation

- [x] Run one end-to-end live role through the updated CLI workflow and review the generated evaluation wording.
- [ ] Repeat the validation on a UK-located role, not just a target-sector live role.
- [x] Record what worked and what felt clunky.
- [ ] Update `PROJECT_MAP.md` and the workflow docs after the first real test.
- [ ] Validate the workflow against a real ATS application form, not just the advert.
- [ ] Replace the portfolio carousel's temporary YouTube/GitHub links with the real project URLs from the next turn.

## Coding

- [x] Add a local CLI to create application workspaces from pasted or saved job adverts.
- [x] Add a local CLI command to record submissions into `job_search_tracker.csv`.
- [x] Add a UK job-source intake helper for saved adverts from LinkedIn, company sites, and recruiters.
- [x] Add stronger UK supporting-statement prompts to the generated evaluation output.
- [x] Add explicit draft scaffolds for a tailored CV and tailored cover letter per application.
- [x] Add interview-question generation based on the role and evaluation.
- [ ] Add a private form-capture structure for ATS questions, steps, and observations.
- [x] Add an ATS/vendor observation model so repeated platform patterns can be learned over time.
- [x] Add a `form-review` step or command before any future `form-fill` automation.
- [ ] Decide whether to extend the CLI with AI-assisted drafting hooks or keep drafting agent-led.

## Later Phase

- [ ] Add a private form-capture workflow for ATS questions, steps, and observations.
- [ ] Add machine-readable form-capture data alongside markdown notes.
- [ ] Add ATS pattern summaries across captured forms.
- [ ] Add `form-fill` support when computer use is available.
- [ ] Add submit automation only after review and fill steps are stable.
