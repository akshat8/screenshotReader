from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ScreenshotDocument(BaseModel):
    """MongoDB document shape for the screenshots collection."""

    filename: str
    file_path: str
    file_hash: Optional[str] = None
    ocr_text: Optional[str] = None
    image_description: Optional[str] = None
    searchable_text: Optional[str] = None
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    processing_error: Optional[str] = None
    pinecone_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_mongo(self) -> dict:
        data = self.model_dump(exclude_none=True)
        data["processing_status"] = self.processing_status.value
        return data
