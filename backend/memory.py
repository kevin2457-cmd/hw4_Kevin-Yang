"""Persistent chat history for logged-in shoppers, stored in the existing chat_messages table."""

import json

from db import get_db
from models import MAX_PRODUCT_CARDS, ChatHistoryMessage, ChatReply, ChatTurn
from tools import build_product_cards

MAX_HISTORY_MESSAGES = 50  # shown in the widget
MAX_AGENT_HISTORY_MESSAGES = 20  # sent to the model as conversation context


def _product_ids(products_json: str | None) -> list[str]:
    """Pull product ids out of a saved products_json. Handles both the seeded rows (full
    product dicts with inventory) and rows this app writes (ProductCard dicts)."""
    if not products_json:
        return []
    try:
        items = json.loads(products_json)
    except json.JSONDecodeError:
        return []
    if not isinstance(items, list):
        return []
    return [
        item["product_id"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("product_id"), str)
    ]


def load_history(user_id: int, limit: int = MAX_HISTORY_MESSAGES) -> list[ChatHistoryMessage]:
    """The user's most recent messages, oldest first. Cards are rebuilt from the saved
    product ids against the current catalogue, so the prices and stock shown are current."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [
        ChatHistoryMessage(
            role=row["role"],
            content=row["content"],
            products=build_product_cards(_product_ids(row["products_json"])) if row["role"] == "assistant" else [],
            created_at=row["created_at"],
        )
        for row in reversed(rows)
        if row["role"] in ("user", "assistant")
    ]


def history_for_agent(user_id: int) -> list[ChatTurn]:
    """Recent saved turns in the shape the agent expects (text + card ids only)."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, MAX_AGENT_HISTORY_MESSAGES),
        ).fetchall()
    return [
        ChatTurn(role=r["role"], content=r["content"], product_ids=_product_ids(r["products_json"])[:MAX_PRODUCT_CARDS])
        for r in reversed(rows)
        if r["role"] in ("user", "assistant")
    ]


def save_exchange(user_id: int, user_message: str, reply: ChatReply) -> None:
    """Store the shopper's message and the assistant's reply (with its cards) in one transaction."""
    products_json = json.dumps([p.model_dump() for p in reply.products]) if reply.products else None
    with get_db() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
            (user_id, user_message),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, reply.reply, products_json),
        )
        conn.commit()
