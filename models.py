from pydantic import BaseModel


class PageResult(BaseModel):
    source_url: str
    title: str
    meta_description: str
    body_text: str
    status: str
    link_text: str = ""
    link_context: str = ""


class ScrapeResponse(BaseModel):
    total_pages: int
    total_index_pages: int
    results: list[PageResult]
