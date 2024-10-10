import logging

import ollama


logger = logging.getLogger("uvicorn.info")


def pull_llm():
    logger.info("Pulling LLM")
    last_progress = 0
    for resp in ollama.pull("llama3.2:1b", stream=True):
        if "completed" not in resp or "total" not in resp:
            continue
        current_progress = resp["completed"] / resp["total"]
        if current_progress - last_progress >= 0.05:
            logger.info(f"Pulling: {current_progress:.0%}")
            last_progress = current_progress
    logger.info("Pulling complete")
