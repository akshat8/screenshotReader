from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.screenshot import ProcessingStatus


class UploadScreenshotItem(BaseModel):
    id: str
    filename: str
    status: ProcessingStatus


class UploadResponse(BaseModel):
    uploaded: int
    screenshots: List[UploadScreenshotItem]


class ScreenshotSummary(BaseModel):
    id: str
    filename: str
    status: ProcessingStatus


class ScreenshotListResponse(BaseModel):
    screenshots: List[ScreenshotSummary]


class ScreenshotDetail(BaseModel):
    id: str
    filename: str
    file_path: str
    status: ProcessingStatus
    ocr_text: Optional[str] = None
    image_description: Optional[str] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
