import os

def env_int(key: str, default: int) -> int:
    v = os.environ.get(key)
    return int(v) if v is not None else default

def env_float(key: str, default: float) -> float:
    v = os.environ.get(key)
    return float(v) if v is not None else default

CPU_WORK_MS = env_int("CPU_WORK_MS", 0)
MEMORY_MB = env_int("MEMORY_MB", 0)
DOWNSTREAM_URL = os.environ.get("DOWNSTREAM_URL", "")
DOWNSTREAM_ERROR_RATE = env_float("DOWNSTREAM_ERROR_RATE", 0.0)
DOWNSTREAM_LATENCY_MS = env_int("DOWNSTREAM_LATENCY_MS", 0)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
MONGODB_URI = os.environ.get("MONGODB_URI", "")
