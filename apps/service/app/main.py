import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import bcrypt
import httpx
from fastapi import FastAPI, Request, Response
from .config import (
    CPU_WORK_MS,
    MEMORY_MB,
    DOWNSTREAM_URL,
    DOWNSTREAM_ERROR_RATE,
    DOWNSTREAM_LATENCY_MS,
    MONGODB_URI,
)
from .metrics import REQUEST_DURATION, REQUESTS_IN_FLIGHT, ERROR_COUNT, metrics_response

logging.basicConfig(level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO")))
logger = logging.getLogger(__name__)

# In-memory token store if no MongoDB
_tokens: dict[str, dict] = {}
_db = None

def get_db():
    global _db
    if _db is not None:
        return _db
    if MONGODB_URI:
        try:
            from pymongo import MongoClient
            _db = MongoClient(MONGODB_URI).get_database().tokens
            return _db
        except Exception as e:
            logger.warning("MongoDB unavailable: %s, using in-memory", e)
    return None

def _cpu_work(ms: int):
    if ms <= 0:
        return
    end = time.perf_counter() + (ms / 1000.0)
    while time.perf_counter() < end:
        pass

def _allocate_mb(n: int):
    if n <= 0:
        return
    try:
        globals()["_mem_chunk"] = b"x" * (n * 1024 * 1024)
    except MemoryError:
        logger.warning("Memory allocation failed for %s MB", n)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if _db:
        _db.client.close()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def middleware(request: Request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())[:8]
    path = request.url.path
    REQUESTS_IN_FLIGHT.labels(path=path).inc()
    start = time.perf_counter()
    try:
        response = await call_next(request)
        status = response.status_code
        if status >= 400:
            ERROR_COUNT.labels(method=request.method, path=path, status=status).inc()
        return response
    except Exception as e:
        ERROR_COUNT.labels(method=request.method, path=path, status="500").inc()
        raise
    finally:
        REQUESTS_IN_FLIGHT.labels(path=path).dec()
        REQUEST_DURATION.labels(method=request.method, path=path).observe(time.perf_counter() - start)
        logger.info(
            json.dumps({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "level": "INFO",
                "request_id": rid,
            }),
            extra={"request_id": rid},
        )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    body, content_type = metrics_response()
    return Response(content=body, media_type=content_type)

@app.post("/login")
async def login(request: Request, response: Response):
    _cpu_work(CPU_WORK_MS)
    _allocate_mb(MEMORY_MB)
    if DOWNSTREAM_URL:
        import random
        time.sleep(DOWNSTREAM_LATENCY_MS / 1000.0)
        if random.random() < DOWNSTREAM_ERROR_RATE:
            response.status_code = 502
            return {"error": "downstream_error"}
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(DOWNSTREAM_URL, timeout=5.0)
            if r.status_code >= 400:
                response.status_code = 502
                return {"error": "downstream_error"}
        except Exception:
            response.status_code = 502
            return {"error": "downstream_error"}
    try:
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    except Exception:
        body = {}
    username = (body or {}).get("username", "")
    password = (body or {}).get("password", "")
    if not username and not password:
        response.status_code = 400
        return {"error": "username and password required"}
    token = str(uuid.uuid4())
    doc = {"token": token, "username": username}
    db = get_db()
    if db:
        db.insert_one(doc)
    else:
        _tokens[token] = doc
    return {"token": token}


@app.post("/signup")
async def signup(request: Request, response: Response):
    """
    CPU-heavy password hashing endpoint to drive autoscaling on CPU.
    Does not persist users; only simulates the cost of a real signup flow.
    """
    _cpu_work(CPU_WORK_MS)
    try:
        body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    except Exception:
        body = {}
    username = (body or {}).get("username", "")
    password = (body or {}).get("password", "")
    if not username or not password:
        response.status_code = 400
        return {"error": "username and password required"}
    # bcrypt hashing is intentionally expensive; this makes /signup CPU-bound.
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return {"username": username, "password_hash": hashed.decode("utf-8")}

@app.post("/chaos")
def chaos(action: str = "memory", mb: int = 50):
    if action == "oom":
        _allocate_mb(1024)
        return {"ok": True, "action": "oom"}
    if action == "memory":
        _allocate_mb(min(mb, 512))
        return {"ok": True, "action": "memory", "mb": mb}
    return {"error": "unknown action"}
