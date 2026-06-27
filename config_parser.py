from dataclasses import dataclass, field
from io import BytesIO

import pandas as pd


def parse_config_list(value, default=None, lowercase: bool = True) -> list:
    """Parse a comma-separated Excel cell value into a clean Python list.

    Returns an empty list (or `default`) when the cell is blank or NaN.
    Positional pairing with other lists is preserved by keeping all items,
    including empty strings.
    """
    if not value or isinstance(value, float):
        return default or []
    items = [t.strip() for t in str(value).split(",")]
    return [t.lower() for t in items] if lowercase else items


@dataclass
class ScrapingConfig:
    """All configuration for a single scrape target, parsed from one Excel row."""

    app_url: str
    tag_list: list = field(default_factory=list)
    remove_tags: list = field(default_factory=list)
    pagination_tags: list = field(default_factory=list)
    main_tags: list = field(default_factory=list)
    main_classes: list = field(default_factory=list)
    strategies: list = field(default_factory=lambda: [1, 2])
    next_page_texts: list = field(default_factory=list)
    remove_content: list = field(default_factory=list)
    single_page: bool = False


def parse_excel_config(file_bytes: bytes) -> list[ScrapingConfig]:
    """Read an .xlsx file and return one ScrapingConfig per valid row."""
    df = pd.read_excel(BytesIO(file_bytes))
    configs: list[ScrapingConfig] = []

    for _, row in df.iterrows():
        app_url = row.get("Application URL")
        if not app_url or isinstance(app_url, float):
            continue

        strategies_raw = parse_config_list(row.get("Next Page Strategy"))
        strategies = [int(s) for s in strategies_raw if str(s).isdigit()] or [1, 2]

        single_page_val = row.get("Single Page")
        single_page = (
            str(single_page_val).strip().lower() in ("true", "1", "yes")
            if single_page_val and not isinstance(single_page_val, float)
            else False
        )

        configs.append(
            ScrapingConfig(
                app_url=str(app_url).strip(),
                tag_list=parse_config_list(row.get("Application Tag")),
                remove_tags=parse_config_list(row.get("Remove Tags")),
                pagination_tags=parse_config_list(row.get("Pagination Tags")),
                main_tags=parse_config_list(row.get("Main Tags")),
                main_classes=parse_config_list(row.get("Main Class"), lowercase=False),
                strategies=strategies,
                next_page_texts=parse_config_list(row.get("Next Page Text Patterns")),
                remove_content=parse_config_list(row.get("Remove Content"), lowercase=False),
                single_page=single_page,
            )
        )

    return configs
