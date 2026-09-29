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
            "app.graphs.processing_graph.get_screenshot_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "app.graphs.processing_graph.update_screenshot_completed",
            new_callable=AsyncMock,
        ) as mock_completed,
        patch(
            "app.graphs.processing_graph.update_screenshot_failed",
            new_callable=AsyncMock,
        ) as mock_failed,
        patch("app.services.file_service.BACKEND_ROOT", tmp_path),
        patch(
            "app.graphs.processing_graph.extract_text", return_value="sample ocr"
        ),
        patch(
            "app.graphs.processing_graph.describe_image",
            new_callable=AsyncMock,
            return_value="sample description",
        ),
        patch(
            "app.graphs.processing_graph.embed_text",
            return_value=[0.1] * 1024,
        ),
        patch(
            "app.graphs.processing_graph.upsert_screenshot_vector",
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
async def test_process_screenshot_falls_back_to_ocr_when_vision_fails(tmp_path: Path):
    with (
        patch(
            "app.graphs.processing_graph.get_screenshot_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "app.graphs.processing_graph.update_screenshot_completed",
            new_callable=AsyncMock,
        ) as mock_completed,
        patch(
            "app.graphs.processing_graph.update_screenshot_failed",
            new_callable=AsyncMock,
        ) as mock_failed,
        patch("app.services.file_service.BACKEND_ROOT", tmp_path),
        patch("app.graphs.processing_graph.extract_text", return_value="ocr text"),
        patch(
            "app.graphs.processing_graph.describe_image",
            new_callable=AsyncMock,
            side_effect=RuntimeError("OpenRouter down"),
        ) as mock_describe,
        patch(
            "app.graphs.processing_graph.embed_text",
            return_value=[0.1] * 1024,
        ),
        patch(
            "app.graphs.processing_graph.upsert_screenshot_vector",
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

        assert mock_describe.await_count == 2
        mock_upsert.assert_awaited_once()
        mock_failed.assert_not_awaited()
        mock_completed.assert_awaited_once()
        assert mock_completed.await_args.kwargs["ocr_text"] == "ocr text"
        assert mock_completed.await_args.kwargs["image_description"] == ""
        assert "ocr text" in mock_completed.await_args.kwargs["searchable_text"]


@pytest.mark.asyncio
async def test_process_screenshot_retries_ocr_then_succeeds(tmp_path: Path):
    with (
        patch(
            "app.graphs.processing_graph.get_screenshot_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "app.graphs.processing_graph.update_screenshot_completed",
            new_callable=AsyncMock,
        ) as mock_completed,
        patch(
            "app.graphs.processing_graph.update_screenshot_failed",
            new_callable=AsyncMock,
        ) as mock_failed,
        patch("app.services.file_service.BACKEND_ROOT", tmp_path),
        patch(
            "app.graphs.processing_graph.extract_text",
            side_effect=[RuntimeError("reader busy"), "sample ocr"],
        ) as mock_ocr,
        patch(
            "app.graphs.processing_graph.describe_image",
            new_callable=AsyncMock,
            return_value="sample description",
        ),
        patch(
            "app.graphs.processing_graph.embed_text",
            return_value=[0.1] * 1024,
        ),
        patch(
            "app.graphs.processing_graph.upsert_screenshot_vector",
            new_callable=AsyncMock,
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

        assert mock_ocr.call_count == 2
        mock_completed.assert_awaited_once()
        mock_failed.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_screenshot_marks_failed_when_ocr_keeps_failing(tmp_path: Path):
    with (
        patch(
            "app.graphs.processing_graph.get_screenshot_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "app.graphs.processing_graph.update_screenshot_completed",
            new_callable=AsyncMock,
        ) as mock_completed,
        patch(
            "app.graphs.processing_graph.update_screenshot_failed",
            new_callable=AsyncMock,
        ) as mock_failed,
        patch("app.services.file_service.BACKEND_ROOT", tmp_path),
        patch(
            "app.graphs.processing_graph.extract_text",
            side_effect=RuntimeError("unreadable image"),
        ) as mock_ocr,
        patch(
            "app.graphs.processing_graph.describe_image",
            new_callable=AsyncMock,
        ) as mock_describe,
    ):
        uploads_dir = tmp_path / "uploads"
        uploads_dir.mkdir()
        write_test_image(uploads_dir / "screenshot-id.png")

        mock_get.return_value = {
            "filename": "test.png",
            "file_path": "uploads/screenshot-id.png",
        }

        await process_screenshot("507f1f77bcf86cd799439011")

        assert mock_ocr.call_count == 2
        mock_describe.assert_not_awaited()
        mock_completed.assert_not_awaited()
        mock_failed.assert_awaited_once()
        assert mock_failed.await_args.args[0] == "507f1f77bcf86cd799439011"
        assert "OCR extraction failed" in mock_failed.await_args.args[1]


@pytest.mark.asyncio
async def test_process_screenshot_marks_failed_when_vision_fails_without_ocr(
    tmp_path: Path,
):
    with (
        patch(
            "app.graphs.processing_graph.get_screenshot_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "app.graphs.processing_graph.update_screenshot_completed",
            new_callable=AsyncMock,
        ) as mock_completed,
        patch(
            "app.graphs.processing_graph.update_screenshot_failed",
            new_callable=AsyncMock,
        ) as mock_failed,
        patch("app.services.file_service.BACKEND_ROOT", tmp_path),
        patch("app.graphs.processing_graph.extract_text", return_value="   "),
        patch(
            "app.graphs.processing_graph.describe_image",
            new_callable=AsyncMock,
            side_effect=RuntimeError("OpenRouter down"),
        ) as mock_describe,
    ):
        uploads_dir = tmp_path / "uploads"
        uploads_dir.mkdir()
        write_test_image(uploads_dir / "screenshot-id.png")

        mock_get.return_value = {
            "filename": "test.png",
            "file_path": "uploads/screenshot-id.png",
        }

        await process_screenshot("507f1f77bcf86cd799439011")

        assert mock_describe.await_count == 2
        mock_completed.assert_not_awaited()
        mock_failed.assert_awaited_once()
        assert "no OCR text" in mock_failed.await_args.args[1]
