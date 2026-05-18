from backend.validators import validation_service


def test_grounding_detects_overlap():
    context = ["Returns are accepted within 14 days of delivery for unused items."]
    answer = "You can return unused items within 14 days of delivery."
    assert validation_service.check_grounding(answer, context)


def test_safety_blocks_forbidden_terms():
    assert not validation_service.check_safety("Please send your password via email.")
