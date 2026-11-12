from collections.abc import Mapping


def authenticate(username: str, password: str, credentials: Mapping[str, str]) -> bool:
    """Return whether username and password match the supplied credentials."""
    return username in credentials and credentials[username] == password
