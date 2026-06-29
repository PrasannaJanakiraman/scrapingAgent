"""FastAPI entry point for the web scraper API."""

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config_parser import parse_excel_config
from cosmos_db import delete_all_items, get_all_items, upsert_item
from llm_summarise import summarise
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

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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

    # Build lookup from URL → (country, category) from the Excel config
    url_meta = {cfg.app_url: {"country": cfg.country, "category": cfg.category} for cfg in configs}

    # Save each scraped page to CosmosDB with LLM summary
    for page in result.get("results", []):
        doc_id = str(uuid.uuid4())
        source_name = (page.get("title") or "").strip() or page.get("source_url", "")
        scraped_data = page.get("body_text", "")
        meta = url_meta.get(page.get("source_url", ""), {})

        doc = {
            "id": doc_id,
            "sourceId": doc_id,
            "sourceName": source_name,
            "url": page.get("source_url", ""),
            "scrapeDate": datetime.now(timezone.utc).isoformat(),
            "status": "InProgress",
            "scrapedData": scraped_data[:50000],
            "summary": "",
            "country": meta.get("country", ""),
            "category": meta.get("category", ""),
        }
        upsert_item(doc)

        if scraped_data.strip():
            try:
                doc["summary"] = summarise(scraped_data[:8000])
                doc["status"] = "Success"
            except Exception:
                doc["status"] = "Failed"
                doc["summary"] = "Summarisation failed."
        else:
            doc["status"] = "Failed"
            doc["summary"] = "No content scraped for this page."

        upsert_item(doc)

    return result


@app.delete("/scrape/data", tags=["scrape"])
async def delete_all_data():
    """Delete all scraped data from CosmosDB."""
    count = delete_all_items()
    return {"deleted": count}


# ── UI Data Endpoints ─────────────────────────────────────────────────────────


@app.get("/api/items", tags=["ui"])
async def get_items(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
):
    """Return all scraped items, optionally filtered by category, status, or country."""
    items = get_all_items()

    if category:
        items = [i for i in items if i.get("category", "") == category]
    if status:
        items = [i for i in items if i.get("status", "").lower() == status.lower()]
    if country:
        items = [i for i in items if i.get("country", "") == country]

    return {"items": items}


@app.get("/api/filters", tags=["ui"])
async def get_filters():
    """Return distinct category, status, and country values for filter dropdowns."""
    items = get_all_items()
    categories = sorted({i.get("category", "") for i in items} - {""})
    statuses = sorted({i.get("status", "Unknown") for i in items})
    countries = sorted({i.get("country", "") for i in items} - {""})
    return {"categories": categories, "statuses": statuses, "countries": countries}


# ── Serve Frontend ────────────────────────────────────────────────────────────

@app.get("/", tags=["ui"])
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")