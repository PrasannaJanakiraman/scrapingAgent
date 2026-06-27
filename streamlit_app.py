"""Streamlit UI for uploading Excel configs, scraping, summarising, and storing results."""

import uuid
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st

from cosmos_db import get_all_items, upsert_item
from llm_summarise import summarise

SCRAPE_API_URL = "http://localhost:8000/scrape"

st.set_page_config(page_title="Web Scraper Dashboard", layout="wide")
st.title("Web Scraper Dashboard")

# ── Upload Section ────────────────────────────────────────────────────────────
st.header("Upload Excel Config")
uploaded_file = st.file_uploader("Choose an .xlsx config file", type=["xlsx"])

if uploaded_file and st.button("Start Scraping"):
    # Call the scrape API
    st.info("Calling scrape API...")
    uploaded_file.seek(0)
    try:
        resp = requests.post(
            SCRAPE_API_URL,
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            timeout=300,
        )
        resp.raise_for_status()
        scrape_result = resp.json()
    except Exception as exc:
        st.error(f"Scrape API error: {exc}")
        st.stop()

    results = scrape_result.get("results", [])

    if not results:
        st.warning("Scrape API returned no results.")
        st.stop()

    # Insert one record per scraped page using title as sourceName, body_text as scrapedData
    progress = st.progress(0, text="Summarising and saving...")
    total = len(results)

    for idx, page in enumerate(results):
        doc_id = str(uuid.uuid4())
        source_name = page.get("title", "").strip() or page.get("source_url", "")
        source_url = page.get("source_url", "")
        scraped_data = page.get("body_text", "")

        # Insert with InProgress status first
        doc = {
            "id": doc_id,
            "sourceId": doc_id,
            "sourceName": source_name,
            "url": source_url,
            "scrapeDate": datetime.now(timezone.utc).isoformat(),
            "status": "InProgress",
            "scrapedData": scraped_data[:50000],
            "summary": "",
        }
        upsert_item(doc)

        # Summarise and update to Success or Failed
        if scraped_data.strip():
            try:
                summary = summarise(scraped_data[:8000])
                doc["status"] = "Success"
                doc["summary"] = summary
            except Exception as exc:
                doc["status"] = "Failed"
                doc["summary"] = f"Summarisation failed: {exc}"
        else:
            doc["status"] = "Failed"
            doc["summary"] = "No content scraped for this page."

        upsert_item(doc)
        progress.progress((idx + 1) / total, text=f"Processed {idx + 1}/{total}")

    st.success(f"Done! {total} page(s) scraped, summarised, and saved.")

# ── Results Table ─────────────────────────────────────────────────────────────
st.header("Scrape Results")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Refresh Data"):
        st.rerun()
with col2:
    if st.button("Delete All Data", type="primary"):
        try:
            resp = requests.delete(f"{SCRAPE_API_URL}/data", timeout=30)
            resp.raise_for_status()
            deleted = resp.json().get("deleted", 0)
            st.session_state["delete_msg"] = f"Deleted {deleted} record(s)."
        except Exception as exc:
            st.session_state["delete_msg"] = f"Delete failed: {exc}"
        st.rerun()

if "delete_msg" in st.session_state:
    st.success(st.session_state.pop("delete_msg"))

try:
    items = get_all_items()
except Exception as exc:
    st.error(f"Could not load data from CosmosDB: {exc}")
    items = []

if items:
    display_df = pd.DataFrame(items)
    columns_to_show = ["sourceName", "url", "status", "scrapedData", "summary"]
    available = [c for c in columns_to_show if c in display_df.columns]
    st.dataframe(display_df[available], use_container_width=True, hide_index=True)
else:
    st.info("No records found. Upload an Excel file to start scraping.")
