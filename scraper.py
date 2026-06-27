"""Core scraping logic: HTML cleaning, content extraction, and the Playwright crawler."""

import os
import re
import tempfile
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from crawlee import Request
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

from config_parser import ScrapingConfig


# ── Data Types ─────────────────────────────────────────────────────────────────

@dataclass
class URLElementDetail:
    url: str
    link_text: str
    element_class: str
    element_id: str
    tag_name: str
    parent_tag: str
    context: str
    attributes: dict


# ── CSS Selectors Used for "Next Page" Detection ───────────────────────────────

NEXT_PAGE_SELECTORS = [
    "a[rel='next']",
    "a.next",
    "a.next-page",
    "li.next a",
    "li.pager-next a",
    ".pagination a[aria-label='Next']",
    ".pagination a[aria-label='next']",
    "a[aria-label='Next page']",
    "a[aria-label='next page']",
    ".pager__item--next a",
    "a:has(span.sr-only:-soup-contains('Next'))",
]


# ── HTML Cleaning ──────────────────────────────────────────────────────────────

def remove_header_footer_elements(
    soup: BeautifulSoup,
    keep_pagination_nav: bool = False,
    remove_tags: list = None,
    pagination_tags: list = None,
) -> BeautifulSoup:
    """Decompose noisy structural elements (header, footer, nav, etc.).

    Args:
        keep_pagination_nav: Pass True on INDEX pages so pagination <nav>s survive.
        remove_tags:         Class/ID keywords to treat as noise (overrides defaults).
        pagination_tags:     Class/ID keywords that identify pagination containers.
    """
    noise_keywords = remove_tags or [
        "header", "footer", "navbar", "navigation", "site-nav",
        "top-bar", "bottom-bar", "menu", "breadcrumb", "sidebar", "cookie",
    ]
    pagination_keywords = pagination_tags or [
        "pagination", "pager", "paging", "page-numbers", "nav-links", "pages",
    ]

    def _is_noise(tag) -> bool:
        if tag.name in ("body", "html", "main", "article"):
            return False

        classes = " ".join(tag.get("class", [])).lower()
        tag_id = tag.get("id", "").lower()

        # Protect pagination navs when crawling index/listing pages
        if keep_pagination_nav and tag.name == "nav":
            if any(kw in classes or kw in tag_id for kw in pagination_keywords):
                return False
            if tag.find("a", rel="next") or tag.find("a", rel="prev"):
                return False
            if any(re.search(r"next|›|»", a.get_text(), re.I) for a in tag.find_all("a")):
                return False

        if tag.name in ("header", "footer"):
            return True
        if tag.name == "nav" and not keep_pagination_nav:
            return True
        if any(kw in classes or kw in tag_id for kw in noise_keywords):
            return True

        return False

    for element in soup.find_all(_is_noise):
        if not element.decomposed:
            element.decompose()

    return soup


# ── Main Content Locator ───────────────────────────────────────────────────────

def find_main_content(
    soup: BeautifulSoup,
    main_tags: list = None,
    main_classes: list = None,
) -> list:
    """Return all content containers matching the supplied tag/class pairs.

    main_tags and main_classes are positionally paired (index 0 goes together,
    index 1 goes together, etc.).  Falls back to common semantic landmarks, then
    soup.body, when nothing matches.
    """
    if not main_tags:
        fallback = (
            soup.find("main")
            or soup.find("article")
            or soup.find(id=re.compile(r"content|main|body", re.I))
            or soup.find(class_=re.compile(r"content|main|body", re.I))
            or soup.body
        )
        return [fallback] if fallback else []

    classes = list(main_classes) if main_classes else []
    results = []

    for i, tag in enumerate(main_tags):
        class_name = classes[i] if i < len(classes) else ""

        if class_name:
            # Support multi-word class strings (AND match)
            cls = class_name.split() if " " in class_name else class_name
            matched = soup.find_all(tag, class_=cls)
        else:
            # Try tag name, then id~=tag, then class~=tag
            matched = (
                soup.find_all(tag)
                or soup.find_all(id=re.compile(rf"{re.escape(tag)}", re.I))
                or soup.find_all(class_=re.compile(rf"{re.escape(tag)}", re.I))
            )

        results.extend(matched)

    return results or ([soup.body] if soup.body else [])


# ── Pagination ─────────────────────────────────────────────────────────────────

def find_next_page(
    soup: BeautifulSoup,
    base_url: str,
    pagination_tags: list = None,
    strategies: list = None,
    next_page_texts: list = None,
) -> str | None:
    """Return the absolute URL of the next page, or None if there isn't one.

    Strategy 1 — CSS selector match against known next-page patterns.
    Strategy 2 — Text match inside pagination containers.
    """
    active = [int(s) for s in (strategies or [1, 2])]

    pattern_str = (
        "|".join(re.escape(t.strip()) for t in next_page_texts)
        if next_page_texts
        else r"next|next page|›|»|forward|older posts?"
    )
    next_re = re.compile(rf"^\s*({pattern_str})\s*$", re.IGNORECASE)

    if 1 in active:
        for selector in NEXT_PAGE_SELECTORS:
            try:
                tag = soup.select_one(selector)
                if tag and tag.get("href"):
                    return urljoin(base_url, tag["href"])
            except Exception:
                continue

    if 2 in active:
        default_css = (
            ".pagination, .pager, .paging, nav[aria-label*='pagination' i], "
            ".page-numbers, ul.pages, .nav-links"
        )
        if pagination_tags:
            dynamic = ", ".join(
                [f".{t}" for t in pagination_tags] + [f"#{t}" for t in pagination_tags]
            )
            pagination_css = f"{default_css}, {dynamic}"
        else:
            pagination_css = default_css

        for container in soup.select(pagination_css):
            for a in container.find_all("a", href=True):
                if next_re.match(a.get_text(strip=True)):
                    return urljoin(base_url, a["href"])

    return None


# ── Link Extraction Helpers ────────────────────────────────────────────────────

def _extract_context(element, tag_list: list) -> str:
    """Walk up to 5 ancestors looking for a meaningful text block."""
    parent = element.parent
    for _ in range(5):
        if parent is None:
            break
        if parent.name in tag_list:
            text = " ".join(parent.get_text(separator=" ", strip=True).split())
            if len(text) > 30:
                return text[:300]
        parent = parent.parent
    return ""


def _is_in_pagination(element, pagination_keywords: list) -> bool:
    """Return True if the element or any ancestor is a pagination container."""
    for node in [element, *element.parents]:
        if not hasattr(node, "get") or node.name in ("body", "html", "[document]"):
            break
        classes = " ".join(node.get("class", [])).lower()
        tag_id = node.get("id", "").lower()
        if any(kw in classes or kw in tag_id for kw in pagination_keywords):
            return True
    return False


def extract_url_details(
    soup: BeautifulSoup,
    base_url: str,
    tag_list: list,
    remove_tags: list = None,
    pagination_tags: list = None,
    main_tags: list = None,
    main_classes: list = None,
) -> list[URLElementDetail]:
    """Extract all non-pagination links from the main content area."""
    soup = remove_header_footer_elements(
        soup,
        keep_pagination_nav=True,
        remove_tags=remove_tags,
        pagination_tags=pagination_tags,
    )
    containers = find_main_content(soup, main_tags=main_tags, main_classes=main_classes)
    results: list[URLElementDetail] = []

    for link in (a for c in containers for a in c.find_all("a", href=True)):
        href = link.get("href", "").strip()
        if not href or href.startswith(("#", "javascript:")):
            continue
        try:
            absolute_url = urljoin(base_url, href)
        except Exception:
            continue

        if pagination_tags and _is_in_pagination(link, pagination_tags):
            continue

        results.append(
            URLElementDetail(
                url=absolute_url,
                link_text=(
                    link.get_text(strip=True)
                    or link.get("title", link.get("aria-label", "[No text]"))
                ),
                element_class=" ".join(link.get("class", [])),
                element_id=link.get("id", ""),
                tag_name="a",
                parent_tag=link.parent.name if link.parent else "unknown",
                context=_extract_context(link, tag_list),
                attributes={
                    k: v for k, v in link.attrs.items() if k not in ("href", "class", "id")
                },
            )
        )

    return results


# ── Page Content Extraction ────────────────────────────────────────────────────

def _apply_remove_content(text: str, remove_patterns: list) -> str:
    """Drop lines matching any of the supplied regex patterns."""
    if not remove_patterns:
        return text
    filtered = [
        line for line in text.splitlines()
        if not any(re.search(p, line, re.IGNORECASE) for p in remove_patterns)
    ]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(filtered))


def extract_page_content(
    soup: BeautifulSoup,
    tag_list: list = None,
    remove_tags: list = None,
    pagination_tags: list = None,
    main_tags: list = None,
    main_classes: list = None,
    remove_content: list = None,
) -> dict:
    """Extract title, meta description, and body text from a content page."""
    title = soup.title.get_text(strip=True) if soup.title else ""
    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_tag.get("content", "") if meta_tag else ""

    for tag in soup.find_all(("script", "style", "noscript", "iframe")):
        tag.decompose()

    soup = remove_header_footer_elements(
        soup,
        keep_pagination_nav=False,
        remove_tags=remove_tags,
        pagination_tags=pagination_tags,
    )
    mains = find_main_content(soup, main_tags=main_tags, main_classes=main_classes)

    if tag_list and mains:
        body_text = "\n".join(
            el.get_text(separator="\n", strip=True)
            for container in mains
            for el in container.find_all(tag_list)
        )
    else:
        body_text = "\n".join(
            container.get_text(separator="\n", strip=True) for container in mains
        )

    # If main-content detection returned very little text, fall back to the
    # full <body> so we don't return near-empty results.
    if len(body_text.strip()) < 50 and soup.body:
        body_text = soup.body.get_text(separator="\n", strip=True)

    body_text = re.sub(r"\n{3,}", "\n\n", body_text)
    body_text = _apply_remove_content(body_text, remove_content)

    return {"title": title, "meta_description": meta_desc, "body_text": body_text}


# ── Crawler ────────────────────────────────────────────────────────────────────

def _build_user_data(config: ScrapingConfig, page_num: int = 1) -> dict:
    """Serialise a ScrapingConfig into a Crawlee user_data dict."""
    return {
        "page_num": page_num,
        "base_url": config.app_url,
        "tag_list": config.tag_list,
        "remove_tags": config.remove_tags,
        "pagination_tags": config.pagination_tags,
        "main_tags": config.main_tags,
        "main_classes": config.main_classes,
        "strategies": config.strategies,
        "next_page_texts": config.next_page_texts,
        "remove_content": config.remove_content,
    }


# async def run_crawler(configs: list[ScrapingConfig]) -> dict:
#     """Run the Playwright crawler for all configs and return results as a dict.

#     Uses a temporary directory for Crawlee's storage so concurrent API calls
#     do not share state.  The caller (main.py) holds a lock to prevent true
#     concurrent runs since Playwright is CPU/memory heavy.
#     """
#     state: dict = {"results": [], "visited_index": set()}

#     with tempfile.TemporaryDirectory() as tmpdir:
#         os.environ["CRAWLEE_STORAGE_DIR"] = tmpdir
#         from playwright.async_api import async_playwright
#         # Force Playwright to initialize in this event loop before Crawlee touches it
#         async with async_playwright() as p:
#             _ = p  # just ensures playwright is running in this loop
#         # crawler = PlaywrightCrawler(headless=True)
#         # change this line (around line 220):
        
#         crawler = PlaywrightCrawler(
#             headless=True,
#             browser_launch_options={"args": ["--no-sandbox", "--disable-setuid-sandbox"]},
#         )


#         @crawler.router.default_handler
#         async def handle_page(context: PlaywrightCrawlingContext):
#             url = context.request.url
#             label = context.request.label
#             ud = context.request.user_data

#             await context.page.wait_for_load_state("domcontentloaded")
#             try:
#                 await context.page.wait_for_load_state("networkidle", timeout=10_000)
#             except Exception:
#                 pass

#             soup = BeautifulSoup(await context.page.content(), "lxml")

#             tag_list        = ud.get("tag_list", [])
#             remove_tags     = ud.get("remove_tags", [])
#             pagination_tags = ud.get("pagination_tags", [])
#             main_tags       = ud.get("main_tags", [])
#             main_classes    = ud.get("main_classes", [])
#             strategies      = ud.get("strategies", [1, 2])
#             next_page_texts = ud.get("next_page_texts", [])
#             remove_content  = ud.get("remove_content", [])
#             base_url        = ud.get("base_url", url)

#             # ── INDEX: extract links + follow pagination ───────────────────
#             if label == "INDEX":
#                 state["visited_index"].add(url)
#                 page_num = ud.get("page_num", 1)

#                 details = extract_url_details(
#                     soup, url,
#                     tag_list=tag_list, remove_tags=remove_tags,
#                     pagination_tags=pagination_tags,
#                     main_tags=main_tags, main_classes=main_classes,
#                 )

#                 shared = {
#                     "base_url": base_url, "tag_list": tag_list,
#                     "remove_tags": remove_tags, "pagination_tags": pagination_tags,
#                     "main_tags": main_tags, "main_classes": main_classes,
#                     "strategies": strategies, "next_page_texts": next_page_texts,
#                     "remove_content": remove_content,
#                 }

#                 page_requests = [
#                     Request.from_url(d.url, label="PAGE", user_data={
#                         **shared, "link_text": d.link_text, "link_context": d.context,
#                     })
#                     for d in details if d.url.startswith("http")
#                 ]
#                 await context.add_requests(page_requests)

#                 next_url = find_next_page(
#                     soup, url, pagination_tags=pagination_tags,
#                     strategies=strategies, next_page_texts=next_page_texts,
#                 )
#                 if next_url and next_url not in state["visited_index"]:
#                     await context.add_requests(
#                         [Request.from_url(
#                             next_url, label="INDEX",
#                             user_data={**shared, "page_num": page_num + 1},
#                             always_enqueue=True,
#                         )],
#                         forefront=True,
#                     )

#             # ── PAGE: extract and collect content ─────────────────────────
#             elif label == "PAGE":
#                 content = extract_page_content(
#                     soup, tag_list=tag_list, remove_tags=remove_tags,
#                     pagination_tags=pagination_tags, main_tags=main_tags,
#                     main_classes=main_classes, remove_content=remove_content,
#                 )
#                 state["results"].append({
#                     "source_url": url,
#                     "title": content["title"],
#                     "meta_description": content["meta_description"],
#                     "body_text": content["body_text"],
#                     "status": "success",
#                     "link_text": ud.get("link_text", ""),
#                     "link_context": ud.get("link_context", ""),
#                 })
#                 print('state=============>',state)

#         start_requests = [
#             Request.from_url(
#                 url=cfg.app_url,
#                 label="PAGE" if cfg.single_page else "INDEX",
#                 user_data=_build_user_data(cfg),
#                 always_enqueue=True,
#             )
#             for cfg in configs
#         ]

#         await crawler.run(start_requests)

#     return {
#         "total_pages": len(state["results"]),
#         "total_index_pages": len(state["visited_index"]),
#         "results": state["results"],
#     }

async def run_crawler(configs: list[ScrapingConfig]) -> dict:
    state: dict = {"results": [], "visited_index": set()}

    os.environ["CRAWLEE_STORAGE_DIR"] = "/tmp/crawlee_storage"
    os.makedirs("/tmp/crawlee_storage", exist_ok=True)

    from crawlee.browsers import BrowserPool

    browser_pool = BrowserPool.with_default_plugin(
        headless=True,
        browser_launch_options={"args": ["--no-sandbox", "--disable-setuid-sandbox"]},
        operation_timeout=timedelta(seconds=120),
    )

    crawler = PlaywrightCrawler(browser_pool=browser_pool)

    @crawler.router.default_handler
    async def handle_page(context: PlaywrightCrawlingContext):
        url = context.request.url
        label = context.request.label
        ud = context.request.user_data

        await context.page.wait_for_load_state("domcontentloaded")
        try:
            await context.page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        soup = BeautifulSoup(await context.page.content(), "lxml")

        tag_list        = ud.get("tag_list", [])
        remove_tags     = ud.get("remove_tags", [])
        pagination_tags = ud.get("pagination_tags", [])
        main_tags       = ud.get("main_tags", [])
        main_classes    = ud.get("main_classes", [])
        strategies      = ud.get("strategies", [1, 2])
        next_page_texts = ud.get("next_page_texts", [])
        remove_content  = ud.get("remove_content", [])
        base_url        = ud.get("base_url", url)

        if label == "INDEX":
            state["visited_index"].add(url)
            page_num = ud.get("page_num", 1)

            details = extract_url_details(
                soup, url,
                tag_list=tag_list, remove_tags=remove_tags,
                pagination_tags=pagination_tags,
                main_tags=main_tags, main_classes=main_classes,
            )

            shared = {
                "base_url": base_url, "tag_list": tag_list,
                "remove_tags": remove_tags, "pagination_tags": pagination_tags,
                "main_tags": main_tags, "main_classes": main_classes,
                "strategies": strategies, "next_page_texts": next_page_texts,
                "remove_content": remove_content,
            }

            page_requests = [
                Request.from_url(d.url, label="PAGE", user_data={
                    **shared, "link_text": d.link_text, "link_context": d.context,
                })
                for d in details if d.url.startswith("http")
            ]
            await context.add_requests(page_requests)

            next_url = find_next_page(
                soup, url, pagination_tags=pagination_tags,
                strategies=strategies, next_page_texts=next_page_texts,
            )
            if next_url and next_url not in state["visited_index"]:
                await context.add_requests(
                    [Request.from_url(
                        next_url, label="INDEX",
                        user_data={**shared, "page_num": page_num + 1},
                        always_enqueue=True,
                    )],
                    forefront=True,
                )

        elif label == "PAGE":
            content = extract_page_content(
                soup, tag_list=tag_list, remove_tags=remove_tags,
                pagination_tags=pagination_tags, main_tags=main_tags,
                main_classes=main_classes, remove_content=remove_content,
            )
            state["results"].append({
                "source_url": url,
                "title": content["title"],
                "meta_description": content["meta_description"],
                "body_text": content["body_text"],
                "status": "success",
                "link_text": ud.get("link_text", ""),
                "link_context": ud.get("link_context", ""),
            })

    start_requests = [
        Request.from_url(
            url=cfg.app_url,
            label="PAGE" if cfg.single_page else "INDEX",
            user_data=_build_user_data(cfg),
            always_enqueue=True,
        )
        for cfg in configs
    ]

    await crawler.run(start_requests)

    return {
        "total_pages": len(state["results"]),
        "total_index_pages": len(state["visited_index"]),
        "results": state["results"],
    }

import asyncio
import sys
import threading
import time

# ── Persistent event loop in a background thread ─────────────────────────────
# Crawlee caches asyncio.Lock objects that are bound to the event loop they were
# created on.  Creating a new loop per request causes "bound to a different
# event loop" errors on the second call.  A single long-lived ProactorEventLoop
# avoids this entirely.

_crawler_loop: asyncio.AbstractEventLoop | None = None
_crawler_thread: threading.Thread | None = None


def _start_crawler_loop() -> None:
    global _crawler_loop
    if sys.platform == "win32":
        _crawler_loop = asyncio.ProactorEventLoop()
    else:
        _crawler_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_crawler_loop)
    _crawler_loop.run_forever()


def _ensure_crawler_loop() -> None:
    global _crawler_thread
    if _crawler_thread is None or not _crawler_thread.is_alive():
        _crawler_thread = threading.Thread(target=_start_crawler_loop, daemon=True)
        _crawler_thread.start()
        while _crawler_loop is None or not _crawler_loop.is_running():
            time.sleep(0.01)


def run_crawler_sync(configs: list[ScrapingConfig]) -> dict:
    _ensure_crawler_loop()
    future = asyncio.run_coroutine_threadsafe(run_crawler(configs), _crawler_loop)
    return future.result(timeout=300)