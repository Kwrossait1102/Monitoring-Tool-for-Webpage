from fastapi import FastAPI, Query
import requests
import time
import os
import threading
from threading import Lock
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv(".env") # load enviroment variable from .env file
from .to_database import init_db, add_record, get_last_records

# ------------------------------------------------------------
# Lifespan context: initialization and shutdown procedures
# ------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database when the application starts
    init_db()
    thread = threading.Thread(target=background_checker, daemon=True)
    thread.start()
    # Yield control to allow the app to run
    yield


# Create FastAPI application instance with lifespan handler
app = FastAPI(lifespan=lifespan)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
# Target URL is read from environment variable (default provided)
TARGET_URL = os.getenv("TARGET_URL", "https://example.com")

# Update automatically every 60s
CHECK_INTERVAL = 60

# Thread-safe counters for availability statistics and database operations
_stats_lock = Lock()
_db_lock = Lock()

_total_checks = 0
_ok_checks = 0
_consecutive_failures = 0

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def _record(ok: bool):
    """Update internal counters for total and successful checks."""
    global _total_checks, _ok_checks, _consecutive_failures
    with _stats_lock:
        _total_checks += 1
        if ok:
            _ok_checks += 1
            _consecutive_failures = 0
        else:
            _consecutive_failures +=1


def _availability_pct():
    """Calculate the overall availability percentage since app start."""
    with _stats_lock:
        if _total_checks == 0:
            return None
        return round(_ok_checks / _total_checks * 100, 2)

def background_checker():
    """Check automatically in background."""
    while True:
        _run_check(source="auto")
        time.sleep(CHECK_INTERVAL)


# ------------------------------------------------------------
# Application routes
# ------------------------------------------------------------

def _run_check(source: str):
    """Perform a single availability check and store the result."""
    start = time.time()
    ts = datetime.now(timezone.utc)  # timezone-aware UTC timestamp

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        ttfb_start = time.time()
        r = requests.get(TARGET_URL, timeout=5, headers=headers, stream=True)

        first_byte = next(r.iter_content(1), None)
        ttfb_ms = round((time.time() - ttfb_start) * 1000, 2)

        content = first_byte + r.content if first_byte else r.content
        response_size_bytes = len(content)

        latency = round((time.time() - start) * 1000, 2)
        ok = bool(r.ok)

        _record(ok)

        with _db_lock:
            add_record(
                ts=ts,
                url=TARGET_URL,
                status_code=r.status_code,
                ok=ok,
                latency_ms=latency,
                error="",
                ttfb_ms=ttfb_ms,
                response_size_bytes=response_size_bytes,
                consecutive_failures=_consecutive_failures,
                source=source
            )

        return {
            "url": TARGET_URL,
            "status_code": r.status_code,
            "available": ok,
            "latency_ms": latency,
            "ttfb_ms":ttfb_ms,
            "response_size_bytes": response_size_bytes,
            "consecutive_failures": _consecutive_failures,
            "availability_pct_since_start": _availability_pct(),
            "source":source
        }

    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        _record(False)

        with _db_lock:
            add_record(
                ts=ts,
                url=TARGET_URL,
                status_code=None,
                ok=False,
                latency_ms=latency,
                error=str(e),
                ttfb_ms=None,
                response_size_bytes=None,
                consecutive_failures=_consecutive_failures,
                source=source,
            )

        return {
            "url": TARGET_URL,
            "available": False,
            "error": str(e),
            "latency_ms": latency,
            "ttfb_ms":None,
            "response_size_bytes":None,
            "consecutive_failures": _consecutive_failures,
            "availability_pct_since_start": _availability_pct(),
            "source":source
        }


@app.get("/")
def check_manual():
    return _run_check(source="manual")

@app.get("/records")
def records(limit: int = Query(100, ge=1, le=1000)):
    items = get_last_records(limit)
    return {"count": len(items), "items": items}


@app.get("/stats")
def stats():
    """Return current in-memory availability statistics."""
    with _stats_lock:
        total = _total_checks
        ok = _ok_checks
        failures = _consecutive_failures
    return {
        "target_url": TARGET_URL,
        "total_checks": total,
        "ok_checks": ok,
        "availability_pct": round(ok / total * 100, 2) if total else None,
        "consecutive_failures": failures,
    }
