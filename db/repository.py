from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import asyncpg

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
DEFAULT_MAPPINGS_PATH = Path(__file__).parent.parent / "data" / "store_mappings.json"


@dataclass
class Expense:
    id: int
    user_id: int
    amount: float
    currency: str
    description: str
    category_id: int | None
    category_name: str | None
    category_icon: str
    store: str | None
    created_at: str


@dataclass
class CategoryTotal:
    name: str
    icon: str
    total: float
    count: int
    percentage: float = 0.0


@dataclass
class DailyTotal:
    date: str
    total: float
    category_name: str | None = None


class Repository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._pool: asyncpg.Pool | None = None

    async def init(self) -> None:
        self._pool = await asyncpg.create_pool(self._database_url, min_size=1, max_size=5)
        async with self._pool.acquire() as conn:
            await conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
        await self._load_default_mappings()

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    # ── Users ──────────────────────────────────────────────

    async def ensure_user(
        self, user_id: int, first_name: str | None, username: str | None, default_currency: str = "EUR"
    ) -> None:
        assert self._pool
        async with self._pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO users (id, first_name, username, default_currency)
                   VALUES ($1, $2, $3, $4)
                   ON CONFLICT(id) DO UPDATE SET first_name=EXCLUDED.first_name, username=EXCLUDED.username""",
                user_id, first_name, username, default_currency,
            )

    async def get_user_currency(self, user_id: int) -> str:
        assert self._pool
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT default_currency FROM users WHERE id=$1", user_id)
            return row["default_currency"] if row else "EUR"

    async def set_user_currency(self, user_id: int, currency: str) -> None:
        assert self._pool
        async with self._pool.acquire() as conn:
            await conn.execute("UPDATE users SET default_currency=$1 WHERE id=$2", currency, user_id)

    # ── Categories ─────────────────────────────────────────

    async def get_categories(self) -> list[tuple[int, str, str]]:
        assert self._pool
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, name, icon FROM categories ORDER BY name")
            return [(row["id"], row["name"], row["icon"]) for row in rows]

    async def get_category_id_by_name(self, name: str) -> int | None:
        assert self._pool
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT id FROM categories WHERE name=$1", name)
            return row["id"] if row else None

    # ── Store mappings ─────────────────────────────────────

    async def find_category_by_store(self, description: str) -> tuple[int, str, str, str] | None:
        """Returns (category_id, category_name, category_icon, matched_pattern) or None."""
        assert self._pool
        normalized = description.lower().strip()

        async with self._pool.acquire() as conn:
            # Exact match
            row = await conn.fetchrow(
                """SELECT sm.pattern, sm.category_id, c.name, c.icon
                   FROM store_mappings sm JOIN categories c ON sm.category_id = c.id
                   WHERE sm.pattern = $1""",
                normalized,
            )
            if row:
                return row["category_id"], row["name"], row["icon"], row["pattern"]

            # Substring match
            rows = await conn.fetch(
                """SELECT sm.pattern, sm.category_id, c.name, c.icon
                   FROM store_mappings sm JOIN categories c ON sm.category_id = c.id""",
            )
            for row in rows:
                pattern = row["pattern"]
                if pattern in normalized or normalized in pattern:
                    return row["category_id"], row["name"], row["icon"], pattern

        return None

    async def add_store_mapping(self, pattern: str, category_id: int, source: str = "manual") -> None:
        assert self._pool
        async with self._pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO store_mappings (pattern, category_id, source)
                   VALUES ($1, $2, $3)
                   ON CONFLICT(pattern) DO UPDATE SET category_id=EXCLUDED.category_id, source=EXCLUDED.source""",
                pattern.lower().strip(), category_id, source,
            )

    # ── Expenses ───────────────────────────────────────────

    async def add_expense(
        self,
        user_id: int,
        amount: float,
        currency: str,
        description: str,
        category_id: int | None = None,
        store: str | None = None,
    ) -> int:
        assert self._pool
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO expenses (user_id, amount, currency, description, category_id, store)
                   VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
                user_id, amount, currency, description, category_id, store,
            )
            return row["id"]

    async def delete_expense(self, expense_id: int, user_id: int) -> bool:
        assert self._pool
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM expenses WHERE id=$1 AND user_id=$2", expense_id, user_id
            )
            return result == "DELETE 1"

    async def get_last_expense(self, user_id: int) -> Expense | None:
        assert self._pool
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT e.*, c.name as category_name, COALESCE(c.icon, '') as category_icon
                   FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
                   WHERE e.user_id=$1 ORDER BY e.created_at DESC LIMIT 1""",
                user_id,
            )
            return self._row_to_expense(row) if row else None

    async def update_expense_category(self, expense_id: int, category_id: int) -> None:
        assert self._pool
        async with self._pool.acquire() as conn:
            await conn.execute("UPDATE expenses SET category_id=$1 WHERE id=$2", category_id, expense_id)

    async def get_expense_by_id(self, expense_id: int) -> Expense | None:
        assert self._pool
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT e.*, c.name as category_name, COALESCE(c.icon, '') as category_icon
                   FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
                   WHERE e.id=$1""",
                expense_id,
            )
            return self._row_to_expense(row) if row else None

    async def get_expenses(
        self, user_id: int, start: str, end: str, currency: str | None = None
    ) -> list[Expense]:
        assert self._pool
        async with self._pool.acquire() as conn:
            if currency:
                rows = await conn.fetch(
                    """SELECT e.*, c.name as category_name, COALESCE(c.icon, '') as category_icon
                       FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
                       WHERE e.user_id=$1 AND e.created_at >= $2 AND e.created_at < $3 AND e.currency=$4
                       ORDER BY e.created_at DESC""",
                    user_id, start, end, currency,
                )
            else:
                rows = await conn.fetch(
                    """SELECT e.*, c.name as category_name, COALESCE(c.icon, '') as category_icon
                       FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
                       WHERE e.user_id=$1 AND e.created_at >= $2 AND e.created_at < $3
                       ORDER BY e.created_at DESC""",
                    user_id, start, end,
                )
            return [self._row_to_expense(row) for row in rows]

    # ── Aggregation ────────────────────────────────────────

    async def get_category_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[CategoryTotal]:
        assert self._pool
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT COALESCE(c.name, 'Другое') as name, COALESCE(c.icon, '📦') as icon,
                          SUM(e.amount) as total, COUNT(*) as cnt
                   FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
                   WHERE e.user_id=$1 AND e.created_at >= $2 AND e.created_at < $3 AND e.currency=$4
                   GROUP BY c.name, c.icon ORDER BY total DESC""",
                user_id, start, end, currency,
            )
            result = [CategoryTotal(name=r["name"], icon=r["icon"], total=float(r["total"]), count=r["cnt"]) for r in rows]

        grand_total = sum(r.total for r in result)
        for r in result:
            r.percentage = (r.total / grand_total * 100) if grand_total else 0
        return result

    async def get_daily_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[DailyTotal]:
        assert self._pool
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT e.created_at::date::text as day, SUM(e.amount) as total
                   FROM expenses e
                   WHERE e.user_id=$1 AND e.created_at >= $2 AND e.created_at < $3 AND e.currency=$4
                   GROUP BY day ORDER BY day""",
                user_id, start, end, currency,
            )
            return [DailyTotal(date=r["day"], total=float(r["total"])) for r in rows]

    async def get_monthly_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[tuple[str, float]]:
        assert self._pool
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT to_char(e.created_at, 'YYYY-MM') as month, SUM(e.amount) as total
                   FROM expenses e
                   WHERE e.user_id=$1 AND e.created_at >= $2 AND e.created_at < $3 AND e.currency=$4
                   GROUP BY month ORDER BY month""",
                user_id, start, end, currency,
            )
            return [(r["month"], float(r["total"])) for r in rows]

    async def get_monthly_category_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[tuple[str, str, str, float]]:
        assert self._pool
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT to_char(e.created_at, 'YYYY-MM') as month,
                          COALESCE(c.name, 'Другое') as name,
                          COALESCE(c.icon, '📦') as icon,
                          SUM(e.amount) as total
                   FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
                   WHERE e.user_id=$1 AND e.created_at >= $2 AND e.created_at < $3 AND e.currency=$4
                   GROUP BY month, c.name, c.icon ORDER BY month, total DESC""",
                user_id, start, end, currency,
            )
            return [(r["month"], r["name"], r["icon"], float(r["total"])) for r in rows]

    async def get_currencies_used(self, user_id: int, start: str, end: str) -> list[str]:
        assert self._pool
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT DISTINCT currency FROM expenses
                   WHERE user_id=$1 AND created_at >= $2 AND created_at < $3 ORDER BY currency""",
                user_id, start, end,
            )
            return [row["currency"] for row in rows]

    # ── Private ────────────────────────────────────────────

    async def _load_default_mappings(self) -> None:
        assert self._pool
        if not DEFAULT_MAPPINGS_PATH.exists():
            return

        async with self._pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM store_mappings")
            if count > 0:
                return

            data = json.loads(DEFAULT_MAPPINGS_PATH.read_text(encoding="utf-8"))
            for category_name, info in data.items():
                icon = info["icon"]
                stores = info["stores"]

                await conn.execute(
                    "INSERT INTO categories (name, icon) VALUES ($1, $2) ON CONFLICT(name) DO NOTHING",
                    category_name, icon,
                )
                cat_row = await conn.fetchrow("SELECT id FROM categories WHERE name=$1", category_name)
                cat_id = cat_row["id"]

                for store in stores:
                    await conn.execute(
                        "INSERT INTO store_mappings (pattern, category_id, source) VALUES ($1, $2, 'default') ON CONFLICT(pattern) DO NOTHING",
                        store.lower().strip(), cat_id,
                    )

    @staticmethod
    def _row_to_expense(row: asyncpg.Record) -> Expense:
        return Expense(
            id=row["id"],
            user_id=row["user_id"],
            amount=float(row["amount"]),
            currency=row["currency"],
            description=row["description"],
            category_id=row["category_id"],
            category_name=row["category_name"],
            category_icon=row["category_icon"],
            store=row["store"],
            created_at=str(row["created_at"]),
        )
