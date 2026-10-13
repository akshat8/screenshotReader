from app.services.query_helpers import NOT_FOUND_MESSAGE
from app.services.retrieval_service import _normalize_scores


def test_normalize_scores_empty():
    assert _normalize_scores({}) == {}


def test_normalize_scores_scales_to_max_one():
    scores = _normalize_scores({"a": 2.0, "b": 4.0})
    assert scores["a"] == 0.5
    assert scores["b"] == 1.0


def test_not_found_message_constant():
    assert "couldn't find enough information" in NOT_FOUND_MESSAGE.lower()
