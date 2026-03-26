from __future__ import annotations

import csv
import io

from db.repository import Expense


def export_csv(expenses: list[Expense]) -> io.BytesIO:
    """Export expenses to a CSV file (UTF-8 with BOM for Excel compatibility)."""
    text_buf = io.StringIO()
    writer = csv.writer(text_buf)
    writer.writerow(["Дата", "Сумма", "Валюта", "Описание", "Категория", "Магазин"])

    for e in expenses:
        writer.writerow([
            e.created_at[:10],
            f"{e.amount:.2f}",
            e.currency,
            e.description,
            e.category_name or "Другое",
            e.store or "",
        ])

    # UTF-8 BOM for Excel
    buf = io.BytesIO()
    buf.write(b"\xef\xbb\xbf")
    buf.write(text_buf.getvalue().encode("utf-8"))
    buf.seek(0)
    return buf
