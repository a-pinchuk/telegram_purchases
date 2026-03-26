from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import aiosqlite

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
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        await self._db.commit()
        await self._load_default_mappings()

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    # ── Users ──────────────────────────────────────────────

    async def ensure_user(
        self, user_id: int, first_name: str | None, username: str | None, default_currency: str = "EUR"
    ) -> None:
        assert self._db
        await self._db.execute(
            """INSERT INTO users (id, first_name, username, default_currency)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET first_name=excluded.first_name, username=excluded.username""",
            (user_id, first_name, username, default_currency),
        )
        await self._db.commit()

    async def get_user_currency(self, user_id: int) -> str:
        assert self._db
        async with self._db.execute("SELECT default_currency FROM users WHERE id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row["default_currency"] if row else "EUR"

    async def set_user_currency(self, user_id: int, currency: str) -> None:
        assert self._db
        await self._db.execute("UPDATE users SET default_currency=? WHERE id=?", (currency, user_id))
        await self._db.commit()

    # ── Categories ─────────────────────────────────────────

    async def get_categories(self) -> list[tuple[int, str, str]]:
        assert self._db
        async with self._db.execute("SELECT id, name, icon FROM categories ORDER BY name") as cur:
            return [(row["id"], row["name"], row["icon"]) async for row in cur]

    async def get_category_id_by_name(self, name: str) -> int | None:
        assert self._db
        async with self._db.execute("SELECT id FROM categories WHERE name=?", (name,)) as cur:
            row = await cur.fetchone()
            return row["id"] if row else None

    # ── Store mappings ─────────────────────────────────────

    async def find_category_by_store(self, description: str) -> tuple[int, str, str, str] | None:
        """Returns (category_id, category_name, category_icon, matched_pattern) or None."""
        assert self._db
        normalized = description.lower().strip()

        async with self._db.execute(
            """SELECT sm.pattern, sm.category_id, c.name, c.icon
               FROM store_mappings sm JOIN categories c ON sm.category_id = c.id
               WHERE sm.pattern = ?""",
            (normalized,),
        ) as cur:
            row = await cur.fetchone()
            if row:
                return row["category_id"], row["name"], row["icon"], row["pattern"]

        async with self._db.execute(
            """SELECT sm.pattern, sm.category_id, c.name, c.icon
               FROM store_mappings sm JOIN categories c ON sm.category_id = c.id""",
        ) as cur:
            async for row in cur:
                pattern = row["pattern"]
                if pattern in normalized or normalized in pattern:
                    return row["category_id"], row["name"], row["icon"], pattern

        return None

    async def add_store_mapping(self, pattern: str, category_id: int, source: str = "manual") -> None:
        assert self._db
        await self._db.execute(
            """INSERT INTO store_mappings (pattern, category_id, source)
               VALUES (?, ?, ?)
               ON CONFLICT(pattern) DO UPDATE SET category_id=excluded.category_id, source=excluded.source""",
            (pattern.lower().strip(), category_id, source),
        )
        await self._db.commit()

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
        assert self._db
        async with self._db.execute(
            """INSERT INTO expenses (user_id, amount, currency, description, category_id, store)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, amount, currency, description, category_id, store),
        ) as cur:
            expense_id = cur.lastrowid
        await self._db.commit()
        return expense_id  # type: ignore[return-value]

    async def delete_expense(self, expense_id: int, user_id: int) -> bool:
        assert self._db
        async with self._db.execute(
            "DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id)
        ) as cur:
            await self._db.commit()
            return cur.rowcount > 0

    async def get_last_expense(self, user_id: int) -> Expense | None:
        assert self._db
        async with self._db.execute(
            """SELECT e.*, c.name as category_name, COALESCE(c.icon, '') as category_icon
               FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
               WHERE e.user_id=? ORDER BY e.created_at DESC LIMIT 1""",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            return self._row_to_expense(row) if row else None

    async def update_expense_category(self, expense_id: int, category_id: int) -> None:
        assert self._db
        await self._db.execute("UPDATE expenses SET category_id=? WHERE id=?", (category_id, expense_id))
        await self._db.commit()

    async def get_expense_by_id(self, expense_id: int) -> Expense | None:
        assert self._db
        async with self._db.execute(
            """SELECT e.*, c.name as category_name, COALESCE(c.icon, '') as category_icon
               FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
               WHERE e.id=?""",
            (expense_id,),
        ) as cur:
            row = await cur.fetchone()
            return self._row_to_expense(row) if row else None

    async def get_expenses(
        self, user_id: int, start: str, end: str, currency: str | None = None
    ) -> list[Expense]:
        assert self._db
        query = """SELECT e.*, c.name as category_name, COALESCE(c.icon, '') as category_icon
                   FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
                   WHERE e.user_id=? AND e.created_at >= ? AND e.created_at < ?"""
        params: list = [user_id, start, end]
        if currency:
            query += " AND e.currency=?"
            params.append(currency)
        query += " ORDER BY e.created_at DESC"

        async with self._db.execute(query, params) as cur:
            return [self._row_to_expense(row) async for row in cur]

    # ── Aggregation ────────────────────────────────────────

    async def get_category_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[CategoryTotal]:
        assert self._db
        async with self._db.execute(
            """SELECT COALESCE(c.name, 'Другое') as name, COALESCE(c.icon, '📦') as icon,
                      SUM(e.amount) as total, COUNT(*) as cnt
               FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
               WHERE e.user_id=? AND e.created_at >= ? AND e.created_at < ? AND e.currency=?
               GROUP BY c.name ORDER BY total DESC""",
            (user_id, start, end, currency),
        ) as cur:
            rows = [CategoryTotal(name=r["name"], icon=r["icon"], total=r["total"], count=r["cnt"]) async for r in cur]

        grand_total = sum(r.total for r in rows)
        for r in rows:
            r.percentage = (r.total / grand_total * 100) if grand_total else 0
        return rows

    async def get_daily_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[DailyTotal]:
        assert self._db
        async with self._db.execute(
            """SELECT date(e.created_at) as day, SUM(e.amount) as total
               FROM expenses e
               WHERE e.user_id=? AND e.created_at >= ? AND e.created_at < ? AND e.currency=?
               GROUP BY day ORDER BY day""",
            (user_id, start, end, currency),
        ) as cur:
            return [DailyTotal(date=r["day"], total=r["total"]) async for r in cur]

    async def get_monthly_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[tuple[str, float]]:
        assert self._db
        async with self._db.execute(
            """SELECT strftime('%Y-%m', e.created_at) as month, SUM(e.amount) as total
               FROM expenses e
               WHERE e.user_id=? AND e.created_at >= ? AND e.created_at < ? AND e.currency=?
               GROUP BY month ORDER BY month""",
            (user_id, start, end, currency),
        ) as cur:
            return [(r["month"], r["total"]) async for r in cur]

    async def get_monthly_category_totals(
        self, user_id: int, start: str, end: str, currency: str
    ) -> list[tuple[str, str, str, float]]:
        assert self._db
        async with self._db.execute(
            """SELECT strftime('%Y-%m', e.created_at) as month,
                      COALESCE(c.name, 'Другое') as name,
                      COALESCE(c.icon, '📦') as icon,
                      SUM(e.amount) as total
               FROM expenses e LEFT JOIN categories c ON e.category_id = c.id
               WHERE e.user_id=? AND e.created_at >= ? AND e.created_at < ? AND e.currency=?
               GROUP BY month, c.name ORDER BY month, total DESC""",
            (user_id, start, end, currency),
        ) as cur:
            return [(r["month"], r["name"], r["icon"], r["total"]) async for r in cur]

    async def get_currencies_used(self, user_id: int, start: str, end: str) -> list[str]:
        assert self._db
        async with self._db.execute(
            """SELECT DISTINCT currency FROM expenses
               WHERE user_id=? AND created_at >= ? AND created_at < ? ORDER BY currency""",
            (user_id, start, end),
        ) as cur:
            return [row["currency"] async for row in cur]

    # ── Private ────────────────────────────────────────────

    async def _load_default_mappings(self) -> None:
        assert self._db
        if not DEFAULT_MAPPINGS_PATH.exists():
            return

        async with self._db.execute("SELECT COUNT(*) as cnt FROM store_mappings") as cur:
            row = await cur.fetchone()
            if row and row["cnt"] > 0:
                return

        data = json.loads(DEFAULT_MAPPINGS_PATH.read_text(encoding="utf-8"))
        for category_name, info in data.items():
            icon = info["icon"]
            stores = info["stores"]

            await self._db.execute(
                "INSERT OR IGNORE INTO categories (name, icon) VALUES (?, ?)",
                (category_name, icon),
            )
            async with self._db.execute("SELECT id FROM categories WHERE name=?", (category_name,)) as cur:
                cat_row = await cur.fetchone()
                cat_id = cat_row["id"]

            for store in stores:
                await self._db.execute(
                    "INSERT OR IGNORE INTO store_mappings (pattern, category_id, source) VALUES (?, ?, 'default')",
                    (store.lower().strip(), cat_id),
                )
        await self._db.commit()

    @staticmethod
    def _row_to_expense(row: aiosqlite.Row) -> Expense:
        return Expense(
            id=row["id"],
            user_id=row["user_id"],
            amount=row["amount"],
            currency=row["currency"],
            description=row["description"],
            category_id=row["category_id"],
            category_name=row["category_name"],
            category_icon=row["category_icon"],
            store=row["store"],
            created_at=row["created_at"],
        )
