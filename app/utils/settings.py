import os

# ---- LLM CONFIG ----
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# ---- ANALYSIS RETRY CONFIG ----
ANALYSIS_MAX_RETRIES = int(os.getenv("ANALYSIS_MAX_RETRIES", "3"))
ANALYSIS_BASE_DELAY = int(os.getenv("ANALYSIS_BASE_DELAY", "5"))  # seconds

# ---- REDIS ----
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")