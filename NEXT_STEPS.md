# JobGarden

Goal: a UK-focused local job-search workspace for Lawrence that supports intake, evaluation, drafting, tracking, and public portfolio work without mixing private application material into the live site.

Current phase:

- portfolio site is live on `lozknowles.com`
- local CLI workflow exists for advert intake, application creation, and submission tracking
- application intelligence guidance now exists for ATS and form learning
- one live target-sector role has been run through the workflow as a validation check

What we learned from the first live validation:

1. Saved advert import is valuable, especially for HTML job pages.
2. Supporting-statement prompts are more useful when generated directly inside `evaluation.md`.
3. Real adverts quickly expose metadata issues like location, channel, and geography assumptions.
4. Advert analysis alone is not enough; real application forms need their own learning loop.

Next step:

1. Validate the workflow on a genuinely UK-based role.
2. Add a private form-capture workflow for real ATS applications.
3. Review whether `job_search_tracker.csv` needs extra fields for UK applications and ATS observations.
4. Decide whether to add AI-assisted drafting hooks to `jobgarden_cli.py`.
5. Review CV and cover-letter templates against the target roles.
6. Keep `DECISIONS_LOG.md` updated whenever workflow defaults change.
