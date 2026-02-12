from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Dict, List, Tuple, Optional

from fastapi import HTTPException
from sqlalchemy import asc, desc, func, Select
from sqlalchemy.orm import Session


@dataclass
class PaginationResult:
    items: list
    total: int
    total_pages: int


def apply_pagination(db: Session, query: Select, page: int, page_size: int) -> PaginationResult:
    # total count
    count_q = query.with_only_columns(func.count()).order_by(None)
    total = db.execute(count_q).scalar_one()
    total_pages = max(1, ceil(total / page_size)) if page_size > 0 else 1

    offset = (page - 1) * page_size
    rows = db.execute(query.offset(offset).limit(page_size)).scalars().all()
    return PaginationResult(items=rows, total=total, total_pages=total_pages)


def parse_sort(sort: Optional[str], allowed_fields: Dict[str, object]) -> List[Tuple[object, str]]:
    """
    sort supports multiple fields, comma-separated:
      sort=driver_name,-created_at
    """
    if not sort:
        return []

    parts = [p.strip() for p in sort.split(",") if p.strip()]
    if not parts:
        return []

    parsed: List[Tuple[object, str]] = []
    for raw in parts:
        direction = "asc"
        field = raw

        if raw.startswith("-"):
            direction = "desc"
            field = raw[1:].strip()

        if field not in allowed_fields:
            raise HTTPException(status_code=422, detail=f"Invalid sort field: {field}")

        parsed.append((allowed_fields[field], direction))

    return parsed


def apply_sort(query: Select, sort_fields: List[Tuple[object, str]]) -> Select:
    for col, direction in sort_fields:
        query = query.order_by(desc(col) if direction == "desc" else asc(col))
    return query