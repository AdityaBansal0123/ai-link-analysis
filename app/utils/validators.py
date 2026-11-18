import ipaddress
import re
import socket
from urllib.parse import urlparse
from typing import List, Tuple


class LinkAnalysisException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str = "ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class InvalidURLError(LinkAnalysisException):
    """Raised when the URL is invalid or malformed."""
    def __init__(self, message: str = "Invalid URL provided. Please provide a valid HTTP or HTTPS URL."):
        super().__init__(message=message, code="INVALID_URL", status_code=400)


class SSRFSecurityError(LinkAnalysisException):
    """Raised when the URL resolves to a forbidden or private network destination (SSRF protection)."""
    def __init__(self, message: str = "Access to internal, loopback, or private network addresses is forbidden."):
        super().__init__(message=message, code="SSRF_FORBIDDEN", status_code=403)


class WebsiteInaccessibleError(LinkAnalysisException):
    """Raised when the website cannot be reached or returned an error status."""
    def __init__(self, message: str = "Website is inaccessible or returned an error."):
        super().__init__(message=message, code="WEBSITE_INACCESSIBLE", status_code=502)


class WebsiteTimeoutError(LinkAnalysisException):
    """Raised when connecting or reading from the website times out."""
    def __init__(self, message: str = "Website request timed out."):
        super().__init__(message=message, code="WEBSITE_TIMEOUT", status_code=504)


class LLMServiceError(LinkAnalysisException):
    """Raised when LLM processing fails."""
    def __init__(self, message: str = "Failed to process content with LLM."):
        super().__init__(message=message, code="LLM_PROCESSING_ERROR", status_code=500)


# Forbidden hostnames and prefixes
FORBIDDEN_HOST_PATTERNS = [
    re.compile(r"^localhost$", re.IGNORECASE),
    re.compile(r".*\.localhost$", re.IGNORECASE),
    re.compile(r".*\.local$", re.IGNORECASE),
    re.compile(r".*\.internal$", re.IGNORECASE),
    re.compile(r".*\.lan$", re.IGNORECASE),
    re.compile(r"^metadata\.google\.internal$", re.IGNORECASE),
    re.compile(r"^instance-data$", re.IGNORECASE),
]

# Additional metadata IP addresses to block
METADATA_IPS = {
    "169.254.169.254",  # AWS, GCP, Azure, OpenStack metadata service
    "169.254.170.2",    # AWS ECS task metadata
    "fd00:ec2::254",    # AWS IPv6 metadata
}


def is_ip_forbidden(ip_str: str) -> bool:
    """Checks whether an IP address is private, loopback, link-local, multicast, or metadata."""
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip_str in METADATA_IPS:
            return True
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
            return True
        return False
    except ValueError:
        return True


def validate_and_sanitize_url(url: str) -> Tuple[str, str]:
    """
    Validates URL syntax and performs strict SSRF checks against DNS resolution.
    Returns:
        Tuple of (clean_url, resolved_ip)
    Raises:
        InvalidURLError: If URL is malformed or lacks valid scheme/host
        SSRFSecurityError: If host points to internal, loopback, or cloud metadata address
    """
    if not url or not isinstance(url, str):
        raise InvalidURLError("URL must be a non-empty string.")

    url = url.strip()

    # Prepend https:// if user passed a bare domain e.g. "example.com"
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = f"https://{url}"

    parsed = urlparse(url)

    # Check scheme
    if parsed.scheme.lower() not in ("http", "https"):
        raise InvalidURLError(f"Unsupported URL scheme '{parsed.scheme}'. Only 'http' and 'https' are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise InvalidURLError("URL does not contain a valid hostname.")

    # Check against forbidden host pattern list
    for pattern in FORBIDDEN_HOST_PATTERNS:
        if pattern.match(hostname):
            raise SSRFSecurityError(f"Requests to '{hostname}' are blocked for security (SSRF prevention).")

    # If hostname is already a direct IP address
    try:
        ip = ipaddress.ip_address(hostname)
        if is_ip_forbidden(str(ip)):
            raise SSRFSecurityError(f"Target IP address '{hostname}' is in a private or restricted network range.")
        return url, str(ip)
    except ValueError:
        # Not a raw IP, proceed to DNS resolution
        pass

    # Resolve hostname via DNS and check all returned IP addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise InvalidURLError(f"Could not resolve domain '{hostname}': {str(e)}")

    if not addr_info:
        raise InvalidURLError(f"No IP addresses found for domain '{hostname}'.")

    resolved_ips: List[str] = []
    for info in addr_info:
        ip_addr = info[4][0]
        resolved_ips.append(ip_addr)
        if is_ip_forbidden(ip_addr):
            raise SSRFSecurityError(
                f"Domain '{hostname}' resolved to a restricted IP address '{ip_addr}'. Request blocked for SSRF prevention."
            )

    return url, resolved_ips[0]
