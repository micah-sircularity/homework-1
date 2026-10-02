"""Course-assistant RAG chatbot with a session message thread."""

import json
import os
from pathlib import Path

from fireworks import Fireworks

try:
    from index_docs import search
    from models import RAGResponse
except ImportError:
    from helpers.index_docs import search
    from helpers.models import RAGResponse

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "accounts/fireworks/models/glm-5p3-flash"
# Serverless rates for GLM 5.3 Flash, USD per token.
INPUT_USD_PER_TOKEN = 0.15 / 1_000_000
CACHED_INPUT_USD_PER_TOKEN = 0.029 / 1_000_000
OUTPUT_USD_PER_TOKEN = 0.50 / 1_000_000

instructions = """
You're a course assistant, your task is to answer the QUESTION from the
course students using the provided CONTEXT
""".strip()

prompt_template = """
<QUESTION>
{question}
</QUESTION>

<CONTEXT>
{context}
</CONTEXT>
""".strip()


def load_env(path: Path = ROOT / ".env") -> None:
    """Load KEY=VALUE lines from .env without overriding existing variables."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def build_prompt(question: str, search_results: list[dict]) -> str:
    """Fill the question and retrieved chunks into the prompt template."""
    context = json.dumps(search_results, indent=2)
    return prompt_template.format(question=question, context=context).strip()


def new_messages() -> list[dict]:
    """Start a session thread with the course-assistant instructions."""
    return [{"role": "system", "content": instructions}]


def _usage(response) -> dict:
    """Input tokens, output tokens, and USD cost from a Fireworks response."""
    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = (usage.completion_tokens or 0) if usage else 0
    cached_tokens = 0
    if usage and usage.prompt_tokens_details and usage.prompt_tokens_details.cached_tokens:
        cached_tokens = usage.prompt_tokens_details.cached_tokens
    fresh_input_tokens = max(input_tokens - cached_tokens, 0)
    cost = (
        fresh_input_tokens * INPUT_USD_PER_TOKEN
        + cached_tokens * CACHED_INPUT_USD_PER_TOKEN
        + output_tokens * OUTPUT_USD_PER_TOKEN
    )
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": cost,
    }


def llm(messages: list[dict], model: str = DEFAULT_MODEL) -> dict:
    """Send the full message thread to Fireworks.

    Returns the reply text plus input tokens, output tokens, and USD cost.
    """
    load_env()
    client = Fireworks()
    response = client.chat.completions.create(model=model, messages=messages)
    return {
        "answer": response.choices[0].message.content or "",
        **_usage(response),
    }


def llm_chat(messages: list[dict], model: str = DEFAULT_MODEL) -> dict:
    """Ask Fireworks for a RAGResponse and return it with token usage."""
    load_env()
    client = Fireworks()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "RAGResponse",
                "schema": RAGResponse.model_json_schema(),
            },
        },
    )
    parsed = RAGResponse.model_validate_json(response.choices[0].message.content or "")
    return {"response": parsed, **_usage(response)}


def rag(query: str, messages: list[dict], num_results: int = 5) -> dict:
    """Search, append the user turn, call the structured LLM, and store the reply."""
    search_results = search(query, num_results=num_results)
    prompt = build_prompt(query, search_results)
    messages.append({"role": "user", "content": prompt})
    result = llm_chat(messages)
    messages.append({"role": "assistant", "content": result["response"].answer})
    return result
