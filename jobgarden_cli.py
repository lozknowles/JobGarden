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
import html
import json
import re
import shutil
from dataclasses import dataclass
from datetime import UTC, date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
APPLICATIONS_DIR = ROOT / "documents" / "applications"
TRACKER_FILE = ROOT / "job_search_tracker.csv"
IMPORTS_DIR = ROOT / "job_scraper" / "imports"
FORMS_DIR = ROOT / "job_scraper" / "forms"


TRACKER_FIELDS = [
    "date",
    "company",
    "sector",
    "role",
    "role_family",
    "role_type",
    "channel",
    "ats_vendor",
    "application_form_type",
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
    "payroll bureau": 7,
    "payroll services": 7,
    "compliance": 9,
    "benefits": 8,
    "workforce management": 7,
    "time and attendance": 7,
    "people platform": 7,
    "managed services": 7,
    "integrations": 7,
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
    "go to market": 5,
    "gtm": 5,
    "functional": 5,
    "process improvement": 6,
    "service delivery": 7,
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
    "benefits": 8,
    "compliance": 8,
    "hr technology": 9,
    "hr tech": 9,
    "managed services": 7,
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
    "full-time": "permanent",
    "part time": "part-time",
    "part-time": "part-time",
}

SECTOR_HINTS = {
    "hr": "HR software",
    "people": "HR software",
    "payroll": "Payroll / HR software",
    "saas": "SaaS",
    "software": "Software",
    "benefits": "HR software",
    "public sector": "Public sector",
}

ROLE_FAMILY_PATTERNS = [
    ("data_migration_analyst", ("data migration", "migration analyst", "data mapping", "data reconciliation", "data cleansing", "successfactors")),
    ("product_marketing", ("product marketing", "go to market", "gtm", "positioning", "messaging")),
    ("functional_analyst", ("functional analyst", "functional consultant", "requirements gathering", "configuration")),
    ("implementation_assurance", ("implementation", "assurance", "audit", "programme assurance", "program assurance")),
    ("service_operations", ("service delivery", "operations", "process improvement", "shared services", "managed services")),
    ("product_management", ("product manager", "product owner", "roadmap", "backlog", "product strategy")),
]


@dataclass
class Evaluation:
    technical: int
    experience: int
    behavioural: int
    alignment: int
    logistics: str
    overall: int
    verdict: str
    role_family: str
    strengths: list[str]
    gaps: list[str]
    notes: list[str]
    warnings: list[str]
    business_outcomes: list[str]


class JobAdHTMLExtractor(HTMLParser):
    """Minimal HTML-to-text extractor for saved job adverts."""

    BLOCK_TAGS = {
        "article",
        "br",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "p",
        "section",
        "title",
        "tr",
        "ul",
        "ol",
    }

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip_depth += 1
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        cleaned = normalise_whitespace(html.unescape(data))
        if cleaned:
            self.parts.append(cleaned)

    def get_text(self) -> str:
        raw = "\n".join(self.parts)
        lines = [normalise_whitespace(line) for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def normalise_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:80] or "job"


def labelise(value: str) -> str:
    if not value:
        return "Unknown"
    return value.replace("_", " ").title()


def strip_html_to_text(raw_html: str) -> str:
    parser = JobAdHTMLExtractor()
    parser.feed(raw_html)
    return parser.get_text()


def read_text_file(path: Path) -> str:
    suffix = path.suffix.lower()
    raw = path.read_text(encoding="utf-8")
    if suffix in {".html", ".htm"}:
        return strip_html_to_text(raw)
    return raw.strip()


def read_job_text(args: argparse.Namespace) -> str:
    if args.job_ad_file:
        return read_text_file(Path(args.job_ad_file))
    if args.job_ad_text:
        return args.job_ad_text.strip()
    raise SystemExit("Provide either --job-ad-file or --job-ad-text.")


def infer_channel(*sources: str, path: Path | None = None) -> str:
    haystack = " ".join([*sources, str(path or "")]).lower()
    if "linkedin" in haystack:
        return "LinkedIn"
    if "employmenthero" in haystack:
        return "Employment Hero"
    if "greenhouse" in haystack:
        return "Greenhouse"
    if "lever" in haystack:
        return "Lever"
    if "workday" in haystack:
        return "Workday"
    if "recruiter" in haystack or "recruitment" in haystack:
        return "Recruiter"
    if "indeed" in haystack:
        return "Indeed"
    if "email" in haystack or path and path.suffix.lower() in {".eml", ".msg"}:
        return "Email"
    return "unknown"


def infer_ats_vendor(*sources: str, path: Path | None = None) -> str:
    haystack = " ".join([*sources, str(path or "")]).lower()
    patterns = [
        ("Workday", ("workday",)),
        ("Greenhouse", ("greenhouse", "boards.greenhouse.io")),
        ("Lever", ("lever", "jobs.lever.co")),
        ("SuccessFactors", ("successfactors",)),
        ("Taleo", ("taleo",)),
        ("SmartRecruiters", ("smartrecruiters",)),
        ("Teamtailor", ("teamtailor",)),
        ("Recruitee", ("recruitee",)),
        ("Applied", ("beapplied", "applied")),
        ("Jobtrain", ("jobtrain",)),
        ("Indeed", ("indeed",)),
        ("Employment Hero", ("employmenthero",)),
    ]
    for vendor, needles in patterns:
        if any(needle in haystack for needle in needles):
            return vendor
    return "Unknown"


def title_from_html(path: Path) -> str:
    if path.suffix.lower() not in {".html", ".htm"}:
        return ""
    raw = path.read_text(encoding="utf-8")
    match = re.search(r"<title[^>]*>(.*?)</title>", raw, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return normalise_whitespace(html.unescape(match.group(1)))


def leading_lines(text: str, limit: int = 20) -> list[str]:
    return [line for line in text.splitlines()[:limit] if line]


def parse_title_metadata(title: str) -> tuple[str, str, str]:
    if not title:
        return "", "", ""

    patterns = [
        r"^(?P<role>.+?)\s+Job at\s+(?P<company>.+)$",
        r"^(?P<role>.+?)\s+at\s+(?P<company>.+)$",
        r"^(?P<role>.+?),\s+(?P<location>.+?)\s+\|\s+(?P<company>.+?)(?:\s+Careers)?$",
        r"^(?P<role>.+?)\s+\|\s+(?P<company>.+?)(?:\s+Careers)?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, title)
        if match:
            groups = match.groupdict()
            return (
                normalise_whitespace(groups.get("role", "")),
                normalise_whitespace(groups.get("company", "")),
                normalise_whitespace(groups.get("location", "")),
            )
    return "", "", ""


def infer_metadata_from_text(text: str, path: Path | None = None) -> dict[str, str]:
    title = title_from_html(path) if path else ""
    role, company, location = parse_title_metadata(title)
    lines = leading_lines(text)

    if not role:
        for line in lines:
            if line.lower().startswith("product owner") or line.lower().startswith("product manager"):
                role = line
                break
    if not company:
        for idx, line in enumerate(lines):
            if line.lower().startswith("at ") and len(line) < 120:
                company = line[3:].strip()
                break
            if line.lower() == "at" and idx + 1 < len(lines):
                company = lines[idx + 1].strip()
                break
    if not location:
        for line in lines:
            lowered = line.lower()
            if "job at" in lowered:
                continue
            if line == role or line == title or lowered.startswith("at "):
                continue
            if "•" in line or "|" in line:
                location = line
                break
            if "united kingdom" in lowered or "remote" in lowered or "hybrid" in lowered or "australia" in lowered:
                location = line
                break

    return {
        "role": role,
        "company": company,
        "location": location,
        "channel": infer_channel(title, text[:200], path=path),
        "title": title,
    }


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


def infer_role_family(text: str) -> str:
    lowered = text.lower()
    scores: dict[str, int] = {}
    for family, phrases in ROLE_FAMILY_PATTERNS:
        score = sum(1 for phrase in phrases if phrase in lowered)
        if score:
            scores[family] = score

    if not scores:
        return "unknown"
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))[0][0]


def infer_application_form_type(*sources: str, text: str = "") -> str:
    haystack = " ".join(sources).lower()
    if any(term in haystack for term in ("workday", "greenhouse", "lever", "employmenthero", "successfactors", "teamtailor", "smartrecruiters", "jobtrain", "recruitee")):
        return "ats-hosted"
    if "indeed" in haystack:
        return "job-board-hosted"
    if any(term in text.lower() for term in ("apply now", "upload cv", "cover letter", "supporting statement")):
        return "employer-form"
    return "unknown"


def logistics_status(text: str, location: str | None) -> tuple[str, list[str]]:
    lowered = text.lower()
    notes: list[str] = []

    if "visa" in lowered or "sponsorship" in lowered:
        return "FLAG", ["Check right-to-work wording and whether sponsorship is expected."]

    if any(place in lowered for place in ("australia", "sydney", "new south wales", "united states", "usa")):
        notes.append(
            "Advert appears to be anchored outside the UK; check whether remote hiring genuinely includes UK candidates."
        )

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
    if any(term in lowered for term in ("2 - 5 years", "2 – 5 years", "fewer than 6 years", "associate", "junior")):
        gaps.append("Check for a seniority mismatch or overqualification risk.")

    return gaps or ["No major gap is obvious from the advert; validate through research and tailoring."]


def infer_warnings(job_text: str, role_family: str) -> list[str]:
    lowered = job_text.lower()
    warnings: list[str] = []

    if role_family == "product_marketing":
        warnings.append("This advert may be product marketing-led rather than true product ownership.")
    if role_family == "data_migration_analyst":
        warnings.append("This advert is a data-migration analyst role rather than a target product-management role.")
    if role_family == "functional_analyst":
        warnings.append("This advert may be closer to functional analysis or configuration than product leadership.")
    if role_family == "service_operations":
        warnings.append("This advert may lean toward service operations rather than core product strategy.")
    if role_family == "implementation_assurance":
        warnings.append("This advert leans toward delivery or implementation assurance; tailor accordingly.")
    if any(term in lowered for term in ("up to 4-5 years", "junior product manager", "junior product owner", "associate")):
        warnings.append("Potential seniority mismatch: advert may be aimed below Lawrence's likely level.")
    if any(term in lowered for term in ("startup", "high-velocity", "fast-paced")):
        warnings.append("Check whether the pace and culture fit what Lawrence wants now.")

    return warnings


def infer_business_outcomes(job_text: str) -> list[str]:
    lowered = job_text.lower()
    outcomes: list[str] = []

    mapping = [
        ("customer value", ("customer", "user value", "customer needs")),
        ("commercial growth", ("commercial", "revenue", "growth", "go to market", "market share")),
        ("operational efficiency", ("efficiency", "process improvement", "continuous improvement", "service delivery")),
        ("delivery confidence", ("implementation", "delivery", "rollout", "launch", "risk")),
        ("compliance and control", ("compliance", "governance", "audit", "policy")),
        ("adoption and engagement", ("adoption", "engagement", "usage", "retention")),
        ("data-led decisions", ("data", "analytics", "kpi", "insight", "metrics")),
    ]

    for label, phrases in mapping:
        if any(phrase in lowered for phrase in phrases):
            outcomes.append(label)

    return outcomes or ["customer value"]


def supporting_statement_prompts(job_text: str) -> list[str]:
    lowered = job_text.lower()
    prompts = [
        "Open with a concise reason for targeting this role and why the employer's HR or payroll product space is relevant.",
        "Match the strongest three requirements from the advert to concrete evidence from Lawrence's HR software, product, and implementation background.",
    ]

    if any(term in lowered for term in ("roadmap", "product vision", "strategy", "backlog")):
        prompts.append(
            "Include an example of shaping product direction, roadmap priorities, or delivery trade-offs."
        )
    if any(term in lowered for term in ("implementation", "rollout", "professional services", "delivery")):
        prompts.append(
            "Show how implementation oversight or customer delivery experience reduces risk and improves outcomes."
        )
    if any(term in lowered for term in ("stakeholder", "communication", "sales", "marketing", "support")):
        prompts.append(
            "Demonstrate cross-functional communication across executives, product, delivery, sales, or customer teams."
        )
    if any(term in lowered for term in ("data", "analytics", "metrics", "insight")):
        prompts.append(
            "Reference a data-led example where analysis or metrics informed a product or commercial decision."
        )

    prompts.extend(
        [
            "Keep the tone UK-appropriate: specific, evidence-led, and free of inflated claims.",
            "Close by confirming right to work, notice period if useful, and practical location fit only if the advert makes it relevant.",
        ]
    )
    return prompts


def infer_focus_themes(job_text: str) -> list[str]:
    lowered = job_text.lower()
    themes: list[tuple[str, tuple[str, ...]]] = [
        ("Data migration, validation, and reconciliation", ("data migration", "data mapping", "data modelling", "reconciliation", "cleansing", "validation")),
        ("Product strategy and roadmap ownership", ("roadmap", "product strategy", "product vision", "priorities")),
        ("HR and payroll domain credibility", ("hr", "payroll", "hris", "hcm", "people platform")),
        ("Implementation and delivery confidence", ("implementation", "delivery", "rollout", "launch")),
        ("Stakeholder leadership", ("stakeholder", "communication", "influence", "present updates")),
        ("Data-led decision making", ("data", "analytics", "kpi", "insight", "metrics")),
        ("Commercial and customer outcomes", ("customer", "commercial", "growth", "value")),
        ("Cross-functional collaboration", ("sales", "marketing", "support", "engineering", "architects", "qa")),
    ]

    selected = [label for label, phrases in themes if any(phrase in lowered for phrase in phrases)]
    return selected[:5] or ["Transferable product, delivery, and leadership strengths"]


def infer_cv_emphasis(job_text: str) -> list[str]:
    lowered = job_text.lower()
    bullets: list[str] = [
        "Lead with HR software, payroll, and SaaS product credibility near the top of the CV.",
        "Keep the CV outcome-led, with measurable change, growth, migration, delivery, or transformation results.",
    ]
    if any(term in lowered for term in ("data migration", "data mapping", "reconciliation", "cleansing", "successfactors", "uat", "parallel payroll")):
        bullets.append("Make any direct data-migration, audit, validation, or implementation-governance evidence easy to spot.")
    if any(term in lowered for term in ("roadmap", "product owner", "product manager", "okr")):
        bullets.append("Bring roadmap ownership, prioritisation, and product-direction decisions into the opening profile and key roles.")
    if any(term in lowered for term in ("implementation", "delivery", "professional services")):
        bullets.append("Show implementation oversight and delivery-risk reduction as a differentiator, not just operational detail.")
    if any(term in lowered for term in ("data", "analytics", "kpi", "insight")):
        bullets.append("Include at least one example of data-led decision making or analytics-informed product direction.")
    if any(term in lowered for term in ("team", "mentor", "lead")):
        bullets.append("Make leadership and mentoring visible if the role expects team guidance or product-owner leadership.")
    return bullets


def infer_cover_letter_angles(job_text: str) -> list[str]:
    lowered = job_text.lower()
    angles = [
        "Open with direct relevance to the employer's HR, payroll, or people-software context.",
        "Link product judgement to commercial credibility and customer outcomes.",
    ]
    if any(term in lowered for term in ("data migration", "data mapping", "validation", "reconciliation", "cleansing")):
        angles.append("Address data migration credibility directly, especially validation, reconciliation, risk reduction, and stakeholder communication.")
    if any(term in lowered for term in ("implementation", "delivery", "launch")):
        angles.append("Frame implementation oversight as a strength that improves adoption and reduces delivery risk.")
    if any(term in lowered for term in ("stakeholder", "sales", "marketing", "support")):
        angles.append("Show that cross-functional communication is a practical strength, not a soft generic claim.")
    if any(term in lowered for term in ("startup", "fast-paced", "high-velocity")):
        angles.append("Address pace carefully: show adaptability without pretending this is identical to every past environment.")
    return angles


def infer_interview_questions(metadata: dict, evaluation: Evaluation) -> list[str]:
    role = metadata.get("role", "this role")
    company = metadata.get("company", "the company")
    role_family = metadata.get("role_family", "unknown")
    if role_family == "data_migration_analyst":
        questions = [
            f"What attracted you to {role} at {company}?",
            "Tell us about a time you found and resolved a data-quality or reconciliation issue.",
            "How do you approach data mapping between a legacy system and a target platform?",
            "Describe how you would explain migration defects or risks to non-technical stakeholders.",
            "Tell us about a time you supported testing, validation, or business readiness in a system change.",
        ]
    else:
        questions = [
            f"What attracted you to {role} at {company}?",
            "How do you decide what belongs on a product roadmap when stakeholder demands compete?",
            "Tell us about a time you improved the outcome of an HR, payroll, or people-technology initiative.",
            "How do you balance strategic product thinking with delivery reality?",
            "Describe a situation where you had to influence senior stakeholders with different priorities.",
        ]
    if "data-led decisions" in evaluation.business_outcomes:
        questions.append("Tell us about a decision you made using data, KPIs, or customer insight.")
    if any("seniority mismatch" in warning.lower() for warning in evaluation.warnings):
        questions.append("This role may look narrower than parts of your background. Why is it still a strong fit for you now?")
    if any("pace and culture" in warning.lower() for warning in evaluation.warnings):
        questions.append("How do you adapt your leadership style in fast-paced or evolving environments?")
    questions.append("What questions would you ask us before deciding this role is the right fit?")
    return questions


def build_evaluation(job_text: str, location: str | None) -> Evaluation:
    technical = keyword_score(job_text, TECHNICAL_KEYWORDS)
    experience = keyword_score(job_text, EXPERIENCE_KEYWORDS)
    behavioural = keyword_score(job_text, BEHAVIOURAL_KEYWORDS)
    alignment = keyword_score(job_text, ALIGNMENT_KEYWORDS)
    logistics, logistics_notes = logistics_status(job_text, location)
    role_family = infer_role_family(job_text)

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
        role_family=role_family,
        strengths=infer_strengths(job_text),
        gaps=infer_gaps(job_text),
        notes=logistics_notes,
        warnings=infer_warnings(job_text, role_family),
        business_outcomes=infer_business_outcomes(job_text),
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
    statement_prompts = "\n".join(f"- {item}" for item in supporting_statement_prompts(metadata.get("job_text", "")))
    warnings = "\n".join(f"- {item}" for item in evaluation.warnings) or "- No structural warning identified."
    business_outcomes = "\n".join(f"- {item}" for item in evaluation.business_outcomes)

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

**Role Family:** {labelise(evaluation.role_family)}

## Key Strengths
{strengths}

## Gaps To Check
{gaps}

## Structural Warnings
{warnings}

## Business Outcomes To Lead With
{business_outcomes}

## Logistics Notes
{notes}

## Supporting Statement Prompts
{statement_prompts}

## Suggested UK Supporting Statement Shape
- Opening: why this role, why this employer, and why now.
- Evidence match: two or three short paragraphs aligned to the advert's core requirements.
- Delivery credibility: a concrete example of product, implementation, or stakeholder impact.
- Closing: practical fit, motivation, and a direct expression of interest.

## Role Metadata
- Company: {company}
- Role: {role}
- Role family: {labelise(evaluation.role_family)}
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


def render_cv_brief_markdown(metadata: dict, evaluation: Evaluation) -> str:
    focus_themes = "\n".join(f"- {item}" for item in infer_focus_themes(metadata.get("job_text", "")))
    emphasis = "\n".join(f"- {item}" for item in infer_cv_emphasis(metadata.get("job_text", "")))
    return f"""# Tailored CV Brief

## Role
- Company: {metadata.get('company', '')}
- Role: {metadata.get('role', '')}
- Role family: {labelise(metadata.get('role_family', 'unknown'))}
- Overall fit: {evaluation.overall}/100 ({evaluation.verdict})

## Lead With
{focus_themes}

## CV Emphasis
{emphasis}

## Evidence To Pull Forward
- Use the strongest examples from HR software, payroll, SaaS, product leadership, implementation assurance, and senior stakeholder influence.
- Prefer results, transitions, growth, delivery confidence, customer outcomes, and transformation evidence.
- Keep examples relevant to the role shape rather than listing every past responsibility.

## CV Editing Checklist
- [ ] Rewrite the profile summary for this role
- [ ] Bring the most relevant achievements into the first page
- [ ] Reduce lower-value legacy detail
- [ ] Make role-family fit obvious within 10 seconds of reading
- [ ] Check British English and naming consistency
"""


def render_cover_letter_brief_markdown(metadata: dict, evaluation: Evaluation) -> str:
    prompts = "\n".join(f"- {item}" for item in supporting_statement_prompts(metadata.get("job_text", "")))
    angles = "\n".join(f"- {item}" for item in infer_cover_letter_angles(metadata.get("job_text", "")))
    warnings = "\n".join(f"- {item}" for item in evaluation.warnings) or "- No major structural warning identified."
    return f"""# Tailored Cover Letter Brief

## Role
- Company: {metadata.get('company', '')}
- Role: {metadata.get('role', '')}
- Channel: {metadata.get('channel', '')}

## Core Angles
{angles}

## Supporting Statement Prompts
{prompts}

## Risks To Handle Carefully
{warnings}

## Suggested Structure
1. Why this company and role
2. Why Lawrence's background is relevant
3. Evidence of product / delivery / stakeholder impact
4. Close with practical fit and direct interest

## Cover Letter Checklist
- [ ] Tailor the opening sentence to the employer
- [ ] Match the strongest three requirements directly
- [ ] Use evidence, not adjectives
- [ ] Keep tone specific and commercially credible
- [ ] End cleanly without overclaiming
"""


def render_interview_questions_markdown(metadata: dict, evaluation: Evaluation) -> str:
    questions = "\n".join(f"- {item}" for item in infer_interview_questions(metadata, evaluation))
    business_outcomes = "\n".join(f"- {item}" for item in evaluation.business_outcomes)
    return f"""# Interview Questions

## Role
- Company: {metadata.get('company', '')}
- Role: {metadata.get('role', '')}

## Likely Questions
{questions}

## Themes To Prepare
- Role family: {labelise(metadata.get('role_family', 'unknown'))}
- Business outcomes to emphasise:
{business_outcomes}

## Preparation Notes
- Prepare STAR examples around product direction, stakeholder influence, implementation confidence, and business outcomes.
- Be ready to explain why this role is the right level and shape.
- Be ready to connect HR/payroll domain knowledge to the employer's actual product context.
"""


def write_preparation_pack(app_dir: Path, metadata: dict, evaluation: Evaluation) -> None:
    (app_dir / "cv_brief.md").write_text(
        render_cv_brief_markdown(metadata, evaluation),
        encoding="utf-8",
    )
    (app_dir / "cover_letter_brief.md").write_text(
        render_cover_letter_brief_markdown(metadata, evaluation),
        encoding="utf-8",
    )
    (app_dir / "interview_questions.md").write_text(
        render_interview_questions_markdown(metadata, evaluation),
        encoding="utf-8",
    )


def refresh_preparation_pack(args: argparse.Namespace) -> int:
    app_dir, metadata = load_application_dir(args.application_dir)
    evaluation = build_evaluation(metadata.get("job_text", ""), metadata.get("location"))
    metadata["fit_rating"] = evaluation.verdict
    metadata["role_family"] = evaluation.role_family
    write_json(app_dir / "application.json", metadata)
    (app_dir / "evaluation.md").write_text(
        render_evaluation_markdown(metadata.get("company", ""), metadata.get("role", ""), evaluation, metadata),
        encoding="utf-8",
    )
    write_preparation_pack(app_dir, metadata, evaluation)
    print(app_dir / "cv_brief.md")
    print(app_dir / "cover_letter_brief.md")
    print(app_dir / "interview_questions.md")
    return 0


def render_form_review_markdown(metadata: dict, form_path: Path) -> str:
    ats_vendor = metadata.get("ats_vendor", "Unknown")
    form_type = metadata.get("application_form_type", "unknown")
    return f"""# Form Review

## Role
- Company: {metadata.get('company', '')}
- Role: {metadata.get('role', '')}
- Application ID: {metadata.get('application_id', '')}
- ATS vendor: {ats_vendor}
- Form type: {form_type}
- Channel: {metadata.get('channel', '')}
- Source: {metadata.get('source', '')}

## Form Structure
- Steps:
- Account creation required: yes / no / unknown
- CV upload required: yes / no / unknown
- CV parsing used: yes / no / unknown
- LinkedIn import offered: yes / no / unknown
- Cover letter required: yes / no / unknown
- Supporting statement required: yes / no / unknown
- Additional free-text questions: yes / no / unknown
- Equal opportunities section present: yes / no / unknown

## Exact Questions
- Q1:
- Q2:
- Q3:

## Gating / Screening Questions
- Right to work:
- Sponsorship:
- Location / commute:
- Salary expectation:
- Notice period:
- Years of experience:
- Domain experience:
- Travel:

## ATS / Workflow Observations
- What looked like a knockout filter?
- What looked weighted but not explicit?
- What looked biased, simplistic, or risky?
- What file formats or naming rules were enforced?
- Did the form appear to parse the CV accurately?

## Preparation Notes
- Which CV version should be used?
- Is a tailored cover letter enough, or is a supporting statement needed?
- Which business outcomes should be emphasised?
- Which gaps need careful framing?

## Outcome
- Status:
- Submitted by:
- Date:
- Notes:

## File
- Private review file: {form_path.relative_to(ROOT)}
"""


def create_form_review(args: argparse.Namespace) -> int:
    app_dir, metadata = load_application_dir(args.application_dir)
    FORMS_DIR.mkdir(parents=True, exist_ok=True)

    application_id = metadata.get("application_id") or app_dir.name
    form_path = FORMS_DIR / f"{application_id}-form-review.md"

    if form_path.exists() and not args.force:
        raise SystemExit(f"Form review already exists: {form_path}. Use --force to overwrite.")

    metadata["ats_vendor"] = args.ats_vendor or metadata.get("ats_vendor") or infer_ats_vendor(
        metadata.get("source", ""),
        metadata.get("channel", ""),
        metadata.get("job_text", "")[:200],
    )
    existing_form_type = metadata.get("application_form_type", "")
    metadata["application_form_type"] = (
        args.application_form_type
        or (
            existing_form_type
            if existing_form_type and existing_form_type != "unknown"
            else infer_application_form_type(
                metadata.get("source", ""),
                metadata.get("channel", ""),
                text=metadata.get("job_text", ""),
            )
        )
    )
    write_json(app_dir / "application.json", metadata)
    form_path.write_text(render_form_review_markdown(metadata, form_path), encoding="utf-8")

    print(form_path)
    print(f"ATS vendor: {metadata['ats_vendor']}")
    print(f"Form type: {metadata['application_form_type']}")
    return 0


def create_application_workspace(
    company: str,
    role: str,
    job_text: str,
    channel: str,
    source: str,
    location: str,
    sector: str,
    role_type: str,
    original_file: Path | None = None,
) -> tuple[Path, Evaluation]:
    created = date.today().isoformat()
    app_slug = f"{created}-{slugify(company)}-{slugify(role)}"
    app_dir = APPLICATIONS_DIR / app_slug

    if app_dir.exists():
        raise SystemExit(f"Application directory already exists: {app_dir}")

    app_dir.mkdir(parents=True, exist_ok=False)
    evaluation = build_evaluation(job_text, location)

    metadata = {
        "application_id": app_slug,
        "company": normalise_whitespace(company),
        "role": normalise_whitespace(role),
        "channel": normalise_whitespace(channel or "unknown"),
        "source": source or "",
        "location": location or "",
        "role_type": role_type or infer_role_type(job_text),
        "role_family": evaluation.role_family,
        "sector": sector or infer_sector(job_text),
        "ats_vendor": infer_ats_vendor(source, channel, job_text[:200], path=original_file),
        "application_form_type": infer_application_form_type(source, channel, text=job_text),
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "draft",
        "fit_rating": evaluation.verdict,
        "job_text": job_text,
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
    write_preparation_pack(app_dir, metadata, evaluation)

    if original_file:
        target = app_dir / f"job_ad{original_file.suffix or '.txt'}"
        shutil.copyfile(original_file, target)
    else:
        (app_dir / "job_ad.txt").write_text(job_text + "\n", encoding="utf-8")

    return app_dir, evaluation


def create_application(args: argparse.Namespace) -> int:
    job_text = read_job_text(args)
    app_dir, evaluation = create_application_workspace(
        company=args.company,
        role=args.role,
        job_text=job_text,
        channel=args.channel or "unknown",
        source=args.source or "",
        location=args.location or "",
        sector=args.sector or "",
        role_type=args.role_type or "",
        original_file=Path(args.job_ad_file) if args.job_ad_file else None,
    )

    print(app_dir)
    print(f"Overall fit: {evaluation.overall}/100 ({evaluation.verdict})")
    return 0


def import_application(args: argparse.Namespace) -> int:
    input_path = Path(args.input_file)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    text = read_text_file(input_path)
    inferred = infer_metadata_from_text(text, input_path)

    role = args.role or inferred.get("role") or "Unknown role"
    company = args.company or inferred.get("company") or "Unknown company"
    location = args.location or inferred.get("location") or ""
    source = args.source or str(input_path)
    inferred_channel = inferred.get("channel", "")
    channel = args.channel or (
        inferred_channel
        if inferred_channel and inferred_channel != "unknown"
        else infer_channel(source, inferred.get("title", ""), text[:200], path=input_path)
    )

    IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    import_slug = f"{stamp}-{slugify(company)}-{slugify(role)}"
    import_text_path = IMPORTS_DIR / f"{import_slug}.txt"
    import_meta_path = IMPORTS_DIR / f"{import_slug}.json"

    import_text_path.write_text(text + "\n", encoding="utf-8")
    write_json(
        import_meta_path,
        {
            "company": company,
            "role": role,
            "location": location,
        "channel": channel,
        "source": source,
        "input_file": str(input_path),
        "page_title": inferred.get("title", ""),
        "ats_vendor": infer_ats_vendor(source, channel, text[:200], path=input_path),
        "application_form_type": infer_application_form_type(source, channel, text=text),
    },
    )

    print(import_text_path)
    print(import_meta_path)

    if args.create:
        app_dir, evaluation = create_application_workspace(
            company=company,
            role=role,
            job_text=text,
            channel=channel,
            source=source,
            location=location,
            sector=args.sector or "",
            role_type=args.role_type or "",
            original_file=input_path,
        )
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
        "role_family": metadata.get("role_family", ""),
        "role_type": metadata.get("role_type", ""),
        "channel": args.channel or metadata.get("channel", ""),
        "ats_vendor": args.ats_vendor or metadata.get("ats_vendor", ""),
        "application_form_type": args.application_form_type or metadata.get("application_form_type", ""),
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

    import_parser = subparsers.add_parser(
        "import",
        help="Import a saved advert or recruiter note and optionally create an application workspace",
    )
    import_parser.add_argument("--input-file", required=True, help="Path to saved HTML, text, or email-style note")
    import_parser.add_argument("--company", help="Override the inferred company name")
    import_parser.add_argument("--role", help="Override the inferred role title")
    import_parser.add_argument("--channel", help="Override the inferred channel")
    import_parser.add_argument("--source", help="Source URL or note")
    import_parser.add_argument("--location", help="Override the inferred location")
    import_parser.add_argument("--sector", help="Override the inferred sector")
    import_parser.add_argument("--role-type", help="Override the inferred role type")
    import_parser.add_argument(
        "--create",
        action="store_true",
        help="Create an application workspace immediately after import",
    )
    import_parser.set_defaults(func=import_application)

    submit_parser = subparsers.add_parser(
        "submit",
        help="Record a sent application in the tracker",
    )
    submit_parser.add_argument("--application-dir", required=True, help="Application folder path")
    submit_parser.add_argument("--status", default="submitted", help="Submission status")
    submit_parser.add_argument("--channel", help="Submission channel override")
    submit_parser.add_argument("--ats-vendor", help="ATS vendor override")
    submit_parser.add_argument("--application-form-type", help="Application form type override")
    submit_parser.add_argument("--date", help="Submission date YYYY-MM-DD")
    submit_parser.add_argument("--contact-person", help="Hiring contact")
    submit_parser.add_argument("--cv-file", help="CV file used")
    submit_parser.add_argument("--cover-letter-file", help="Cover letter or statement file used")
    submit_parser.add_argument("--notes", help="Tracker notes")
    submit_parser.set_defaults(func=submit_application)

    form_review_parser = subparsers.add_parser(
        "form-review",
        help="Create a private structured review sheet for an application's real form flow",
    )
    form_review_parser.add_argument("--application-dir", required=True, help="Application folder path")
    form_review_parser.add_argument("--ats-vendor", help="Override inferred ATS vendor")
    form_review_parser.add_argument(
        "--application-form-type",
        help="Override inferred form type, e.g. ats-hosted, job-board-hosted, employer-form",
    )
    form_review_parser.add_argument("--force", action="store_true", help="Overwrite an existing form review file")
    form_review_parser.set_defaults(func=create_form_review)

    prepare_parser = subparsers.add_parser(
        "prepare",
        help="Generate or refresh the tailored CV brief, cover letter brief, and interview-question pack",
    )
    prepare_parser.add_argument("--application-dir", required=True, help="Application folder path")
    prepare_parser.set_defaults(func=refresh_preparation_pack)

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
