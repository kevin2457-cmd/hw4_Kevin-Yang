"""Campus Customs FastAPI backend.

Problem 3: serve catalogue products, inventory, and product images from
`data/campus_customs.db` to the React frontend.
Problem 4: account creation and login (routes in auth.py).
Problem 5: POST /api/chat -> PydanticAI shopping assistant (agent.py).
Problem 8: saved chat history for logged-in users (memory.py) + page context.

Run from this folder:  uvicorn main:app --reload --port 8000
"""

from pathlib import Path

from dotenv import load_dotenv

# Load settings (PORTKEY_API_KEY, AUTH_SECRET, ...) before other modules read them.
# hw4/.env wins; the class-folder .env (one level above hw4) is the fallback.
_HW_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_HW_DIR / ".env")
load_dotenv(_HW_DIR.parent / ".env")

import logging  # noqa: E402

from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

import auth  # noqa: E402
import memory  # noqa: E402
from agent import AgentConfigError, run_chat  # noqa: E402
from db import DATA_DIR, SIZE_ORDER, get_db, inventory_for, product_from_row  # noqa: E402
from models import (  # noqa: E402
    ChatHistory,
    ChatReply,
    ChatRequest,
    CurrentProduct,
    CustomerContext,
    ShopperDeps,
)

logger = logging.getLogger("campus_customs")

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product images live in data/products/; the DB stores paths like
# "products/<slug>.jpg", so they are served at /media/products/<slug>.jpg.
# Only the products folder is mounted so the .db file is never downloadable.
app.mount("/media/products", StaticFiles(directory=DATA_DIR / "products"), name="media")

app.include_router(auth.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def list_products() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        stock = dict(
            conn.execute("SELECT product_id, SUM(quantity) FROM inventory GROUP BY product_id").fetchall()
        )
        # Sizes with quantity > 0, so the Products page can filter by "available in my size".
        sizes_in_stock: dict[str, set[str]] = {}
        for pid, size in conn.execute("SELECT product_id, size FROM inventory WHERE quantity > 0"):
            sizes_in_stock.setdefault(pid, set()).add(size)
    return [
        {
            **product_from_row(r),
            "total_stock": stock.get(r["product_id"], 0),
            "in_stock_sizes": [s for s in SIZE_ORDER if s in sizes_in_stock.get(r["product_id"], set())],
        }
        for r in rows
    ]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        inventory = inventory_for(conn, product_id)
    return {
        **product_from_row(row),
        "inventory": inventory,
        "total_stock": sum(i["quantity"] for i in inventory),
    }


def _current_product(product_id: str | None) -> CurrentProduct | None:
    """Resolve the page's product_id against the DB; unknown ids are ignored."""
    if not product_id:
        return None
    with get_db() as conn:
        row = conn.execute("SELECT product_id, name FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    return CurrentProduct(product_id=row["product_id"], name=row["name"]) if row else None


@app.get("/api/chat/history", response_model=ChatHistory)
def chat_history(user: auth.UserOut = Depends(auth.require_user)) -> ChatHistory:
    """The logged-in shopper's own saved messages (identity from the token only)."""
    return ChatHistory(messages=memory.load_history(user.id))


@app.post("/api/chat", response_model=ChatReply)
async def chat(body: ChatRequest, user: auth.UserOut | None = Depends(auth.optional_user)) -> ChatReply:
    deps = ShopperDeps(
        customer=CustomerContext(
            user_id=user.id, first_name=user.first_name, last_name=user.last_name, email=user.email
        )
        if user
        else None,
        current_product=_current_product(body.current_product_id),
    )
    # Logged-in: conversation context comes from the saved history in the DB, not the browser.
    # Guest: use the in-browser history the widget sent.
    history = memory.history_for_agent(user.id) if user else body.history
    try:
        reply = await run_chat(body.message, history, deps)
    except AgentConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        logger.exception("Chat agent failed")
        raise HTTPException(
            status_code=502,
            detail="The shopping assistant couldn't answer right now. Please try again in a moment.",
        )
    if user:
        memory.save_exchange(user.id, body.message, reply)
        reply.saved = True
    return reply
