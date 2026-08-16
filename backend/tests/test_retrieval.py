from app.services.retrieval_service import _normalize_scores, RetrievalHit
from app.services.query_service import is_relevant, NOT_FOUND_MESSAGE


def test_normalize_scores_empty():
    assert _normalize_scores({}) == {}


def test_normalize_scores_scales_to_max_one():
    scores = _normalize_scores({"a": 2.0, "b": 4.0})
    assert scores["a"] == 0.5
    assert scores["b"] == 1.0


def test_is_relevant_below_threshold():
    hits = [
        RetrievalHit(
            screenshot_id="1",
            filename="a.png",
            semantic_score=0.1,
            keyword_score=0.0,
            final_score=0.07,
        )
    ]
    assert is_relevant(hits) is False


def test_is_relevant_above_threshold():
    hits = [
        RetrievalHit(
            screenshot_id="1",
            filename="a.png",
            semantic_score=0.9,
            keyword_score=0.8,
            final_score=0.87,
        )
    ]
    assert is_relevant(hits) is True


def test_not_found_message_constant():
    assert "couldn't find enough information" in NOT_FOUND_MESSAGE.lower()
