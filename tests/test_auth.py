from src.auth import authenticate


def test_authenticate_accepts_matching_credentials():
    assert authenticate("alice", "secret", {"alice": "secret"}) is True


def test_authenticate_rejects_unknown_user_or_wrong_password():
    credentials = {"alice": "secret"}
    assert authenticate("bob", "secret", credentials) is False
    assert authenticate("alice", "wrong", credentials) is False
