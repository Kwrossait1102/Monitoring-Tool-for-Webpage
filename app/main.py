from fastapi import FastAPI, Query
import requests
import time
import os
from threading import Lock
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from to_database import init_db, add_record, get_last_records
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------
# Lifespan context: initialization and shutdown procedures
# ------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database when the application starts
    init_db()
    # Yield control to allow the app to run
    yield
    # (Optional) Perform cleanup tasks when the app shuts down


# Create FastAPI application instance with lifespan handler
app = FastAPI(lifespan=lifespan)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
# Target URL is read from environment variable (default provided)
TARGET_URL = os.getenv("TARGET_URL", "https://example.com")

# Thread-safe counters for availability statistics
_stats_lock = Lock()
_total_checks = 0
_ok_checks = 0


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def _record(ok: bool):
    """Update internal counters for total and successful checks."""
    global _total_checks, _ok_checks
    with _stats_lock:
        _total_checks += 1
        if ok:
            _ok_checks += 1


def _availability_pct():
    """Calculate the overall availability percentage since app start."""
    with _stats_lock:
        if _total_checks == 0:
            return None
        return round(_ok_checks / _total_checks * 100, 2)


# ------------------------------------------------------------
# Application routes
# ------------------------------------------------------------
@app.get("/")
def check_availability():
    """Perform a single availability check and store the result."""
    start = time.time()
    ts = datetime.now(timezone.utc)  # timezone-aware UTC timestamp
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(TARGET_URL, timeout=5, headers=headers)
        latency = round((time.time() - start) * 1000, 2)
        ok = bool(r.ok)

        _record(ok)
        add_record(ts, TARGET_URL, r.status_code, ok, latency, "")

        return {
            "url": TARGET_URL,
            "status_code": r.status_code,
            "available": ok,
            "latency_ms": latency,
            "availability_pct_since_start": _availability_pct(),
        }

    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        _record(False)
        add_record(ts, TARGET_URL, None, False, latency, str(e))

        return {
            "url": TARGET_URL,
            "available": False,
            "error": str(e),
            "latency_ms": latency,
            "availability_pct_since_start": _availability_pct(),
        }


@app.get("/records")
def records(limit: int = Query(100, ge=1, le=1000)):
    """Return recent availability check records from the database."""
    items = get_last_records(limit)
    return {"count": len(items), "items": items}


@app.get("/stats")
def stats():
    """Return current in-memory availability statistics."""
    with _stats_lock:
        total = _total_checks
        ok = _ok_checks
    return {
        "target_url": TARGET_URL,
        "total_checks": total,
        "ok_checks": ok,
        "availability_pct": round(ok / total * 100, 2) if total else None,
    }
