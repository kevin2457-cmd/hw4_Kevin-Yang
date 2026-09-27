"""Campus Customs shopping assistant: a PydanticAI agent on the course model via Portkey.

The system prompt lives in prompts/prompt.md; tools live in tools.py.
Every run is appended to output/audit_trail.json (audit.py).
"""

import os
import time
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from openai import AsyncOpenAI  # noqa: E402
from pydantic_ai import Agent, RunContext, capture_run_messages  # noqa: E402
from pydantic_ai.messages import (  # noqa: E402
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIResponsesModel  # noqa: E402
from pydantic_ai.providers.openai import OpenAIProvider  # noqa: E402
from pydantic_ai.usage import UsageLimits  # noqa: E402

import audit  # noqa: E402
from models import AgentOutput, ChatReply, ChatTurn, ShopperDeps  # noqa: E402
from tools import AGENT_TOOLS, build_product_cards  # noqa: E402

HERE = Path(__file__).resolve().parent

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-6-astra")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").rstrip("/")
PROMPT_PATH = HERE / "prompts" / "prompt.md"
MAX_MODEL_REQUESTS = 8  # cap on model calls (incl. tool round-trips) per chat message
MAX_HISTORY_TURNS = 20  # only the most recent turns are sent back to the model


class AgentConfigError(RuntimeError):
    """The agent can't start, e.g. the API key is missing."""


@lru_cache(maxsize=1)
def get_agent() -> Agent[ShopperDeps, AgentOutput]:
    api_key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not api_key:
        raise AgentConfigError("PORTKEY_API_KEY is not set. Add it to hw4/.env (see .env.example).")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": api_key},
    )
    model = OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
    agent = Agent(
        model,
        deps_type=ShopperDeps,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        tools=AGENT_TOOLS,
        output_type=AgentOutput,
    )
    agent.instructions(shopper_context)
    return agent


def shopper_context(ctx: RunContext[ShopperDeps]) -> str:
    """Per-request instructions built from the deps: who is chatting and which page is open.
    Kept to a few lines; product facts are still fetched with the tools."""
    lines = ["## Current context"]
    customer = ctx.deps.customer
    if customer:
        lines.append(
            f"- Shopper: logged in as {customer.first_name} {customer.last_name} "
            f"(user_id {customer.user_id}, email {customer.email}). "
            "This conversation is saved to their account."
        )
    else:
        lines.append("- Shopper: a guest (not logged in). Nothing is saved.")
    product = ctx.deps.current_product
    if product:
        lines.append(
            f'- Page: the shopper is viewing the product page for "{product.name}" '
            f"(product_id `{product.product_id}`). Unless they clearly mean another item, "
            '"this", "it" and "this one" refer to this product: call the tools with this product_id.'
        )
    else:
        lines.append("- Page: not on a product page.")
    return "\n".join(lines)


def _to_model_history(history: list[ChatTurn]) -> list[ModelMessage]:
    """Turn plain-text history (from the DB or the widget) into PydanticAI messages."""
    turns = history[-MAX_HISTORY_TURNS:]
    while turns and turns[0].role != "user":  # the model history should start with a user turn
        turns = turns[1:]
    messages: list[ModelMessage] = []
    for turn in turns:
        if turn.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            text = turn.content
            if turn.product_ids:
                text += f"\n\n[Product cards shown: {', '.join(turn.product_ids)}]"
            messages.append(ModelResponse(parts=[TextPart(content=text)]))
    return messages


async def run_chat(message: str, history: list[ChatTurn], deps: ShopperDeps) -> ChatReply:
    model_history = _to_model_history(history)
    audit_info = dict(
        message=message,
        user_id=deps.customer.user_id if deps.customer else None,
        current_product_id=deps.current_product.product_id if deps.current_product else None,
        history_turns=len(model_history),
        model=MODEL_NAME,
        request_limit=MAX_MODEL_REQUESTS,
    )
    started = time.perf_counter()
    with capture_run_messages() as run_messages:
        try:
            result = await get_agent().run(
                message,
                deps=deps,
                message_history=model_history,
                usage_limits=UsageLimits(request_limit=MAX_MODEL_REQUESTS),
            )
        except Exception as exc:
            # Log the failed run (tool calls made so far + why it stopped), then let main.py
            # return the error to the widget, so the shopper never sees a fake answer.
            audit.record_run(
                **audit_info,
                messages=run_messages[len(model_history):],
                duration_ms=int((time.perf_counter() - started) * 1000),
                error=exc,
            )
            raise
    tool_names = {tool.__name__ for tool in AGENT_TOOLS}  # skips PydanticAI's own final_result tool
    tools_used = [
        part.tool_name
        for msg in result.new_messages()
        if isinstance(msg, ModelResponse)
        for part in msg.parts
        if isinstance(part, ToolCallPart) and part.tool_name in tool_names
    ]
    output = result.output
    reply = ChatReply(
        reply=output.reply,
        tools_used=list(dict.fromkeys(tools_used)),
        products=build_product_cards(output.product_ids),
    )
    audit.record_run(
        **audit_info,
        messages=result.new_messages(),
        duration_ms=int((time.perf_counter() - started) * 1000),
        reply=reply,
    )
    return reply
