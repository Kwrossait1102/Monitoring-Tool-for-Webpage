from __future__ import annotations
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Integer, Float, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# 1) Engine & Session
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/monitor")
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 2) Base Model
class Base(DeclarativeBase):
    pass

# 3) ORM Model
class CheckRecord(Base):
    __tablename__ = "check_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ok: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ttfb_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    consecutive_failures: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    source:Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    error: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    # prevent duplicate (url, ts)
    __table_args__ = (UniqueConstraint("url", "ts", name="uq_url_ts"),)

# 4) Create tables
def init_db() -> None:
    Base.metadata.create_all(bind=engine)

# 5) CRUD helpers
def add_record(
    ts: datetime,
    url: str,
    status_code: Optional[int],
    ok: bool,
    source: str,
    latency_ms: Optional[float],
    error: Optional[str],
    ttfb_ms: Optional[float] = None,  
    response_size_bytes: Optional[int] = None,  
    consecutive_failures: Optional[int] = None,
) -> None:
    with SessionLocal() as session:
        rec = CheckRecord(
            ts=ts,
            url=url,
            status_code=status_code,
            ok=ok,
            latency_ms=latency_ms,
            ttfb_ms=ttfb_ms,                       
            response_size_bytes=response_size_bytes,  
            consecutive_failures=consecutive_failures or 0,
            source=source,
            error=error or None,
        )
        session.add(rec)
        session.commit()

def get_last_records(limit: int = 100) -> List[Dict[str, Any]]:
    with SessionLocal() as session:
        q = session.query(CheckRecord).order_by(CheckRecord.id.desc()).limit(limit)
        rows = list(reversed(q.all()))  
        return [
            {
                "ts_iso": r.ts.replace(microsecond=0).isoformat() + "Z",
                "url": r.url,
                "status_code": r.status_code,
                "ok": r.ok,
                "latency_ms": r.latency_ms,
                "ttfb_ms": r.ttfb_ms, 
                "response_size_bytes": r.response_size_bytes, 
                "consecutive_failures": r.consecutive_failures,
                "sourde": r.source,
                "error": r.error or "",
            }
            for r in rows
        ]
