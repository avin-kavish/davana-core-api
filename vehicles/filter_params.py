from vehicles.term_parser import parse_vehicle_term

FILTER_PARAM_NAMES = (
    "term",
    "vehicle_type",
    "make",
    "model",
    "year_from",
    "year_to",
    "price_from",
    "price_to",
    "mileage_from",
    "mileage_to",
    "condition",
    "registration",
    "color",
    "fuel",
    "transmission",
    "hybrid",
)


def build_filter_params(query_params) -> dict[str, str | None]:
    filters = {name: None for name in FILTER_PARAM_NAMES}

    for name in FILTER_PARAM_NAMES:
        value = query_params.get(name)
        if value:
            filters[name] = value

    term = filters.get("term")
    if term:
        filters["term"] = None
        for key in ("make", "model", "year_from", "year_to"):
            filters[key] = None
        for key, value in parse_vehicle_term(term).items():
            filters[key] = value

    return filters


def filterset_data(filters: dict[str, str | None]) -> dict[str, str]:
    return {
        key: value
        for key, value in filters.items()
        if key != "term" and value is not None
    }
