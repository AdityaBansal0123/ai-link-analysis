import pytest
from app.utils.validators import (
    validate_and_sanitize_url,
    InvalidURLError,
    SSRFSecurityError,
    is_ip_forbidden,
)


def test_valid_urls():
    clean_url, resolved_ip = validate_and_sanitize_url("https://example.com")
    assert clean_url == "https://example.com"
    assert resolved_ip != ""

    # Test auto-prepending https
    clean_url2, _ = validate_and_sanitize_url("example.org")
    assert clean_url2 == "https://example.org"


def test_invalid_scheme():
    with pytest.raises(InvalidURLError):
        validate_and_sanitize_url("ftp://example.com/file.txt")

    with pytest.raises(InvalidURLError):
        validate_and_sanitize_url("file:///etc/passwd")


def test_invalid_urls():
    with pytest.raises(InvalidURLError):
        validate_and_sanitize_url("")

    with pytest.raises(InvalidURLError):
        validate_and_sanitize_url("   ")

    with pytest.raises(InvalidURLError):
        validate_and_sanitize_url("https://")


def test_ssrf_forbidden_ips():
    assert is_ip_forbidden("127.0.0.1") is True
    assert is_ip_forbidden("127.0.0.2") is True
    assert is_ip_forbidden("10.0.0.1") is True
    assert is_ip_forbidden("192.168.1.1") is True
    assert is_ip_forbidden("172.16.0.1") is True
    assert is_ip_forbidden("169.254.169.254") is True
    assert is_ip_forbidden("0.0.0.0") is True
    assert is_ip_forbidden("::1") is True

    # Public IP should not be forbidden
    assert is_ip_forbidden("8.8.8.8") is False
    assert is_ip_forbidden("93.184.216.34") is False


def test_ssrf_forbidden_hostnames():
    with pytest.raises(SSRFSecurityError):
        validate_and_sanitize_url("http://localhost:4000")

    with pytest.raises(SSRFSecurityError):
        validate_and_sanitize_url("http://127.0.0.1:8000")

    with pytest.raises(SSRFSecurityError):
        validate_and_sanitize_url("http://169.254.169.254/latest/meta-data/")

    with pytest.raises(SSRFSecurityError):
        validate_and_sanitize_url("http://10.0.1.5:8080")

    with pytest.raises(SSRFSecurityError):
        validate_and_sanitize_url("http://metadata.google.internal")
