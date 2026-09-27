"""Tools the Campus Customs agent can call. All data comes from campus_customs.db."""

import json
import re
from collections import defaultdict

from db import SIZE_ORDER, category_for, get_db, inventory_for, product_from_row
from models import (
    MAX_PRODUCT_CARDS,
    CatalogueOverview,
    CategoryCount,
    ComparedProduct,
    InventoryResult,
    ProductComparison,
    ProductCard,
    ProductDetails,
    ProductSearchResult,
    ProductSummary,
    SizeStock,
)

EXAMPLES_PER_CATEGORY = 3
MAX_SEARCH_RESULTS = 12
MAX_COMPARE = 4

# Words shoppers use for each shop category (see db.category_for). Matching a category
# word filters by category, which smooths over inconsistent garment_type text such as
# "hoodie" / "pullover hoodie" / "hooded sweatshirt".
CATEGORY_WORDS = {
    "Hoodies": ["hoodie", "hoody", "hoodies", "hooded", "hood"],
    "Crewnecks": ["crewneck", "crew", "crewnecks", "sweatshirt", "sweatshirts", "sweater", "sweaters", "mockneck"],
    "T-Shirts": ["t-shirt", "tshirt", "tee", "tees", "t-shirts", "tshirts", "shirt", "shirts"],
    "Quarter-Zips": ["quarter-zip", "quarterzip"],
    "Jackets": ["jacket", "jackets", "fleece", "bomber", "coat", "coats"],
    "Long Sleeves": ["long-sleeve", "longsleeve", "long-sleeves"],
}
WORD_TO_CATEGORY = {w: cat for cat, words in CATEGORY_WORDS.items() for w in words}
# Generic words that only pick a category when nothing more specific was said:
# "hooded sweatshirt" -> Hoodies (not Crewnecks), "long sleeve shirt" -> Long Sleeves.
WEAK_CATEGORY_WORDS = {"sweatshirt", "sweatshirts", "sweater", "sweaters", "shirt", "shirts"}

# Words that carry no search meaning here (every product is Yale / Campus Customs merch).
STOPWORDS = {
    "a", "an", "and", "any", "are", "do", "does", "for", "have", "i", "in", "is", "it", "me",
    "of", "on", "or", "show", "some", "the", "to", "what", "which", "with", "you", "your",
    "yale", "campus", "customs", "product", "products", "item", "items", "gear", "merch",
    "apparel", "clothing", "clothes", "looking", "want", "need", "got", "sell", "carry",
    # budget / size words: those constraints go in search_products' filter arguments
    "under", "below", "less", "than", "over", "above", "cheap", "cheaper", "price", "budget",
    "size", "sizes", "stock", "available",
}
SYNONYMS = {"grey": "gray"}

SIZE_ALIASES = {
    "xs": "XS", "extra small": "XS", "x-small": "XS", "xsmall": "XS",
    "s": "S", "small": "S", "sm": "S",
    "m": "M", "medium": "M", "med": "M",
    "l": "L", "large": "L", "lg": "L",
    "xl": "XL", "extra large": "XL", "x-large": "XL", "xlarge": "XL",
    "xxl": "XXL", "2xl": "XXL", "xx-large": "XXL", "xxlarge": "XXL", "extra extra large": "XXL",
}


def _normalize_query(query: str) -> str:
    q = query.lower()
    q = re.sub(r"\b(quarter|1/4|1-4)[\s-]*zip", "quarter-zip", q)
    q = re.sub(r"\bt[\s-]?shirts?\b", "t-shirt", q)
    q = re.sub(r"\blong[\s-]?sleeves?\b", "long-sleeve", q)
    q = re.sub(r"\bcrew[\s-]?necks?\b", "crewneck", q)
    return q


def _tokens(query: str) -> tuple[set[str], list[str]]:
    """Split a query into (categories mentioned, other keywords)."""
    categories: set[str] = set()
    weak_categories: set[str] = set()
    keywords: list[str] = []
    for word in re.findall(r"[$a-z0-9/'.-]+", _normalize_query(query)):
        word = word.strip("'-")
        if not word or word in STOPWORDS or word.startswith("$") or word in SIZE_ALIASES:
            continue
        if word in WORD_TO_CATEGORY:
            (weak_categories if word in WEAK_CATEGORY_WORDS else categories).add(WORD_TO_CATEGORY[word])
            continue
        word = SYNONYMS.get(word, word)
        if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]  # simple plural -> singular ("bulldogs" -> "bulldog")
        keywords.append(word)
    return categories or weak_categories, keywords


def _summary(row) -> ProductSummary:
    return ProductSummary(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        category=category_for(row["garment_type"]),
        colors=json.loads(row["colors"]),
        price=row["price"],
    )


def list_categories() -> CatalogueOverview:
    """List the kinds of clothing Campus Customs sells, with how many products are in each
    category and a few example product names. Use this when the shopper asks what the store
    carries or which types of items are available. It does not include prices or stock."""
    with get_db() as conn:
        rows = conn.execute("SELECT name, garment_type FROM catalogue ORDER BY name").fetchall()

    by_category: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_category[category_for(row["garment_type"])].append(row["name"])

    return CatalogueOverview(
        total_products=len(rows),
        categories=[
            CategoryCount(category=c, product_count=len(names), example_products=names[:EXAMPLES_PER_CATEGORY])
            for c, names in sorted(by_category.items(), key=lambda kv: -len(kv[1]))
        ],
    )


def _normalize_size(size: str) -> str:
    return SIZE_ALIASES.get(size.strip().lower(), size.strip().upper())


def search_products(
    query: str,
    max_price: float | None = None,
    min_price: float | None = None,
    in_stock_size: str | None = None,
    max_results: int = MAX_SEARCH_RESULTS,
) -> ProductSearchResult:
    """Search the Campus Customs catalogue with shopper keywords, e.g. "hoodies",
    "gray crewneck", "hockey", "Saybrook", "bulldog t-shirt", "navy quarter-zip".

    Category words (hoodie, crewneck, t-shirt, quarter-zip, jacket, long sleeve) filter by
    category; every other keyword must appear in the product's name, garment type, colors,
    search tags, or description. Returns product ids, names, colors and prices.
    Use get_product_details / get_inventory with a product_id for more.

    Put budgets and sizes in the filter arguments, not in `query`:
    "hoodies under $60 in XL" -> query="hoodies", max_price=60, in_stock_size="XL".

    Args:
        query: What the shopper is looking for, in plain words. May be "" if only filters apply.
        max_price: Only products priced at or below this (USD).
        min_price: Only products priced at or above this (USD).
        in_stock_size: Only products with at least 1 in stock in this size (XS, S, M, L, XL, XXL, or "medium", "2XL", ...).
        max_results: How many products to return (at most 12).
    """
    max_results = max(1, min(max_results, MAX_SEARCH_RESULTS))
    categories, keywords = _tokens(query)
    size = _normalize_size(in_stock_size) if in_stock_size else None
    filters = [
        f"price <= ${max_price:.2f}" if max_price is not None else "",
        f"price >= ${min_price:.2f}" if min_price is not None else "",
        f"in stock in size {size}" if size else "",
    ]
    filters = [f for f in filters if f]

    if size and size not in SIZE_ORDER:
        return ProductSearchResult(
            query=query, total_matches=0, returned=0, products=[],
            note=f"Size {size} is not offered. Sizes carried: {', '.join(SIZE_ORDER)}.",
        )

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        in_size = (
            {r[0] for r in conn.execute("SELECT product_id FROM inventory WHERE size = ? AND quantity > 0", (size,))}
            if size
            else None
        )

    scored = []
    for row in rows:
        if categories and category_for(row["garment_type"]) not in categories:
            continue
        if max_price is not None and row["price"] > max_price:
            continue
        if min_price is not None and row["price"] < min_price:
            continue
        if in_size is not None and row["product_id"] not in in_size:
            continue
        name = row["name"].lower()
        tags = " ".join(json.loads(row["search_tags"])).lower()
        colors = " ".join(json.loads(row["colors"])).lower()
        garment = row["garment_type"].lower()
        desc = row["description"].lower()
        score = 0
        for kw in keywords:
            hit = 3 * (kw in name) + 2 * (kw in tags) + 2 * (kw in colors) + 2 * (kw in garment) + (kw in desc)
            if hit == 0:
                break  # every keyword must match somewhere
            score += hit
        else:
            scored.append((score, row))

    scored.sort(key=lambda sr: -sr[0])  # stable: ties stay alphabetical
    products = [_summary(row) for _, row in scored[:max_results]]

    note = ""
    if not categories and not keywords and not filters:
        note = "The query had no searchable words. Ask the shopper what they are looking for, or use list_categories."
        products, scored = [], []
    elif not products:
        looked_for = ", ".join(sorted(categories) + keywords + filters)
        note = f"No products match all of: {looked_for}. Tell the shopper we don't carry that; do not suggest items as if they matched."
    elif len(scored) > len(products):
        note = f"Showing the top {len(products)} of {len(scored)} matches."
        if not filters and len(keywords) <= 1:
            note += (
                " This is a broad request: show a few options and ask ONE short question"
                " (style, color, size, or budget) to narrow it down."
            )
    if filters and products:
        note = (note + f" All results are {', '.join(filters)}.").strip()

    return ProductSearchResult(
        query=query, total_matches=len(scored), returned=len(products), products=products, note=note
    )


def get_product_details(product_id: str) -> ProductDetails:
    """Get the full catalogue record for one product: name, garment type, description,
    colors, price, and image. Use a product_id from search_products (e.g. "basic-hoodie-big-yale").

    Args:
        product_id: The product's id (slug) from search_products.
    """
    with get_db() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id.strip(),)).fetchone()
    if row is None:
        return ProductDetails(
            found=False,
            product_id=product_id,
            note="No product with this id. Use search_products to find the right product_id.",
        )
    return ProductDetails(
        found=True,
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        category=category_for(row["garment_type"]),
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        image_url=f"/media/{row['image_file_path']}",
        note="" if json.loads(row["colors"]) else "The catalogue lists no colors for this product.",
    )


def get_inventory(product_id: str, size: str | None = None) -> InventoryResult:
    """Get the real stock for one product, by size (XS, S, M, L, XL, XXL).
    Quantity 0 means that size is out of stock.

    Args:
        product_id: The product's id (slug) from search_products.
        size: Optional size the shopper asked about, e.g. "M", "medium", "XL", "2XL".
    """
    requested = None
    if size:
        requested = SIZE_ALIASES.get(size.strip().lower(), size.strip().upper())

    with get_db() as conn:
        row = conn.execute("SELECT name FROM catalogue WHERE product_id = ?", (product_id.strip(),)).fetchone()
        if row is None:
            return InventoryResult(
                found=False,
                product_id=product_id,
                note="No product with this id. Use search_products to find the right product_id.",
            )
        stock = inventory_for(conn, product_id.strip())

    sizes = [SizeStock(size=s["size"], quantity=s["quantity"], in_stock=s["quantity"] > 0) for s in stock]
    result = InventoryResult(
        found=True,
        product_id=product_id,
        name=row["name"],
        sizes=sizes,
        total_stock=sum(s.quantity for s in sizes),
        in_stock_sizes=[s.size for s in sizes if s.in_stock],
        out_of_stock_sizes=[s.size for s in sizes if not s.in_stock],
        requested_size=requested,
    )
    if requested:
        match = next((s for s in sizes if s.size == requested), None)
        if match is None:
            result.note = f"Size {requested} is not offered. Sizes carried: {', '.join(SIZE_ORDER)}."
        else:
            result.requested_size_quantity = match.quantity
            result.note = (
                f"Size {requested}: {match.quantity} in stock."
                if match.in_stock
                else f"Size {requested} is OUT OF STOCK."
            )
    return result


def compare_products(product_ids: list[str]) -> ProductComparison:
    """Compare 2-4 specific products side by side using database facts only: price,
    garment type, colors, and stock by size. Also returns which is cheapest, the price
    difference, colors they share, and sizes in stock for all of them.
    Use this when the shopper asks to compare items or asks "which is cheaper / what's the
    difference". Get the product_ids from search_products first.

    Args:
        product_ids: 2 to 4 product ids (slugs) from search_products.
    """
    ids = list(dict.fromkeys(pid.strip() for pid in product_ids if pid.strip()))
    if len(ids) < 2:
        return ProductComparison(products=[], note="Need at least 2 different product_ids to compare.")
    extra = ids[MAX_COMPARE:]
    ids = ids[:MAX_COMPARE]

    compared: list[ComparedProduct] = []
    not_found: list[str] = []
    with get_db() as conn:
        for pid in ids:
            row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (pid,)).fetchone()
            if row is None:
                not_found.append(pid)
                continue
            stock = inventory_for(conn, pid)
            compared.append(
                ComparedProduct(
                    product_id=pid,
                    name=row["name"],
                    garment_type=row["garment_type"],
                    category=category_for(row["garment_type"]),
                    price=row["price"],
                    colors=json.loads(row["colors"]),
                    total_stock=sum(s["quantity"] for s in stock),
                    in_stock_sizes=[s["size"] for s in stock if s["quantity"] > 0],
                    out_of_stock_sizes=[s["size"] for s in stock if s["quantity"] == 0],
                )
            )

    result = ProductComparison(products=compared, not_found=not_found)
    if compared:
        low = min(p.price for p in compared)
        result.cheapest = [p.product_id for p in compared if p.price == low]
        result.price_difference = round(max(p.price for p in compared) - low, 2)
        result.colors_in_common = sorted(set.intersection(*(set(p.colors) for p in compared)))
        result.sizes_in_stock_for_all = [
            s for s in SIZE_ORDER if all(s in p.in_stock_sizes for p in compared)
        ]
    notes = []
    if not_found:
        notes.append(f"Not in the catalogue: {', '.join(not_found)}. Use search_products to find the right ids.")
    if extra:
        notes.append(f"Only the first {MAX_COMPARE} products were compared.")
    if len(compared) > 1 and result.price_difference == 0:
        notes.append("They are the same price.")
    notes.append("Compare only these fields; don't claim differences in quality, fit or material that aren't in the data.")
    result.note = " ".join(notes)
    return result


def build_product_cards(product_ids: list[str]) -> list[ProductCard]:
    """Look up card data for the ids the agent chose. Not an agent tool: the backend calls it
    after the run, so every card value comes from the DB. Unknown ids and duplicates are dropped."""
    ids = list(dict.fromkeys(pid.strip() for pid in product_ids if pid.strip()))[:MAX_PRODUCT_CARDS]
    cards: list[ProductCard] = []
    with get_db() as conn:
        for pid in ids:
            row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (pid,)).fetchone()
            if row is None:
                continue
            product = product_from_row(row)
            stock = inventory_for(conn, pid)
            cards.append(
                ProductCard(
                    product_id=product["product_id"],
                    name=product["name"],
                    garment_type=product["garment_type"],
                    category=product["category"],
                    price=product["price"],
                    image_url=product["image_url"],
                    colors=product["colors"],
                    total_stock=sum(s["quantity"] for s in stock),
                    in_stock_sizes=[s["size"] for s in stock if s["quantity"] > 0],
                )
            )
    return cards


AGENT_TOOLS = [list_categories, search_products, get_product_details, get_inventory, compare_products]
