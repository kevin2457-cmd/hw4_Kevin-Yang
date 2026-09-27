"""Append-only audit trail of agent runs: output/audit_trail.json (Problem 12).

One entry per chat message: when it ran, a short description of the request, every tool
call in order (name, key arguments, short result summary), and why the run stopped.
It never stores passwords, tokens, API keys or emails, and it truncates long values.
Writing the log can never break a chat: failures are logged and ignored.
"""

import json
import logging
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, RetryPromptPart, ToolCallPart, ToolReturnPart

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
PREVIEW_CHARS = 200
MAX_ARG_CHARS = 120
MAX_IDS_SHOWN = 6
OUTPUT_TOOL = "final_result"  # PydanticAI's internal tool for the structured AgentOutput

_lock = threading.Lock()
logger = logging.getLogger("campus_customs.audit")

# Keys whose values are never written, and patterns scrubbed out of any free text.
_SENSITIVE_KEYS = re.compile(r"pass(word)?|token|secret|api[_-]?key|authorization|hash", re.I)
_SENSITIVE_TEXT = [
    re.compile(r"\b\d+\.\d{10}\.[0-9a-f]{64}\b"),  # our signed login tokens
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),  # API-key-looking strings
    re.compile(r"pbkdf2_sha256\$\S+"),  # password hashes
]


def _scrub(text: str, limit: int = PREVIEW_CHARS) -> str:
    for pattern in _SENSITIVE_TEXT:
        text = pattern.sub("[redacted]", text)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _safe_args(args: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in args.items():
        if _SENSITIVE_KEYS.search(key):
            safe[key] = "[redacted]"
        elif isinstance(value, str):
            safe[key] = _scrub(value, MAX_ARG_CHARS)
        elif isinstance(value, list):
            safe[key] = [_scrub(str(v), MAX_ARG_CHARS) for v in value[:MAX_IDS_SHOWN]]
        else:
            safe[key] = value
    return safe


def _ids(items: list, attr: str = "product_id") -> str:
    ids = [getattr(i, attr) for i in items[:MAX_IDS_SHOWN]]
    more = f", +{len(items) - MAX_IDS_SHOWN} more" if len(items) > MAX_IDS_SHOWN else ""
    return f"[{', '.join(ids)}{more}]"


def summarize_result(content: Any) -> str:
    """A one-line, human-readable summary of a tool's return value (not the raw data)."""
    name = type(content).__name__
    try:
        if name == "CatalogueOverview":
            cats = ", ".join(f"{c.category} {c.product_count}" for c in content.categories)
            return f"{content.total_products} products; {cats}"
        if name == "ProductSearchResult":
            text = f"{content.total_matches} matches, returned {content.returned}: {_ids(content.products)}"
            return _scrub(text + (f" | note: {content.note}" if content.note else ""), 300)
        if name == "ProductDetails":
            if not content.found:
                return f"not found: {content.product_id}"
            return f"{content.name}: ${content.price:.2f}, colors {content.colors}"
        if name == "InventoryResult":
            if not content.found:
                return f"not found: {content.product_id}"
            sizes = " ".join(f"{s.size}:{s.quantity}" for s in content.sizes)
            text = f"{content.name}: {sizes} (total {content.total_stock})"
            return text + (f" | {content.note}" if content.note else "")
        if name == "ProductComparison":
            text = f"compared {_ids(content.products)}; cheapest {content.cheapest}; price diff ${content.price_difference}"
            return text + (f"; not found {content.not_found}" if content.not_found else "")
        if isinstance(content, BaseModel):
            return _scrub(content.model_dump_json(), 300)
        return _scrub(str(content), 300)
    except Exception:  # a summary problem must never break auditing
        return _scrub(repr(content), 300)


def _steps(messages: list[ModelMessage]) -> tuple[list[dict], int, str | None]:
    """Tool calls in the order the model made them, with their results; plus the number
    of model requests and the last finish_reason."""
    steps: list[dict] = []
    by_call_id: dict[str, dict] = {}
    model_requests = 0
    finish_reason = None
    for message in messages:
        if isinstance(message, ModelResponse):
            model_requests += 1
            finish_reason = getattr(message, "finish_reason", None) or finish_reason
            for part in message.parts:
                if isinstance(part, ToolCallPart) and part.tool_name != OUTPUT_TOOL:
                    step = {
                        "step": len(steps) + 1,
                        "model_request": model_requests,
                        "tool": part.tool_name,
                        "args": _safe_args(part.args_as_dict()),
                        "status": "pending",
                        "result_summary": None,
                    }
                    steps.append(step)
                    by_call_id[part.tool_call_id] = step
        elif isinstance(message, ModelRequest):
            for part in message.parts:
                step = by_call_id.get(getattr(part, "tool_call_id", ""))
                if step is None:
                    continue
                if isinstance(part, ToolReturnPart):
                    step["status"] = "ok"
                    step["result_summary"] = summarize_result(part.content)
                elif isinstance(part, RetryPromptPart):
                    # Bad arguments or a tool asked the model to retry: recorded as an error.
                    step["status"] = "error (model asked to retry)"
                    step["result_summary"] = _scrub(str(part.content), 300)
    return steps, model_requests, finish_reason


def record_run(
    *,
    message: str,
    user_id: int | None,
    current_product_id: str | None,
    history_turns: int,
    model: str,
    messages: list[ModelMessage],
    duration_ms: int,
    reply: Any = None,
    error: BaseException | None = None,
    request_limit: int | None = None,
) -> None:
    """Append one entry for a finished (or failed) agent run."""
    try:
        steps, model_requests, finish_reason = _steps(messages)
        if error is None:
            used_output_tool = any(
                isinstance(p, ToolCallPart) and p.tool_name == OUTPUT_TOOL
                for m in messages if isinstance(m, ModelResponse) for p in m.parts
            )
            how = "structured answer via final_result" if used_output_tool else "text answer"
            stop_reason = f"completed: model returned its final {how} (finish_reason={finish_reason or 'stop'})"
        elif type(error).__name__ == "UsageLimitExceeded":
            stop_reason = f"stopped: hit the limit of {request_limit} model requests before answering"
        else:
            stop_reason = f"error: {type(error).__name__}: {_scrub(str(error), 200)}"

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "run_id": uuid.uuid4().hex[:12],
            "request": {
                "summary": _scrub(message),
                "chars": len(message),
                "user": f"user_id={user_id}" if user_id is not None else "guest",
                "current_product_id": current_product_id,
                "history_turns_sent_to_model": history_turns,
            },
            "model": model,
            "tool_calls": steps,
            "model_requests": model_requests,
            "stop_reason": stop_reason,
            "outcome": (
                {
                    "reply_preview": _scrub(reply.reply),
                    "product_card_ids": [p.product_id for p in reply.products],
                    "tools_used": reply.tools_used,
                }
                if reply is not None
                else None
            ),
            "duration_ms": duration_ms,
        }
        _append(entry)
    except Exception:
        logger.exception("Could not write audit trail entry")


def _append(entry: dict) -> None:
    """Append-only: read the existing list, add one entry, write back atomically.
    Earlier entries are never modified. A corrupt file is kept aside, never deleted."""
    with _lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rows: list = []
        if AUDIT_PATH.exists() and AUDIT_PATH.stat().st_size > 0:
            try:
                loaded = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
                rows = loaded if isinstance(loaded, list) else [loaded]
            except json.JSONDecodeError:
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                AUDIT_PATH.replace(AUDIT_PATH.with_name(f"audit_trail.corrupt-{stamp}.json"))
        rows.append(entry)
        tmp = AUDIT_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(AUDIT_PATH)
