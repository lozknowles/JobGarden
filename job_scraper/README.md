# Job Intake

`job_scraper/` is now a UK-friendly intake area rather than an active region-specific scraper.

## Current approach

Use saved adverts or pasted text from:

- LinkedIn jobs
- company careers sites
- recruiter emails
- job boards with UK-relevant roles

Then create a structured workspace with:

```bash
python3 jobgarden_cli.py import --input-file /path/to/saved-job.html --create
```

You can still use the direct path if you already have clean text:

```bash
python3 jobgarden_cli.py create --company "Company" --role "Role" --job-ad-file /path/to/job-ad.txt
```

## Why this is the default

- It keeps the workflow reliable when job boards change.
- It avoids brittle automation for now.
- It gives Codex and future agents a stable input format.

## Future option

If needed, this folder can later hold:

- import helpers for saved HTML or text adverts
- source-specific parsers
- optional UK board connectors

For now, treat manual or semi-manual intake as the supported path.
