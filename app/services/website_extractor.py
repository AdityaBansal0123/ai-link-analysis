import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
from dataclasses import dataclass, field

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.utils.validators import (
    validate_and_sanitize_url,
    WebsiteInaccessibleError,
    WebsiteTimeoutError,
    SSRFSecurityError,
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractedWebsiteContent:
    url: str
    final_url: str
    status_code: int
    title: str
    meta_description: str
    meta_keywords: List[str]
    og_tags: Dict[str, str] = field(default_factory=dict)
    headings: Dict[str, List[str]] = field(default_factory=dict)
    cleaned_text: str = ""
    detected_brand_name: str = ""
    navigation_links: List[str] = field(default_factory=list)
    char_count: int = 0


class WebsiteExtractor:
    """
    Safely fetches and parses website content with SSRF defenses,
    content sanitization, and structured metadata extraction.
    """

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36 "
            "(compatible; DxoraLinkAnalysisBot/1.0; +https://dxora.com)"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    async def fetch_html(self, url: str) -> httpx.Response:
        """
        Executes an asynchronous HTTP GET request while defending against SSRF
        and redirect re-targeting attacks.
        """
        sanitized_url, _ = validate_and_sanitize_url(url)
        current_url = sanitized_url
        redirect_count = 0

        timeout = httpx.Timeout(settings.REQUEST_TIMEOUT_SECONDS, connect=8.0)

        async with httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=timeout,
            follow_redirects=False,
            verify=False  # Allow sites with minor SSL chain quirks to be analyzed gracefully
        ) as client:
            while redirect_count <= settings.MAX_REDIRECTS:
                try:
                    response = await client.get(current_url)
                except httpx.TimeoutException as e:
                    logger.warning(f"Timeout fetching {current_url}: {e}")
                    raise WebsiteTimeoutError(f"Request to '{current_url}' timed out after {settings.REQUEST_TIMEOUT_SECONDS}s.")
                except httpx.RequestError as e:
                    logger.warning(f"Request error fetching {current_url}: {e}")
                    raise WebsiteInaccessibleError(f"Unable to connect to website: {str(e)}")

                # Check for redirects
                if response.is_redirect:
                    redirect_count += 1
                    location = response.headers.get("location")
                    if not location:
                        break
                    
                    # Resolve relative redirect URLs
                    next_url = str(response.url.join(location))
                    
                    # Strictly validate every redirected hop for SSRF
                    validated_redirect_url, _ = validate_and_sanitize_url(next_url)
                    current_url = validated_redirect_url
                    continue

                if response.status_code >= 400:
                    raise WebsiteInaccessibleError(
                        f"Website returned HTTP error {response.status_code} ({response.reason_phrase})."
                    )

                return response

            raise WebsiteInaccessibleError(f"Exceeded maximum redirect count ({settings.MAX_REDIRECTS}).")

    def parse_html(self, url: str, html_text: str, status_code: int = 200) -> ExtractedWebsiteContent:
        """
        Extracts structural elements, metadata, and clean contextual text from raw HTML.
        """
        soup = BeautifulSoup(html_text, "lxml" if "lxml" in BeautifulSoup.__dict__ else "html.parser")

        # 1. Extract OpenGraph & Meta Tags
        og_tags: Dict[str, str] = {}
        meta_description = ""
        meta_keywords: List[str] = []

        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            prop = meta.get("property", "").lower()
            content = meta.get("content", "").strip()

            if not content:
                continue

            if prop.startswith("og:"):
                og_tags[prop] = content
            elif name == "description" and not meta_description:
                meta_description = content
            elif prop == "og:description" and not meta_description:
                meta_description = content
            elif name == "keywords":
                meta_keywords = [k.strip() for k in content.split(",") if k.strip()]

        # 2. Extract Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif og_tags.get("og:title"):
            title = og_tags["og:title"].strip()

        # 3. Detect Brand Name
        detected_brand = self._infer_brand_name(url, title, og_tags)

        # 4. Extract Headings
        headings: Dict[str, List[str]] = {
            "h1": [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)],
            "h2": [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)][:12],
            "h3": [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)][:12],
        }

        # 5. Extract Navigation Links
        nav_links: List[str] = []
        for nav in soup.find_all(["nav", "header"]):
            for a in nav.find_all("a", href=True):
                anchor_text = a.get_text(strip=True)
                if anchor_text and len(anchor_text) < 40 and anchor_text not in nav_links:
                    nav_links.append(anchor_text)
                if len(nav_links) >= 15:
                    break

        # 6. Sanitize Body Text
        # Remove noisy tags
        for element in soup(["script", "style", "noscript", "svg", "iframe", "canvas", "head", "template"]):
            element.decompose()

        raw_text = soup.get_text(separator=" ", strip=True)
        # Normalize excessive whitespace
        cleaned_text = re.sub(r"\s+", " ", raw_text)

        # Truncate content to token-efficient length while preserving core information
        if len(cleaned_text) > settings.MAX_CONTENT_LENGTH:
            cleaned_text = cleaned_text[: settings.MAX_CONTENT_LENGTH] + "... [truncated for length]"

        return ExtractedWebsiteContent(
            url=url,
            final_url=url,
            status_code=status_code,
            title=title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            og_tags=og_tags,
            headings=headings,
            cleaned_text=cleaned_text,
            detected_brand_name=detected_brand,
            navigation_links=nav_links,
            char_count=len(cleaned_text)
        )

    def _infer_brand_name(self, url: str, title: str, og_tags: Dict[str, str]) -> str:
        """Infers candidate brand name from OpenGraph, title separators, or domain."""
        if og_tags.get("og:site_name"):
            return og_tags["og:site_name"].strip()

        if title:
            # Common title formats: "Product Name | Brand", "Brand - Tagline"
            parts = re.split(r"\s*[|\-–—•:]+\s*", title)
            if len(parts) > 1:
                # Often the first or last component is the brand
                first = parts[0].strip()
                last = parts[-1].strip()
                if 2 <= len(last) <= 30 and not any(skip in last.lower() for skip in ["home", "official", "welcome"]):
                    return last
                if 2 <= len(first) <= 30:
                    return first

        # Fallback to domain name
        parsed = urlparse(url)
        netloc = parsed.netloc.split(":")[0]
        # Remove www.
        if netloc.startswith("www."):
            netloc = netloc[4:]
        domain_parts = netloc.split(".")
        if domain_parts:
            return domain_parts[0].capitalize()

        return "Brand"

    async def extract(self, url: str) -> ExtractedWebsiteContent:
        """Top-level pipeline method: validates, fetches, and parses the target website."""
        response = await self.fetch_html(url)
        content = self.parse_html(url, response.text, response.status_code)
        content.final_url = str(response.url)
        return content
