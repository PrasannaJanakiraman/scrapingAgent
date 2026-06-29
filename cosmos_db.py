"""CosmosDB operations for storing and retrieving scrape results."""

import os

from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey

load_dotenv()

_client = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=os.environ["COSMOS_KEY"])
_database = _client.create_database_if_not_exists(os.environ.get("COSMOS_DATABASE_NAME", "Regulatory_Data"))
_container = _database.create_container_if_not_exists(
    id=os.environ.get("COSMOS_CONTAINER_NAME", "SourceDate"),
    partition_key=PartitionKey(path="/sourceId"),
)


def upsert_item(item: dict) -> dict:
    """Insert or update a document in CosmosDB."""
    return _container.upsert_item(item)


def get_all_items() -> list[dict]:
    """Return all documents from the container."""
    query = "SELECT c.id, c.sourceId, c.sourceName, c.url, c.scrapeDate, c.status, c.scrapedData, c.summary, c.country, c.category FROM c"
    return list(_container.query_items(query=query, enable_cross_partition_query=True))


def delete_all_items() -> int:
    """Delete all documents from the container. Returns the count of deleted items."""
    items = list(_container.query_items(query="SELECT c.id, c.sourceId FROM c", enable_cross_partition_query=True))
    for item in items:
        _container.delete_item(item["id"], partition_key=item["sourceId"])
    return len(items)
