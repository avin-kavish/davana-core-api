import re

from vehicles.make_options import POPULAR_VEHICLE_MAKES
from vehicles.model_options import MODELS_BY_MAKE

YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")

KNOWN_MAKES = sorted(POPULAR_VEHICLE_MAKES, key=len, reverse=True)


def _title_case_phrase(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split())


def _match_known_model(make: str, remainder: str) -> str | None:
    models = MODELS_BY_MAKE.get(make)
    if not models or not remainder:
        return None

    normalized = " ".join(remainder.split())
    lower = normalized.lower()

    for model in sorted(models, key=len, reverse=True):
        model_lower = model.lower()
        if lower == model_lower:
            return model
        if lower.startswith(model_lower):
            trailing = normalized[len(model) :].strip()
            if not trailing:
                return model

    return None


def _match_known_make(text: str) -> tuple[str, str] | None:
    lower = text.lower()
    for candidate in KNOWN_MAKES:
        if lower.startswith(candidate.lower()):
            remainder = text[len(candidate) :].strip()
            return candidate, remainder
    return None


def parse_vehicle_term(term: str) -> dict[str, str]:
    cleaned = " ".join(term.strip().split())
    if not cleaned:
        return {}

    parsed: dict[str, str] = {}

    year_match = YEAR_PATTERN.search(cleaned)
    if year_match:
        year = year_match.group(0)
        parsed["year_from"] = year
        parsed["year_to"] = year
        cleaned = YEAR_PATTERN.sub("", cleaned).strip()
        cleaned = " ".join(cleaned.split())

    if not cleaned:
        return parsed

    make_match = _match_known_make(cleaned)
    if make_match:
        make, remainder = make_match
        parsed["make"] = make
        model = _match_known_model(make, remainder)
        if model:
            parsed["model"] = model
        return parsed

    parts = cleaned.split()
    if len(parts) == 1:
        guessed_make = _title_case_phrase(parts[0])
        if guessed_make in MODELS_BY_MAKE:
            parsed["make"] = guessed_make

    return parsed
