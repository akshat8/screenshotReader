def build_searchable_text(ocr_text: str | None, image_description: str | None) -> str:
    ocr_section = (ocr_text or "").strip()
    description_section = (image_description or "").strip()
    return f"OCR:\n{ocr_section}\n\nIMAGE DESCRIPTION:\n{description_section}"
