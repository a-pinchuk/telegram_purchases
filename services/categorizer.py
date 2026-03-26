from __future__ import annotations

from dataclasses import dataclass

from db.repository import Repository


@dataclass
class CategoryResult:
    category_id: int
    category_name: str
    category_icon: str
    matched_pattern: str


async def categorize(description: str, repo: Repository) -> CategoryResult | None:
    """Look up a category for the given description using store mappings."""
    if not description:
        return None

    result = await repo.find_category_by_store(description)
    if result:
        cat_id, cat_name, cat_icon, pattern = result
        return CategoryResult(
            category_id=cat_id,
            category_name=cat_name,
            category_icon=cat_icon,
            matched_pattern=pattern,
        )

    return None
