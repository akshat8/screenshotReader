import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

SCREENSHOTS_COLLECTION = "screenshots"

_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongodb(mongodb_uri: str) -> None:
    global _client
    _client = AsyncIOMotorClient(mongodb_uri)
    await _client.admin.command("ping")
    logger.info("Connected to MongoDB")


async def close_mongodb_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client().get_default_database()


def get_screenshots_collection():
    return get_database()[SCREENSHOTS_COLLECTION]


async def init_indexes() -> None:
    collection = get_screenshots_collection()

    await collection.create_index(
        [("processing_status", 1), ("created_at", -1)],
        name="status_created_at",
    )
    await collection.create_index(
        [("searchable_text", "text"), ("ocr_text", "text")],
        name="screenshots_text_search",
    )
    await collection.create_index(
        "file_hash",
        unique=True,
        sparse=True,
        name="file_hash_unique",
    )
    logger.info("MongoDB indexes initialized")


async def verify_mongodb_read_write() -> bool:
    """Insert and read a transient document to verify DB operations."""
    collection = get_screenshots_collection()
    test_doc = {
        "_test": True,
        "filename": "__healthcheck__",
        "file_path": "__healthcheck__",
        "processing_status": "pending",
    }
    result = await collection.insert_one(test_doc)
    fetched = await collection.find_one({"_id": result.inserted_id})
    await collection.delete_one({"_id": result.inserted_id})
    return fetched is not None and fetched.get("filename") == "__healthcheck__"
