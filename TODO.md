# TODO

## Immediate

- [ ] Decide whether `CLAUDE.md` stays as a transitional note or becomes a Codex-oriented `WORKFLOW.md`.
- [ ] Replace Claude-specific references in repo docs with Codex wording where user-facing.
- [ ] Audit `.claude/` and `.agents/` to separate reusable ideas from legacy Claude-only wiring.

## UK Workflow Migration

- [x] Replace Danish job-board search logic with UK sources or a manual pasted-job-ad workflow.
- [ ] Update the job-evaluation guidance for UK application norms, including supporting statements and CV expectations.
- [ ] Check the application tracker fields against the way UK applications are actually managed.
- [ ] Confirm the CV and cover-letter templates still fit UK conventions and target roles.
- [x] Create a simple portfolio page on `lozknowles.com` that highlights HR software leadership, implementation assurance, and selected projects.

## Clean-up

- [ ] Review `cover_letters/OpenFonts/cover.cls` and remove or relocate it if it is just a duplicate.
- [ ] Decide whether `claude_animation.gif` still has a purpose.
- [ ] Decide whether `salary_lookup.py` should stay optional or be updated with UK salary data.

## Validation

- [ ] Run one end-to-end UK application through the updated CLI workflow.
- [ ] Record what worked and what felt clunky.
- [ ] Update `PROJECT_MAP.md` and the workflow docs after the first real test.

## Coding

- [x] Add a local CLI to create application workspaces from pasted or saved job adverts.
- [x] Add a local CLI command to record submissions into `job_search_tracker.csv`.
- [ ] Add a UK job-source intake helper for saved adverts from LinkedIn, company sites, and recruiters.
- [ ] Decide whether to extend the CLI with AI-assisted drafting hooks or keep drafting agent-led.
