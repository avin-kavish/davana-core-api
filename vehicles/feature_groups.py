from vehicles.models import Vehicle

OTHER_FEATURE_GROUP = "Other"

_FEATURE_GROUP_BY_VALUE: dict[str, str] = {}
_CANONICAL_FEATURE_BY_LOWER: dict[str, str] = {}


def _build_feature_maps() -> None:
    if _FEATURE_GROUP_BY_VALUE:
        return

    for group_name, choices in Vehicle.FEATURE_CHOICES:
        for value, _label in choices:
            _FEATURE_GROUP_BY_VALUE[value] = group_name
            _CANONICAL_FEATURE_BY_LOWER[value.lower()] = value


def group_and_sort_features(features: list[str] | None) -> list[dict[str, list[str] | str]]:
    if not features:
        return []

    _build_feature_maps()

    grouped: dict[str, list[str]] = {}
    for feature in features:
        canonical = _CANONICAL_FEATURE_BY_LOWER.get(feature.lower(), feature)
        group = _FEATURE_GROUP_BY_VALUE.get(canonical, OTHER_FEATURE_GROUP)
        grouped.setdefault(group, []).append(canonical)

    return [
        {
            "group": group_name,
            "items": sorted(grouped[group_name], key=str.casefold),
        }
        for group_name in sorted(grouped.keys(), key=str.casefold)
    ]
