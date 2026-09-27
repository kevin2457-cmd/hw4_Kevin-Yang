"""Shared SQLite helpers for the API routes (main.py) and the agent tools (tools.py)."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def category_for(garment_type: str) -> str:
    """Group the free-text garment_type values into a few shop categories."""
    g = garment_type.lower()
    if "hood" in g:
        return "Hoodies"
    if "quarter-zip" in g:
        return "Quarter-Zips"
    if "jacket" in g:
        return "Jackets"
    if "t-shirt" in g:
        return "T-Shirts"
    if "long-sleeve" in g:
        return "Long Sleeves"
    if "crew" in g or "sweatshirt" in g:
        return "Crewnecks"
    return "Other"


def product_from_row(row: sqlite3.Row) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "category": category_for(row["garment_type"]),
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_url": f"/media/{row['image_file_path']}",
        "price": row["price"],
    }


def inventory_for(conn: sqlite3.Connection, product_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    rows = sorted(rows, key=lambda r: SIZE_ORDER.index(r["size"]) if r["size"] in SIZE_ORDER else 99)
    return [{"size": r["size"], "quantity": r["quantity"]} for r in rows]
