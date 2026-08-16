import logging
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from app.db.mongodb import get_screenshots_collection
from app.models.screenshot import ProcessingStatus, ScreenshotDocument

logger = logging.getLogger(__name__)


def parse_object_id(screenshot_id: str) -> ObjectId:
    try:
        return ObjectId(screenshot_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid screenshot ID format.")


def document_to_summary(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "filename": document["filename"],
        "status": document["processing_status"],
    }


def document_to_detail(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "filename": document["filename"],
        "file_path": document["file_path"],
        "status": document["processing_status"],
        "ocr_text": document.get("ocr_text"),
        "image_description": document.get("image_description"),
        "processing_error": document.get("processing_error"),
        "created_at": document["created_at"],
        "updated_at": document["updated_at"],
    }


async def get_screenshot_by_file_hash(file_hash: str) -> Optional[dict[str, Any]]:
    collection = get_screenshots_collection()
    return await collection.find_one({"file_hash": file_hash})


async def create_screenshot(
    screenshot_id: str,
    filename: str,
    file_path: str,
    file_hash: str,
) -> dict[str, Any]:
    object_id = parse_object_id(screenshot_id)
    now = datetime.utcnow()
    document = ScreenshotDocument(
        filename=filename,
        file_path=file_path,
        file_hash=file_hash,
        processing_status=ProcessingStatus.PROCESSING,
        pinecone_id=screenshot_id,
        created_at=now,
        updated_at=now,
    )
    mongo_doc = document.to_mongo()
    mongo_doc["_id"] = object_id
    collection = get_screenshots_collection()
    await collection.insert_one(mongo_doc)
    created = await collection.find_one({"_id": object_id})
    if created is None:
        raise HTTPException(status_code=500, detail="Failed to create screenshot record.")
    return created


async def list_screenshots() -> list[dict[str, Any]]:
    collection = get_screenshots_collection()
    cursor = collection.find().sort("created_at", -1)
    return await cursor.to_list(length=None)


async def get_screenshot_by_id(screenshot_id: str) -> Optional[dict[str, Any]]:
    collection = get_screenshots_collection()
    object_id = parse_object_id(screenshot_id)
    return await collection.find_one({"_id": object_id})


async def get_screenshot_or_404(screenshot_id: str) -> dict[str, Any]:
    document = await get_screenshot_by_id(screenshot_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Screenshot not found.")
    return document


def _to_object_id(screenshot_id: str) -> ObjectId:
    try:
        return ObjectId(screenshot_id)
    except InvalidId:
        raise ValueError(f"Invalid screenshot ID: {screenshot_id}")


async def update_screenshot_completed(
    screenshot_id: str,
    ocr_text: str,
    image_description: str,
    searchable_text: str,
) -> None:
    collection = get_screenshots_collection()
    object_id = _to_object_id(screenshot_id)
    await collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "ocr_text": ocr_text,
                "image_description": image_description,
                "searchable_text": searchable_text,
                "processing_status": ProcessingStatus.COMPLETED.value,
                "processing_error": None,
                "updated_at": datetime.utcnow(),
            }
        },
    )


async def update_screenshot_failed(screenshot_id: str, error_message: str) -> None:
    collection = get_screenshots_collection()
    object_id = _to_object_id(screenshot_id)
    safe_message = error_message[:1000]
    await collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "processing_status": ProcessingStatus.FAILED.value,
                "processing_error": safe_message,
                "updated_at": datetime.utcnow(),
            }
        },
    )
    logger.error("Screenshot %s processing failed: %s", screenshot_id, safe_message)
