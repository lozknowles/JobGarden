# JobGarden

Goal: a UK-focused local job-search workspace for Lawrence that supports intake, ranking, tailored CV and cover-letter drafting, tracking, interview prep, and public portfolio work without mixing private application material into the live site.

Current phase:

- portfolio site is live on `lozknowles.com`
- local CLI workflow exists for advert intake, application creation, and submission tracking
- application intelligence guidance now exists for ATS and form learning
- one live target-sector role has been run through the workflow as a validation check

First MVP scope:

1. monitor job sources
2. rank opportunities
3. reject poor matches
4. generate a tailored CV and cover letter
5. update an application tracker
6. prepare interview questions

What we learned from the first live validation:

1. Saved advert import is valuable, especially for HTML job pages.
2. Supporting-statement prompts are more useful when generated directly inside `evaluation.md`.
3. Real adverts quickly expose metadata issues like location, channel, and geography assumptions.
4. Advert analysis alone is not enough; real application forms need their own learning loop.

Next step:

1. Validate the workflow on a genuinely UK-based role.
2. Add explicit draft scaffolds for tailored CVs and tailored cover letters.
3. Add interview-question preparation based on the advert and fit evaluation.
4. Keep `job_search_tracker.csv` focused on MVP value first.
5. Treat ATS form capture and form-fill as later-phase work.
6. Keep the `lozknowles.com` main page focused while the 3D orbit carousel and build-system experiments live on the new Technology Research page.
7. Keep `DECISIONS_LOG.md` updated whenever workflow defaults change.
8. Review the refreshed portfolio page for spacing, motion feel, carousel interaction, and any copy tweaks before a live deployment.
