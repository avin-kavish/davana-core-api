from django.db.models import CharField, F, Value
from django.db.models.functions import Cast, Concat

from vehicles.models import Vehicle


def _make_model_year_phrase():
    """Reserved for make/model/year suggestions."""
    return Concat(
        F("make"),
        Value(" "),
        F("model"),
        Value(" "),
        Cast(F("year_of_manufacture"), CharField()),
    )


def _make_suggestions(
    base_qs,
    query: str | None,
    limit: int,
) -> list[dict[str, str | int | None]]:
    rows = base_qs.values("make").distinct().order_by("make")
    if query:
        rows = rows.filter(make__icontains=query)

    return [
        {
            "phrase": row["make"],
            "make": row["make"],
            "model": None,
            "year": None,
        }
        for row in rows[:limit]
    ]


def _make_model_suggestions(
    base_qs,
    query: str | None,
    limit: int,
) -> list[dict[str, str | int | None]]:
    rows = (
        base_qs.annotate(phrase=Concat(F("make"), Value(" "), F("model")))
        .values("make", "model", "phrase")
        .distinct()
        .order_by("make", "model")
    )
    if query:
        rows = rows.filter(phrase__icontains=query)

    return [
        {
            "phrase": row["phrase"],
            "make": row["make"],
            "model": row["model"],
            "year": None,
        }
        for row in rows[:limit]
    ]


def vehicle_search_suggestions(
    query: str | None = None,
    limit: int = 10,
) -> list[dict[str, str | int | None]]:
    base_qs = Vehicle.objects.filter(is_active=True)
    cleaned_query = (query or "").strip() or None

    suggestions = _make_suggestions(base_qs, cleaned_query, limit)
    suggestions.extend(_make_model_suggestions(base_qs, cleaned_query, limit))

    suggestions.sort(key=lambda item: item["phrase"].lower())
    return suggestions[:limit]
