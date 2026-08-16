import logging
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from app.config import BACKEND_ROOT, settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = frozenset({"png", "jpg", "jpeg", "webp"})

EXTENSION_TO_MEDIA_TYPE = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}


def get_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    return suffix


def validate_extension(filename: str) -> str:
    extension = get_extension(filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for '{filename}'. Allowed: PNG, JPG, JPEG, WEBP.",
        )
    return extension


def validate_file_size(file_size: int) -> None:
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.max_file_size_mb} MB.",
        )


def resolve_file_path(file_path: str) -> Path:
    path = Path(file_path)
    if not path.is_absolute():
        path = BACKEND_ROOT / path
    return path.resolve()


def get_media_type_for_path(file_path: str) -> str:
    extension = get_extension(file_path)
    return EXTENSION_TO_MEDIA_TYPE.get(extension, "application/octet-stream")


async def save_upload_file(
    file_content: bytes,
    extension: str,
    screenshot_id: str | None = None,
) -> tuple[str, str]:
    """Save bytes to disk. Returns (screenshot_id, relative_file_path)."""
    validate_file_size(len(file_content))

    screenshot_id = screenshot_id or str(uuid4())
    upload_dir = settings.upload_path
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{screenshot_id}.{extension}"
    absolute_path = upload_dir / stored_name
    absolute_path.write_bytes(file_content)

    relative_path = str(Path(settings.upload_dir) / stored_name).replace("\\", "/")
    if relative_path.startswith("./"):
        relative_path = relative_path[2:]

    logger.info("Saved upload to %s", absolute_path)
    return screenshot_id, relative_path
