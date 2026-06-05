# Decisions Log

This file records durable workflow and product decisions for JobGarden.

Use it to avoid repeating experiments that already proved weak, misleading, or too brittle.

## How to use this file

- Add entries when a decision changes workflow, evaluation, intake, tracking, or deployment behaviour in a durable way.
- Record what was tried, what we learned, and what the current default is.
- Link future changes back to earlier entries when they revise or replace a decision.

---

## 2026-06-05: Manual and saved-advert intake is the default

### Context

The repo started with legacy assumptions about region-specific job-board automation.

### Decision

Default to saved or pasted job adverts, including saved HTML and recruiter notes, rather than brittle direct scraping.

### Why

- Job boards change too often.
- Saved adverts are easier to verify.
- Manual or semi-manual intake is more reliable for a private job-search workflow.
- It gives Codex a stable input format.

### Current implementation

- `python3 jobgarden_cli.py import --input-file ... --create`
- private intake copies live under `job_scraper/imports/`

### Do not repeat

- Do not assume a job-board search page is a stable ingestion surface.
- Do not prioritise scraper complexity before the intake and evaluation flow is strong.

---

## 2026-06-05: Role family matters as much as title

### Context

UK HR and payroll adverts often use overlapping language across product management, product marketing, functional analysis, implementation, and operations.

### Decision

Classify adverts by `role_family` as part of evaluation, instead of trusting the title alone.

### Why

- Many attractive titles are not really product-management roles.
- Lawrence is strongest in roles that blend product, delivery, implementation assurance, and senior stakeholder influence.
- Misclassifying a role leads to weak applications and bad fit decisions.

### Current implementation

Role families currently inferred:

- `product_management`
- `product_marketing`
- `functional_analyst`
- `implementation_assurance`
- `service_operations`

### Do not repeat

- Do not treat every “Product Manager” or “Product Owner” advert as the same shape of job.

---

## 2026-06-05: HR/payroll domain signals need heavier weighting

### Context

General PM scoring was not enough for Lawrence’s target market.

### Decision

Weight HR and payroll domain terms more heavily in fit evaluation.

### Why

- Domain credibility matters strongly in this market.
- Employers often want knowledge of HRIS, HCM, payroll, compliance, benefits, and service environments.
- Lawrence’s background is unusually strong here, so the workflow should surface that.

### Current implementation

Extra weighting now includes terms such as:

- `payroll`
- `hris`
- `hcm`
- `compliance`
- `benefits`
- `managed services`
- `integrations`

### Do not repeat

- Do not rely on generic PM keywords alone for role scoring.

---

## 2026-06-05: Supporting statements should lead with outcomes

### Context

UK roles often care less about broad responsibility lists and more about tangible business outcomes.

### Decision

Generated evaluations should include a `Business Outcomes To Lead With` section and role-specific supporting-statement prompts.

### Why

- This improves the quality of CV and statement tailoring.
- It makes applications more commercial and less generic.
- It better fits Lawrence’s background in product, implementation, and executive influence.

### Current implementation

Generated evaluation output now highlights outcome themes such as:

- customer value
- commercial growth
- operational efficiency
- delivery confidence
- compliance and control
- adoption and engagement
- data-led decisions

### Do not repeat

- Do not draft supporting statements around responsibilities alone when the advert is asking for outcomes.

---

## 2026-06-05: Real advert validation is mandatory

### Context

Synthetic examples looked fine until a live role exposed issues in channel detection, location parsing, and geography warnings.

### Decision

Validate workflow changes against real adverts before trusting them.

### Why

- Real adverts reveal edge cases quickly.
- This keeps the workflow honest.
- It prevents “works in theory” changes from hardening into the repo.

### Current implementation

- one live target-sector validation role was run through the import and evaluation flow
- findings were used to tighten metadata inference and warnings

### Do not repeat

- Do not mark intake or evaluation work “done” without testing on a live advert.
