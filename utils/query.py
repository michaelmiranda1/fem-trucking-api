# utils/query.py
from __future__ import annotations

import math
from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status


def total_pages(total: int, page_size: int) -> int:
    if page_size <= 0:
        return 1
    return max(1, math.ceil(total / page_size))


def parse_sort(sort: Optional[str]) -> List[str]:
    """
    sort="driver_name,-created_at" -> ["driver_name", "-created_at"]
    """
    if not sort:
        return []
    parts = [p.strip() for p in sort.split(",")]
    return [p for p in parts if p]


def build_order_by(
    sort: Optional[str],
    allowed: Dict[str, Any],
    default: List[str],
    stable_key: Optional[str] = None,
) -> List[Any]:
    """
    allowed: {"driver_name": Driver.driver_name, ...}
    default: ["-updated_at", "driver_id"]
    stable_key: "driver_id" (adds as last tiebreaker if missing)

    Returns SQLAlchemy order_by expressions.
    """
    fields = parse_sort(sort) or default
    order_clauses: List[Any] = []
    seen = set()

    for token in fields:
        desc = token.startswith("-")
        key = token[1:] if desc else token

        if key not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid sort field '{key}'. Allowed: {sorted(list(allowed.keys()))}",
            )

        if key in seen:
            continue
        seen.add(key)

        col = allowed[key]
        order_clauses.append(col.desc() if desc else col.asc())

    # Stable ordering (avoid pagination inconsistencies)
    if stable_key and stable_key in allowed and stable_key not in seen:
        order_clauses.append(allowed[stable_key].asc())

    return order_clauses