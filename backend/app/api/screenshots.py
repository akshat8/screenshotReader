import logging
from typing import List

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import settings
from app.schemas.screenshot import (
    ScreenshotDetail,
    ScreenshotListResponse,
    ScreenshotSummary,
    UploadResponse,
    UploadScreenshotItem,
)
from app.services.file_service import (
    compute_file_hash,
    get_media_type_for_path,
    resolve_file_path,
    save_upload_file,
    validate_extension,
)
from app.services.processing_service import process_screenshot
from app.services.screenshot_service import (
    create_screenshot,
    document_to_detail,
    document_to_summary,
    get_screenshot_by_file_hash,
    get_screenshot_or_404,
    list_screenshots,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_screenshots(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    if len(files) > settings.max_upload_count:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.max_upload_count} files allowed per upload.",
        )

    uploaded_items: list[UploadScreenshotItem] = []

    for upload_file in files:
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Filename is required.")

        extension = validate_extension(upload_file.filename)
        file_content = await upload_file.read()
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail=f"File '{upload_file.filename}' is empty.",
            )

        file_hash = compute_file_hash(file_content)
        existing = await get_screenshot_by_file_hash(file_hash)
        if existing is not None:
            uploaded_items.append(
                UploadScreenshotItem(
                    id=str(existing["_id"]),
                    filename=existing["filename"],
                    status=existing["processing_status"],
                )
            )
            continue

        screenshot_object_id = ObjectId()
        screenshot_id = str(screenshot_object_id)
        _, relative_path = await save_upload_file(
            file_content=file_content,
            extension=extension,
            screenshot_id=screenshot_id,
        )
        document = await create_screenshot(
            screenshot_id=screenshot_id,
            filename=upload_file.filename,
            file_path=relative_path,
            file_hash=file_hash,
        )
        background_tasks.add_task(process_screenshot, screenshot_id)
        uploaded_items.append(
            UploadScreenshotItem(
                id=screenshot_id,
                filename=upload_file.filename,
                status=document["processing_status"],
            )
        )

    return UploadResponse(uploaded=len(uploaded_items), screenshots=uploaded_items)


@router.get("", response_model=ScreenshotListResponse)
async def get_screenshots():
    documents = await list_screenshots()
    summaries = [
        ScreenshotSummary(**document_to_summary(document)) for document in documents
    ]
    return ScreenshotListResponse(screenshots=summaries)


@router.get("/{screenshot_id}", response_model=ScreenshotDetail)
async def get_screenshot(screenshot_id: str):
    document = await get_screenshot_or_404(screenshot_id)
    return ScreenshotDetail(**document_to_detail(document))


@router.get("/{screenshot_id}/image")
async def get_screenshot_image(screenshot_id: str):
    document = await get_screenshot_or_404(screenshot_id)
    file_path = resolve_file_path(document["file_path"])

    if not file_path.is_file():
        logger.error("Image file missing for screenshot %s: %s", screenshot_id, file_path)
        raise HTTPException(status_code=404, detail="Screenshot image file not found.")

    media_type = get_media_type_for_path(document["file_path"])
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=document["filename"],
    )
