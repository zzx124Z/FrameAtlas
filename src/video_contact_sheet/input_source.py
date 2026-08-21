import ipaddress
from pathlib import Path
from urllib.parse import urlparse

SUPPORTED_PUBLIC_HOSTS = ("bilibili.com", "youtube.com", "youtu.be")


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_public_url(value: str) -> bool:
    if not is_url(value):
        return False
    host = urlparse(value).hostname
    if not host or host.lower() == "localhost":
        return False
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        return True


def is_supported_public_url(value: str) -> bool:
    if not is_public_url(value):
        return False
    host = urlparse(value).hostname
    if not host:
        return False
    normalized_host = host.lower().rstrip(".")
    return any(normalized_host == allowed or normalized_host.endswith(f".{allowed}") for allowed in SUPPORTED_PUBLIC_HOSTS)


def resolve_local_input(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"local video does not exist: {path}")
    return path.resolve()
