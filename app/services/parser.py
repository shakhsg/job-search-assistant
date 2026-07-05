import re

from app.utils.text import compact_whitespace, unique_lowered


SKILL_LIBRARY = [
    "python",
    "flask",
    "sql",
    "sqlite",
    "postgresql",
    "javascript",
    "typescript",
    "react",
    "tailwind",
    "docker",
    "aws",
    "gcp",
    "azure",
    "git",
    "rest api",
    "graphql",
    "pandas",
    "numpy",
    "machine learning",
    "data analysis",
    "etl",
    "testing",
    "pytest",
    "ci/cd",
    "kubernetes",
    "linux",
    "seo",
    "product management",
    "analytics",
]

SECTION_ALIASES = {
    "responsibilities": {"responsibilities", "what you'll do", "what you will do", "role responsibilities"},
    "requirements": {"requirements", "qualifications", "what we're looking for", "what we are looking for", "must have"},
    "preferred": {"preferred", "nice to have", "good to have", "bonus"},
    "benefits": {"benefits", "what we offer", "perks"},
}


class JobDescriptionParser:
    def parse(self, description: str, title: str = "") -> dict:
        cleaned_text = compact_whitespace(description)
        lines = [line.strip() for line in description.splitlines() if line.strip()]
        sections = self._extract_sections(lines)
        skills = self._extract_skills(f"{title}\n{description}")
        responsibilities = sections.get("responsibilities") or self._fallback_bullets(lines[:20])
        requirements = sections.get("requirements") or self._extract_requirement_lines(lines)
        preferred = sections.get("preferred", [])
        seniority = self._infer_seniority(f"{title}\n{description}")
        work_mode = self._infer_work_mode(description)

        keywords = unique_lowered(
            skills
            + responsibilities[:5]
            + requirements[:5]
            + preferred[:3]
        )[:12]

        return {
            "summary": cleaned_text[:600],
            "skills": skills,
            "responsibilities": responsibilities[:10],
            "requirements": requirements[:10],
            "preferred": preferred[:6],
            "seniority": seniority,
            "work_mode": work_mode,
            "keywords": keywords,
        }

    def _extract_sections(self, lines: list[str]) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {key: [] for key in SECTION_ALIASES}
        active_section = None

        for line in lines:
            normalized = re.sub(r"[^a-z0-9' ]", "", line.lower()).strip()
            matched_section = None
            for section_name, aliases in SECTION_ALIASES.items():
                if normalized in aliases or any(normalized.startswith(alias) for alias in aliases):
                    matched_section = section_name
                    break

            if matched_section:
                active_section = matched_section
                continue

            cleaned_line = compact_whitespace(line.lstrip("-*•"))
            if active_section and cleaned_line:
                sections[active_section].append(cleaned_line)

        return sections

    def _extract_skills(self, text: str) -> list[str]:
        lowered = text.lower()
        matches = []
        for skill in SKILL_LIBRARY:
            pattern = re.escape(skill)
            if re.search(rf"\b{pattern}\b", lowered):
                matches.append(skill.title() if skill.islower() else skill)
        return unique_lowered(matches)

    def _fallback_bullets(self, lines: list[str]) -> list[str]:
        bullets = [compact_whitespace(line.lstrip("-*•")) for line in lines if line.startswith(("-", "*", "•"))]
        return unique_lowered([line for line in bullets if line])

    def _extract_requirement_lines(self, lines: list[str]) -> list[str]:
        patterns = ("experience", "years", "required", "proficient", "strong", "knowledge")
        return unique_lowered(
            [
                compact_whitespace(line.lstrip("-*•"))
                for line in lines
                if any(pattern in line.lower() for pattern in patterns)
            ]
        )

    def _infer_seniority(self, text: str) -> str:
        lowered = text.lower()
        if any(term in lowered for term in {"director", "head of", "vp", "vice president"}):
            return "director+"
        if any(term in lowered for term in {"lead", "principal", "staff", "senior"}):
            return "senior"
        if any(term in lowered for term in {"intern", "graduate", "junior", "entry"}):
            return "junior"
        return "mid"

    def _infer_work_mode(self, text: str) -> str:
        lowered = text.lower()
        if "remote" in lowered:
            return "remote"
        if "hybrid" in lowered:
            return "hybrid"
        return "onsite"
