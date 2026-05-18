from core.anonymizer import generate_pseudonym, anonymize_email

def test_pseudonym_deterministic():
    id1 = generate_pseudonym("user_1")
    id2 = generate_pseudonym("user_1")
    assert id1 == id2

def test_email_redaction():
    res = anonymize_email("john.doe@example.com")
    assert "@example.com" in res
    assert "john" not in res