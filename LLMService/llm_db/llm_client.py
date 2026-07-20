"""
Thin wrapper around a local Ollama server running qwen2.5:3b.

The LLM's ONLY job in this system is language <-> SQL translation, for
one narrow sub-task at a time. It never decides workflow. It is always
expected to return either a single raw SQL statement, or the literal
string ABORT. All cleanup of the raw text happens here.
"""

import requests,logging

from llm_db.config import OLLAMA_HOST, OLLAMA_MODEL


def _clean(text: str) -> str:
    text = text.strip()

    # Strip accidental markdown code fences (small local models sometimes
    # add these even when told not to).
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Some small models wrap the statement in stray quotes.
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1].strip()

    # Drop a trailing period a chatty model might tack on after the SQL.
    return text


def ask_llm(system_prompt: str, user_message: str) -> str:
    """
    Send a single-turn request to the local Ollama model and return
    cleaned raw text (either a SQL statement or the literal 'ABORT').
    """
    logging.getLogger().critical(f"system_prompt = {system_prompt}\n\n\nuser_message = {user_message}\n\n\n\n")
    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False
        },
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    raw = data.get("message", {}).get("content", "")

    return _clean(raw)
