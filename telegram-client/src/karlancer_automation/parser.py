import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProjectMessage:
    title: str | None
    description: str
    budget: str | None
    deadline: str | None
    source_text: str


def extract_field(text: str, labels: tuple[str, ...]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"^\s*(?:{label_pattern})\s*[:：]\s*(.+?)\s*$"

    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else None


def parse_project_message(text: str) -> ProjectMessage:
    normalized_text = text.strip()

    title = extract_field(
        normalized_text,
        ("عنوان پروژه", "عنوان", "پروژه"),
    )

    budget = extract_field(
        normalized_text,
        ("بودجه", "مبلغ", "هزینه پیشنهادی"),
    )

    deadline = extract_field(
        normalized_text,
        ("مهلت", "زمان انجام", "مدت انجام", "ددلاین"),
    )

    return ProjectMessage(
        title=title,
        description=normalized_text,
        budget=budget,
        deadline=deadline,
        source_text=text,
    )
