from app.services.searchable_text import build_searchable_text


def test_build_searchable_text_combines_ocr_and_description():
    result = build_searchable_text("9876543210", "WhatsApp chat with phone number")
    assert "OCR:" in result
    assert "9876543210" in result
    assert "IMAGE DESCRIPTION:" in result
    assert "WhatsApp chat" in result


def test_build_searchable_text_handles_empty_ocr():
    result = build_searchable_text("", "Hotel booking screenshot")
    assert "OCR:" in result
    assert "Hotel booking screenshot" in result
