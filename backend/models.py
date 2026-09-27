"""Pydantic types for the chat API and the Campus Customs agent."""

from typing import Literal

from pydantic import BaseModel, Field

MAX_MESSAGE_CHARS = 2000


# ---------- chat API ----------

MAX_PRODUCT_CARDS = 6


class ChatTurn(BaseModel):
    """One earlier message in the current (in-browser) conversation."""

    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_MESSAGE_CHARS * 4)
    # Ids of the product cards shown with an assistant turn, so "the second one" /
    # "that hoodie" can be resolved on later turns.
    product_ids: list[str] = Field(default_factory=list, max_length=MAX_PRODUCT_CARDS)


class ChatRequest(BaseModel):
    """What the React chat widget POSTs to /api/chat.

    Logged-in shoppers are identified by the Authorization header, not by this body; their
    history is loaded from the DB, so `history` is only used for guests."""

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    history: list[ChatTurn] = Field(default_factory=list)
    # product_id of the product detail page the shopper has open, if any.
    current_product_id: str | None = Field(default=None, max_length=200)


class AgentOutput(BaseModel):
    """The agent's structured final answer (PydanticAI output_type)."""

    reply: str = Field(description="The message shown to the shopper.")
    product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "product_id values (from tool results) of the products the reply recommends or is "
            f"about, in the order mentioned; at most {MAX_PRODUCT_CARDS}. Empty when the reply "
            "is not about specific products or nothing matched."
        ),
    )


class ProductCard(BaseModel):
    """A product shown as a card in the chat. Every value is read from the DB by the backend."""

    product_id: str
    name: str
    garment_type: str
    category: str
    price: float
    image_url: str
    colors: list[str]
    total_stock: int
    in_stock_sizes: list[str]


class ChatReply(BaseModel):
    """What /api/chat returns to the widget."""

    reply: str
    tools_used: list[str] = Field(default_factory=list)
    products: list[ProductCard] = Field(default_factory=list)
    saved: bool = False  # True when the exchange was stored in the shopper's chat history


class ChatHistoryMessage(BaseModel):
    """One saved message from chat_messages, with its product cards restored."""

    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard] = Field(default_factory=list)
    created_at: str


class ChatHistory(BaseModel):
    """GET /api/chat/history: the logged-in shopper's saved messages, oldest first."""

    messages: list[ChatHistoryMessage]


# ---------- agent deps (who is chatting, what page they are on) ----------

class CustomerContext(BaseModel):
    """The logged-in shopper, from the verified login token."""

    user_id: int
    first_name: str
    last_name: str
    email: str


class CurrentProduct(BaseModel):
    """The product page the shopper has open (looked up in the DB from its id)."""

    product_id: str
    name: str


class ShopperDeps(BaseModel):
    """PydanticAI deps for one chat run. None = guest / not on a product page."""

    customer: CustomerContext | None = None
    current_product: CurrentProduct | None = None


# ---------- tool results ----------

class CategoryCount(BaseModel):
    category: str
    product_count: int
    example_products: list[str]


class CatalogueOverview(BaseModel):
    """Returned by the list_categories tool."""

    total_products: int
    categories: list[CategoryCount]


class ProductSummary(BaseModel):
    """One search hit: enough to name, compare, and price an item without a second call."""

    product_id: str
    name: str
    garment_type: str
    category: str
    colors: list[str]
    price: float


class ProductSearchResult(BaseModel):
    """Returned by search_products."""

    query: str
    total_matches: int
    returned: int
    products: list[ProductSummary]
    note: str = ""


class ProductDetails(BaseModel):
    """Returned by get_product_details. `found=False` means the id is not in the catalogue."""

    found: bool
    product_id: str
    name: str | None = None
    garment_type: str | None = None
    category: str | None = None
    description: str | None = None
    colors: list[str] = Field(default_factory=list)
    price: float | None = None
    image_url: str | None = None
    note: str = ""


class ComparedProduct(BaseModel):
    """One column of a side-by-side comparison; every field is from the DB."""

    product_id: str
    name: str
    garment_type: str
    category: str
    price: float
    colors: list[str]
    total_stock: int
    in_stock_sizes: list[str]
    out_of_stock_sizes: list[str]


class ProductComparison(BaseModel):
    """Returned by compare_products: DB facts side by side, plus computed differences."""

    products: list[ComparedProduct]
    not_found: list[str] = Field(default_factory=list)
    cheapest: list[str] = Field(default_factory=list, description="product_id(s) with the lowest price")
    price_difference: float | None = Field(default=None, description="highest minus lowest price, USD")
    colors_in_common: list[str] = Field(default_factory=list)
    sizes_in_stock_for_all: list[str] = Field(default_factory=list)
    note: str = ""


class SizeStock(BaseModel):
    size: str
    quantity: int
    in_stock: bool


class InventoryResult(BaseModel):
    """Returned by get_inventory: real quantities from the inventory table."""

    found: bool
    product_id: str
    name: str | None = None
    sizes: list[SizeStock] = Field(default_factory=list)
    total_stock: int = 0
    in_stock_sizes: list[str] = Field(default_factory=list)
    out_of_stock_sizes: list[str] = Field(default_factory=list)
    requested_size: str | None = None
    requested_size_quantity: int | None = None
    note: str = ""
