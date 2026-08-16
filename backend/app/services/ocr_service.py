import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr

        logger.info("Initializing EasyOCR reader")
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def extract_text(image_path: str) -> str:
    """Extract text from an image file. Returns empty string if no text found."""
    try:
        reader = _get_reader()
        results = reader.readtext(image_path, detail=0, paragraph=True)
        if not results:
            return ""
        return "\n".join(str(line) for line in results).strip()
    except Exception as exc:
        logger.error("OCR failed for %s: %s", image_path, exc)
        raise RuntimeError(f"OCR extraction failed: {exc}") from exc
