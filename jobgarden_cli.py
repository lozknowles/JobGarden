#!/usr/bin/env python3
"""
Local CLI for JobGarden's UK-focused search and submission workflow.

This tool is intentionally lightweight and stdlib-only. It helps turn a pasted
or saved job advert into a structured application workspace and keeps the
central tracker up to date when an application is submitted.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
APPLICATIONS_DIR = ROOT / "documents" / "applications"
TRACKER_FILE = ROOT / "job_search_tracker.csv"


TRACKER_FIELDS = [
    "date",
    "company",
    "sector",
    "role",
    "role_type",
    "channel",
    "status",
    "contact_person",
    "fit_rating",
    "notes",
    "cv_file",
    "cover_letter_file",
    "source",
]


TECHNICAL_KEYWORDS = {
    "hr software": 10,
    "hris": 10,
    "hcm": 8,
    "payroll": 10,
    "saas": 8,
    "product": 8,
    "product strategy": 10,
    "roadmap": 8,
    "implementation": 9,
    "assurance": 9,
    "audit": 8,
    "stakeholder": 7,
    "enterprise": 7,
    "cloud": 6,
    "azure": 6,
}

EXPERIENCE_KEYWORDS = {
    "leadership": 10,
    "director": 9,
    "senior": 8,
    "customer": 7,
    "commercial": 7,
    "delivery": 8,
    "transformation": 7,
    "implementation": 9,
    "product manager": 9,
    "programme": 6,
    "program": 6,
    "board": 6,
    "strategy": 8,
}

BEHAVIOURAL_KEYWORDS = {
    "collaborative": 8,
    "communication": 8,
    "stakeholder": 8,
    "influence": 8,
    "trusted adviser": 10,
    "advisory": 10,
    "relationship": 6,
    "partner": 6,
    "customer-focused": 7,
    "customer focused": 7,
    "leadership": 7,
}

ALIGNMENT_KEYWORDS = {
    "hr": 10,
    "people": 6,
    "payroll": 10,
    "product": 10,
    "software": 7,
    "saas": 8,
    "implementation": 9,
    "assurance": 9,
    "advisory": 8,
    "audit": 7,
}

ROLE_TYPE_HINTS = {
    "contract": "contract",
    "interim": "contract",
    "freelance": "contract",
    "permanent": "permanent",
    "full time": "permanent",
    "part time": "part-time",
    "part-time": "part-time",
}

SECTOR_HINTS = {
    "hr": "HR software",
    "people": "HR software",
    "payroll": "Payroll / HR software",
    "saas": "SaaS",
    "software": "Software",
    "public sector": "Public sector",
}


@dataclass
class Evaluation:
    technical: int
    experience: int
    behavioural: int
    alignment: int
    logistics: str
    overall: int
    verdict: str
    strengths: list[str]
    gaps: list[str]
    notes: list[str]


def normalise_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:80] or "job"


def read_job_text(args: argparse.Namespace) -> str:
    if args.job_ad_file:
        return Path(args.job_ad_file).read_text(encoding="utf-8").strip()
    if args.job_ad_text:
        return args.job_ad_text.strip()
    raise SystemExit("Provide either --job-ad-file or --job-ad-text.")


def keyword_score(text: str, keywords: dict[str, int], floor: int = 20) -> int:
    haystack = text.lower()
    score = floor
    for phrase, weight in keywords.items():
        if phrase in haystack:
            score += weight
    return max(0, min(score, 100))


def infer_role_type(text: str) -> str:
    lowered = text.lower()
    for phrase, role_type in ROLE_TYPE_HINTS.items():
        if phrase in lowered:
            return role_type
    return "unknown"


def infer_sector(text: str) -> str:
    lowered = text.lower()
    for phrase, sector in SECTOR_HINTS.items():
        if phrase in lowered:
            return sector
    return "Unknown"


def logistics_status(text: str, location: str | None) -> tuple[str, list[str]]:
    lowered = text.lower()
    notes: list[str] = []

    if "visa" in lowered or "sponsorship" in lowered:
        return "FLAG", ["Check right-to-work wording and whether sponsorship is expected."]

    if "remote" in lowered:
        notes.append("Remote wording appears in the advert.")
    if "hybrid" in lowered:
        notes.append("Hybrid working is mentioned.")
    if location:
        notes.append(f"Role location captured as {location}.")

    return "PASS", notes or ["No obvious logistics blocker found in the advert text."]


def verdict_for_score(score: int) -> str:
    if score >= 75:
        return "Strong Fit"
    if score >= 60:
        return "Good Fit"
    if score >= 45:
        return "Moderate Fit"
    if score >= 30:
        return "Weak Fit"
    return "Poor Fit"


def infer_strengths(job_text: str) -> list[str]:
    lowered = job_text.lower()
    strengths: list[str] = []

    if any(term in lowered for term in ("hr", "payroll", "people systems", "hris", "hcm")):
        strengths.append("Direct HR software and payroll domain relevance.")
    if any(term in lowered for term in ("product", "roadmap", "strategy")):
        strengths.append("Strong product strategy and roadmap alignment.")
    if any(term in lowered for term in ("implementation", "delivery", "programme", "program")):
        strengths.append("Credible implementation oversight and delivery leadership.")
    if any(term in lowered for term in ("stakeholder", "communication", "influence")):
        strengths.append("Senior stakeholder leadership is a good match.")

    return strengths or ["Transferable leadership and commercial experience appear relevant."]


def infer_gaps(job_text: str) -> list[str]:
    lowered = job_text.lower()
    gaps: list[str] = []

    if any(term in lowered for term in ("hands-on coding", "software engineer", "developer")):
        gaps.append("Role may lean too far toward hands-on engineering delivery.")
    if "visa" in lowered or "sponsorship" in lowered:
        gaps.append("Confirm that the advert does not expect sponsorship needs.")
    if "travel" in lowered:
        gaps.append("Check the practical level of travel expected.")
    if "startup" in lowered:
        gaps.append("Test whether the culture and pace are the right fit.")

    return gaps or ["No major gap is obvious from the advert; validate through research and tailoring."]


def build_evaluation(job_text: str, location: str | None) -> Evaluation:
    technical = keyword_score(job_text, TECHNICAL_KEYWORDS)
    experience = keyword_score(job_text, EXPERIENCE_KEYWORDS)
    behavioural = keyword_score(job_text, BEHAVIOURAL_KEYWORDS)
    alignment = keyword_score(job_text, ALIGNMENT_KEYWORDS)
    logistics, logistics_notes = logistics_status(job_text, location)

    overall = round(
        technical * 0.30
        + experience * 0.25
        + behavioural * 0.15
        + alignment * 0.30
    )

    return Evaluation(
        technical=technical,
        experience=experience,
        behavioural=behavioural,
        alignment=alignment,
        logistics=logistics,
        overall=overall,
        verdict=verdict_for_score(overall),
        strengths=infer_strengths(job_text),
        gaps=infer_gaps(job_text),
        notes=logistics_notes,
    )


def ensure_tracker() -> None:
    if TRACKER_FILE.exists():
        return
    with TRACKER_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACKER_FIELDS)
        writer.writeheader()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def render_evaluation_markdown(
    company: str,
    role: str,
    evaluation: Evaluation,
    metadata: dict,
) -> str:
    strengths = "\n".join(f"- {item}" for item in evaluation.strengths)
    gaps = "\n".join(f"- {item}" for item in evaluation.gaps)
    notes = "\n".join(f"- {item}" for item in evaluation.notes)

    return f"""# Job Fit Evaluation: {role} at {company}

## Snapshot

| Dimension | Score | Notes |
|---|---:|---|
| Technical Skills | {evaluation.technical}/100 | Match driven from advert keyword overlap and known profile strengths. |
| Experience Match | {evaluation.experience}/100 | Estimated from leadership, delivery, product, and implementation signals. |
| Behavioural Fit | {evaluation.behavioural}/100 | Based on advisory, stakeholder, and communication language. |
| Location / Right to Work | {evaluation.logistics} | {' '.join(evaluation.notes)} |
| Career Alignment | {evaluation.alignment}/100 | Estimated from HR software, product, SaaS, and assurance signals. |

**Overall Score:** {evaluation.overall}/100

**Verdict:** {evaluation.verdict}

## Key Strengths
{strengths}

## Gaps To Check
{gaps}

## Logistics Notes
{notes}

## Role Metadata
- Company: {company}
- Role: {role}
- Channel: {metadata.get('channel', 'unknown')}
- Source: {metadata.get('source', '')}
- Location: {metadata.get('location', '')}
- Created: {metadata.get('created_at', '')}

## Tailoring Checklist
- [ ] Confirm the job is worth pursuing after reading the advert closely
- [ ] Compare against `.claude/skills/job-application-assistant/04-job-evaluation.md`
- [ ] Tailor CV toward the strongest matching themes
- [ ] Draft a cover letter or supporting statement with evidence only
- [ ] Record the final submission in `job_search_tracker.csv`
"""


def render_submission_markdown(metadata: dict, app_slug: str) -> str:
    return f"""# Submission Notes

## Role
- Company: {metadata['company']}
- Role: {metadata['role']}
- Application ID: {app_slug}

## Before Sending
- [ ] Final CV selected
- [ ] Cover letter or supporting statement selected
- [ ] Dates, names, and claims checked
- [ ] British English spelling checked
- [ ] Submission channel confirmed

## Submission Record
- Date sent:
- Status:
- CV file:
- Cover letter / statement file:
- Contact person:
- Notes:
"""


def create_application(args: argparse.Namespace) -> int:
    job_text = read_job_text(args)
    created = date.today().isoformat()
    app_slug = f"{created}-{slugify(args.company)}-{slugify(args.role)}"
    app_dir = APPLICATIONS_DIR / app_slug

    if app_dir.exists():
        raise SystemExit(f"Application directory already exists: {app_dir}")

    app_dir.mkdir(parents=True, exist_ok=False)
    evaluation = build_evaluation(job_text, args.location)

    metadata = {
        "application_id": app_slug,
        "company": normalise_whitespace(args.company),
        "role": normalise_whitespace(args.role),
        "channel": normalise_whitespace(args.channel or "unknown"),
        "source": args.source or "",
        "location": args.location or "",
        "role_type": args.role_type or infer_role_type(job_text),
        "sector": args.sector or infer_sector(job_text),
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "draft",
        "fit_rating": evaluation.verdict,
    }

    write_json(app_dir / "application.json", metadata)
    (app_dir / "evaluation.md").write_text(
        render_evaluation_markdown(metadata["company"], metadata["role"], evaluation, metadata),
        encoding="utf-8",
    )
    (app_dir / "submission.md").write_text(
        render_submission_markdown(metadata, app_slug),
        encoding="utf-8",
    )

    if args.job_ad_file:
        source_path = Path(args.job_ad_file)
        target = app_dir / f"job_ad{source_path.suffix or '.txt'}"
        shutil.copyfile(source_path, target)
    else:
        (app_dir / "job_ad.txt").write_text(job_text + "\n", encoding="utf-8")

    print(app_dir)
    print(f"Overall fit: {evaluation.overall}/100 ({evaluation.verdict})")
    return 0


def load_application_dir(path_arg: str) -> tuple[Path, dict]:
    app_dir = Path(path_arg)
    if not app_dir.exists():
        raise SystemExit(f"Application directory not found: {app_dir}")

    metadata_file = app_dir / "application.json"
    if not metadata_file.exists():
        raise SystemExit(f"Missing application.json in {app_dir}")

    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    return app_dir, metadata


def tracker_rows() -> list[dict[str, str]]:
    if not TRACKER_FILE.exists():
        return []
    with TRACKER_FILE.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_tracker(rows: Iterable[dict[str, str]]) -> None:
    ensure_tracker()
    with TRACKER_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACKER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def submit_application(args: argparse.Namespace) -> int:
    app_dir, metadata = load_application_dir(args.application_dir)
    ensure_tracker()

    rows = tracker_rows()
    application_key = str(app_dir.relative_to(ROOT))
    rows = [
        row for row in rows
        if row.get("source") != application_key
    ]

    row = {
        "date": args.date or date.today().isoformat(),
        "company": metadata.get("company", ""),
        "sector": metadata.get("sector", ""),
        "role": metadata.get("role", ""),
        "role_type": metadata.get("role_type", ""),
        "channel": args.channel or metadata.get("channel", ""),
        "status": args.status,
        "contact_person": args.contact_person or "",
        "fit_rating": metadata.get("fit_rating", ""),
        "notes": args.notes or "",
        "cv_file": args.cv_file or "",
        "cover_letter_file": args.cover_letter_file or "",
        "source": application_key,
    }
    rows.append(row)
    write_tracker(rows)

    metadata["status"] = args.status
    write_json(app_dir / "application.json", metadata)
    print(f"Recorded submission for {metadata.get('company')} - {metadata.get('role')}")
    return 0


def list_applications(args: argparse.Namespace) -> int:
    rows = tracker_rows()
    if args.status:
        rows = [row for row in rows if row.get("status", "").lower() == args.status.lower()]

    if not rows:
        print("No tracked applications found.")
        return 0

    for row in rows:
        print(
            f"{row['date']} | {row['company']} | {row['role']} | "
            f"{row['status']} | {row['fit_rating']}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="JobGarden search and submission CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="Create an application workspace from a job advert",
    )
    create_parser.add_argument("--company", required=True, help="Company name")
    create_parser.add_argument("--role", required=True, help="Role title")
    create_parser.add_argument("--channel", help="Where the role was found")
    create_parser.add_argument("--source", help="Source URL or note")
    create_parser.add_argument("--location", help="Role location")
    create_parser.add_argument("--sector", help="Override the inferred sector")
    create_parser.add_argument("--role-type", help="Override the inferred role type")
    create_parser.add_argument("--job-ad-file", help="Path to a saved job advert")
    create_parser.add_argument("--job-ad-text", help="Job advert text")
    create_parser.set_defaults(func=create_application)

    submit_parser = subparsers.add_parser(
        "submit",
        help="Record a sent application in the tracker",
    )
    submit_parser.add_argument("--application-dir", required=True, help="Application folder path")
    submit_parser.add_argument("--status", default="submitted", help="Submission status")
    submit_parser.add_argument("--channel", help="Submission channel override")
    submit_parser.add_argument("--date", help="Submission date YYYY-MM-DD")
    submit_parser.add_argument("--contact-person", help="Hiring contact")
    submit_parser.add_argument("--cv-file", help="CV file used")
    submit_parser.add_argument("--cover-letter-file", help="Cover letter or statement file used")
    submit_parser.add_argument("--notes", help="Tracker notes")
    submit_parser.set_defaults(func=submit_application)

    list_parser = subparsers.add_parser(
        "list",
        help="List tracked applications",
    )
    list_parser.add_argument("--status", help="Filter by tracker status")
    list_parser.set_defaults(func=list_applications)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
