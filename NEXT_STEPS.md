# JobGarden

Goal: a UK-focused local job-search workspace for Lawrence that supports intake, evaluation, drafting, tracking, and public portfolio work without mixing private application material into the live site.

Current phase:

- portfolio site is live on `lozknowles.com`
- local CLI workflow exists for advert intake, application creation, and submission tracking
- one live target-sector role has been run through the workflow as a validation check

What we learned from the first live validation:

1. Saved advert import is valuable, especially for HTML job pages.
2. Supporting-statement prompts are more useful when generated directly inside `evaluation.md`.
3. Real adverts quickly expose metadata issues like location, channel, and geography assumptions.

Next step:

1. Validate the workflow on a genuinely UK-based role.
2. Review whether `job_search_tracker.csv` needs extra fields for UK applications.
3. Decide whether to add AI-assisted drafting hooks to `jobgarden_cli.py`.
4. Review CV and cover-letter templates against the target roles.
