"""Ingredient normalization and quantity aggregation for the Shopping List.

Per docs/architecture.md §5: this module is pure/stateless — it takes
ingredient rows already fetched from the DB (ordered by lowest recipe_id,
then ingredient position) and returns the aggregated list, so it can be
reasoned about independently of SQL or HTTP. Called only from
routers/shopping_list.py.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional, TypedDict

_QUANTITY_RE = re.compile(r"^\s*(\d+(?:\.\d+)?|\d+/\d+)\s*([a-zA-Z]*)\s*$")


class AggregatedItem(TypedDict):
    ingredient_key: str
    ingredient: str
    quantity: str


def normalize_name(name: str) -> str:
    """Lowercase, strip leading/trailing whitespace, collapse internal
    whitespace runs to a single space. This is the grouping key and also the
    key used in shopping_list_checks and the PATCH path parameter."""
    return re.sub(r"\s+", " ", name.strip().lower())


def _parse_quantity(raw: Optional[str]) -> Optional[tuple[float, str]]:
    """Match a quantity string against the amount/unit pattern. Returns
    (numeric value, lowercased unit word) or None if it doesn't match (e.g.
    blank/free-text amounts like "to taste")."""
    if not raw:
        return None
    match = _QUANTITY_RE.match(raw)
    if not match:
        return None
    number_part, unit_part = match.group(1), match.group(2)
    if "/" in number_part:
        numerator, denominator = number_part.split("/", 1)
        value = float(numerator) / float(denominator)
    else:
        value = float(number_part)
    return value, unit_part.lower()


def _format_number(value: float) -> str:
    """Render a summed quantity, trimming a trailing '.0' (or other
    insignificant trailing zeros)."""
    if value == int(value):
        return str(int(value))
    formatted = f"{value:.4f}".rstrip("0").rstrip(".")
    return formatted


def aggregate(rows: Iterable[Any]) -> list[AggregatedItem]:
    """Group ingredient rows by normalized name and combine quantities.

    `rows` must be pre-ordered by lowest recipe_id, then ingredient
    position (routers/shopping_list.py's SQL ORDER BY enforces this), and
    each row must support `row["quantity"]` / `row["name"]` access
    (sqlite3.Row satisfies this).

    Returns a list of {ingredient_key, ingredient, quantity} dicts, sorted
    alphabetically (case-insensitive) by displayed ingredient name.
    """
    groups: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for row in rows:
        raw_name = row["name"]
        key = normalize_name(raw_name)
        if key not in groups:
            groups[key] = {"display_name": raw_name, "raw_quantities": [], "parsed": []}
            order.append(key)
        group = groups[key]
        raw_quantity = row["quantity"]
        group["raw_quantities"].append(raw_quantity)
        group["parsed"].append(_parse_quantity(raw_quantity))

    results: list[AggregatedItem] = []
    for key in order:
        group = groups[key]
        parsed_list: list[Optional[tuple[float, str]]] = group["parsed"]

        combined_quantity: Optional[str] = None
        if parsed_list and all(p is not None for p in parsed_list):
            units = {p[1] for p in parsed_list if p is not None}
            if len(units) == 1:
                total = sum(p[0] for p in parsed_list if p is not None)
                unit = next(iter(units))
                rendered = _format_number(total)
                combined_quantity = f"{rendered} {unit}" if unit else rendered

        if combined_quantity is None:
            seen: list[str] = []
            for raw in group["raw_quantities"]:
                if raw is None:
                    continue
                stripped = raw.strip()
                if not stripped:
                    continue
                if stripped not in seen:
                    seen.append(stripped)
            combined_quantity = "; ".join(seen)

        results.append(
            AggregatedItem(
                ingredient_key=key,
                ingredient=group["display_name"],
                quantity=combined_quantity,
            )
        )

    results.sort(key=lambda item: item["ingredient"].lower())
    return results
