from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from app.services.processing_service import process_screenshot
from PIL import Image


def write_test_image(path: Path) -> None:
    image = Image.new("RGB", (20, 20), color="blue")
    image.save(path, format="PNG")


@pytest.mark.asyncio
async def test_process_screenshot_success(tmp_path: Path):
    with (
        patch(
            "app.services.processing_service.get_screenshot_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "app.services.processing_service.update_screenshot_completed",
            new_callable=AsyncMock,
        ) as mock_completed,
        patch(
            "app.services.processing_service.update_screenshot_failed",
            new_callable=AsyncMock,
        ) as mock_failed,
        patch("app.services.file_service.BACKEND_ROOT", tmp_path),
        patch(
            "app.services.processing_service.extract_text", return_value="sample ocr"
        ),
        patch(
            "app.services.processing_service.describe_image",
            new_callable=AsyncMock,
            return_value="sample description",
        ),
        patch(
            "app.services.processing_service.embed_text",
            return_value=[0.1] * 1024,
        ),
        patch(
            "app.services.processing_service.upsert_screenshot_vector",
            new_callable=AsyncMock,
        ) as mock_upsert,
    ):
        uploads_dir = tmp_path / "uploads"
        uploads_dir.mkdir()
        write_test_image(uploads_dir / "screenshot-id.png")

        mock_get.return_value = {
            "filename": "test.png",
            "file_path": "uploads/screenshot-id.png",
        }

        await process_screenshot("507f1f77bcf86cd799439011")

        mock_upsert.assert_awaited_once()
        mock_completed.assert_awaited_once()
        mock_failed.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_screenshot_marks_failed_on_error(tmp_path: Path):
    with (
        patch(
            "app.services.processing_service.get_screenshot_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "app.services.processing_service.update_screenshot_completed",
            new_callable=AsyncMock,
        ) as mock_completed,
        patch(
            "app.services.processing_service.update_screenshot_failed",
            new_callable=AsyncMock,
        ) as mock_failed,
        patch("app.services.file_service.BACKEND_ROOT", tmp_path),
        patch("app.services.processing_service.extract_text", return_value="ocr text"),
        patch(
            "app.services.processing_service.describe_image",
            new_callable=AsyncMock,
            side_effect=RuntimeError("OpenRouter down"),
        ),
    ):
        uploads_dir = tmp_path / "uploads"
        uploads_dir.mkdir()
        write_test_image(uploads_dir / "screenshot-id.png")

        mock_get.return_value = {
            "filename": "test.png",
            "file_path": "uploads/screenshot-id.png",
        }

        await process_screenshot("507f1f77bcf86cd799439011")

        mock_completed.assert_not_awaited()
        mock_failed.assert_awaited_once()
