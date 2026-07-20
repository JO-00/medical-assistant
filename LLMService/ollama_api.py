import ollama
import logging
import time

logger = logging.getLogger(__name__)

client = ollama.Client(host="http://host.docker.internal:11434")


def call_ollama(
    user_message: str,
    system_prompt: str = None,
    model: str = "qwen2.5:3b"
) -> str:

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": user_message
    })

    logger.info(
        f"Ollama request | model={model} | "
        f"system_len={len(system_prompt) if system_prompt else 0} | "
        f"user_len={len(user_message)} | "
        f"messages={len(messages)}"
    )

    logger.debug(
        f"User prompt preview START:\n{user_message[:500]}\n...\nEND"
    )

    start = time.time()

    try:
        response = client.chat(
            model=model,
            messages=messages
        )

        elapsed = time.time() - start

        result = response["message"]["content"]

        logger.info(
            f"Ollama success | "
            f"time={elapsed:.2f}s | "
            f"response_len={len(result)}"
        )

        return result

    except Exception as e:
        elapsed = time.time() - start

        logger.exception(
            f"Ollama failed | "
            f"time={elapsed:.2f}s | "
            f"model={model} | "
            f"error={e}"
        )

        raise