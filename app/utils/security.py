import ipaddress
from typing import Optional
from urllib.parse import urlparse


class UnsafeURLError(ValueError):
    pass


def validate_outbound_url(
    url: str,
    *,
    allowed_hosts: Optional[list[str]] = None,
    allowed_schemes: tuple[str, ...] = ("http", "https"),
) -> str:
    parsed = urlparse(url or "")
    host = (parsed.hostname or "").strip().lower().rstrip(".")

    if parsed.scheme.lower() not in allowed_schemes:
        raise UnsafeURLError("Only http/https URLs are allowed.")

    if not host:
        raise UnsafeURLError("A valid hostname is required.")

    try:
        ip_address = ipaddress.ip_address(host)
    except ValueError:
        ip_address = None

    if ip_address and (
        ip_address.is_private
        or ip_address.is_loopback
        or ip_address.is_link_local
        or ip_address.is_multicast
        or ip_address.is_reserved
    ):
        raise UnsafeURLError("Private or local network addresses are blocked.")

    if host in {"localhost"} or host.endswith(".local") or host.endswith(".internal"):
        raise UnsafeURLError("Local hostnames are blocked.")

    if allowed_hosts:
        normalized_hosts = [item.lower().strip().rstrip(".") for item in allowed_hosts if item]
        if not any(host == item or host.endswith(f".{item}") for item in normalized_hosts):
            raise UnsafeURLError("This host is not on the allowlist.")

    return parsed.geturl()
