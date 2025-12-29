
from app.ai.client import call_llm  # your existing client

def run_llm(prompt: str) -> str:
    return call_llm(prompt=prompt)
