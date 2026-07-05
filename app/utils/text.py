import re
from typing import Optional


def compact_whitespace(value: Optional[str]) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def lines_to_list(value: Optional[str]) -> list[str]:
    if not value:
        return []

    items: list[str] = []
    for raw_line in value.replace(",", "\n").splitlines():
        cleaned = compact_whitespace(raw_line.lstrip("-*•"))
        if cleaned:
            items.append(cleaned)
    return items


def unique_lowered(values: list[str]) -> list[str]:
    seen: set[str] = set()
    items: list[str] = []
    for value in values:
        cleaned = compact_whitespace(value)
        marker = cleaned.lower()
        if cleaned and marker not in seen:
            seen.add(marker)
            items.append(cleaned)
    return items


def to_multiline_bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values if value)


def truncate(value: str, max_length: int = 500) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 3].rstrip()}..."
