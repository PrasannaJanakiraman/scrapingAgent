"""FastAPI entry point for the web scraper API."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config_parser import parse_excel_config
from cosmos_db import delete_all_items, get_all_items
from models import ScrapeResponse
from scraper import run_crawler_sync

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Web Scraper API",
    version="1.0.0",
    description=(
        "Upload a config .xlsx file and receive scraped page content as JSON. "
        "Powered by Playwright + Crawlee."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# One scrape at a time — Playwright is resource-heavy and Crawlee uses a
# single storage directory per process.
_crawl_lock = asyncio.Lock()


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


@app.post("/scrape", response_model=ScrapeResponse, tags=["scrape"])
async def scrape(
    file: UploadFile = File(..., description="Excel config file (.xlsx)"),
):
    """
    Upload a config `.xlsx` file and scrape all listed URLs.

    **Required columns in the Excel file:**

    | Column | Description |
    |---|---|
    | Application URL | Target URL to crawl |
    | Application Tag | HTML tags to extract text from (comma-separated) |
    | Remove Tags | CSS class/ID keywords to strip as noise |
    | Pagination Tags | Keywords that identify pagination containers |
    | Main Tags | Tags that wrap the main content |
    | Main Class | CSS classes paired positionally with Main Tags |
    | Next Page Strategy | 1 = CSS selectors, 2 = text match (comma-separated) |
    | Next Page Text Patterns | Custom link texts that mean "next page" |
    | Remove Content | Regex patterns — matching lines are dropped from output |
    | Single Page | `true`/`false` — scrape URL directly, skip link extraction |

    **Returns** a JSON object with all scraped page results.
    """
    if not (file.filename or "").endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are accepted.")

    contents = await file.read()

    try:
        configs = parse_excel_config(contents)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse Excel file: {exc}")

    if not configs:
        raise HTTPException(
            status_code=422,
            detail="No valid rows found. Make sure 'Application URL' column is present and populated.",
        )

    async with _crawl_lock:
        try:
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(max_workers=1) as pool:
                result = await loop.run_in_executor(pool, run_crawler_sync, configs)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Crawler error: {exc}")

    return result


@app.delete("/scrape/data", tags=["scrape"])
async def delete_all_data():
    """Delete all scraped data from CosmosDB."""
    count = delete_all_items()
    return {"deleted": count}


# ── UI Data Endpoints ─────────────────────────────────────────────────────────


def _derive_category(url: str) -> str:
    """Extract a human-readable category from a URL's domain."""
    try:
        host = urlparse(url).hostname or ""
        parts = host.replace("www.", "").split(".")
        return parts[0].title() if parts else "Other"
    except Exception:
        return "Other"


@app.get("/api/items", tags=["ui"])
async def get_items(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """Return all scraped items, optionally filtered by category or status."""
    items = get_all_items()
    for item in items:
        item["category"] = _derive_category(item.get("url", ""))

    if category:
        items = [i for i in items if i["category"] == category]
    if status:
        items = [i for i in items if i.get("status", "").lower() == status.lower()]

    return {"items": items}


@app.get("/api/filters", tags=["ui"])
async def get_filters():
    """Return distinct category and status values for filter dropdowns."""
    items = get_all_items()
    categories = sorted({_derive_category(i.get("url", "")) for i in items})
    statuses = sorted({i.get("status", "Unknown") for i in items})
    return {"categories": categories, "statuses": statuses}


# ── Serve Frontend ────────────────────────────────────────────────────────────

@app.get("/", tags=["ui"])
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")