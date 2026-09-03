"""URL Value Object.

Validates and normalizes URLs for consistent storage and comparison.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse


@dataclass(frozen=True, slots=True)
class URL:
    """Immutable value object representing a validated and normalized URL."""

    value: str

    def __post_init__(self) -> None:
        """Validate and normalize URL after initialization."""
        if not self.value:
            raise ValueError("URL cannot be empty")

        normalized = self._normalize(self.value)
        if not self._is_valid(normalized):
            raise ValueError(f"Invalid URL: {self.value}")

        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(url: str) -> str:
        """Normalize URL by removing fragments, default ports, etc."""
        parsed = urlparse(url.strip())

        # Remove fragment
        parsed = parsed._replace(fragment="")

        # Remove default ports
        if parsed.port == 80 and parsed.scheme == "http":
            netloc = parsed.hostname or ""
        elif parsed.port == 443 and parsed.scheme == "https":
            netloc = parsed.hostname or ""
        else:
            netloc = parsed.netloc

        # Lowercase scheme and netloc
        parsed = parsed._replace(
            scheme=parsed.scheme.lower(), netloc=netloc.lower()
        )

        # Remove trailing slash from path if it's just "/"
        path = parsed.path
        if path == "/":
            path = ""

        parsed = parsed._replace(path=path)

        return urlunparse(parsed)

    @staticmethod
    def _is_valid(url: str) -> bool:
        """Check if URL is valid."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme in ("http", "https") and parsed.netloc)
        except Exception:
            return False

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, URL):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        return urlparse(self.value).netloc

    @property
    def scheme(self) -> str:
        """Extract scheme from URL."""
        return urlparse(self.value).scheme

    @property
    def path(self) -> str:
        """Extract path from URL."""
        return urlparse(self.value).path

    @property
    def query(self) -> str:
        """Extract query string from URL."""
        return urlparse(self.value).query

    @classmethod
    def from_string(cls, url: str) -> URL:
        """Create URL from string (factory method)."""
        return cls(url)

    def clean_for_dedup(self) -> str:
        """Return URL normalized for deduplication comparison.

        Removes query parameters that don't affect content (utm_*, fbclid, etc.)
        """
        parsed = urlparse(self.value)

        # Filter out tracking parameters
        tracking_params = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "ref",
            "source",
            "campaign_id",
        }

        if parsed.query:
            params = []
            for param in parsed.query.split("&"):
                key = param.split("=")[0] if "=" in param else param
                if key not in tracking_params:
                    params.append(param)
            query = "&".join(params)
        else:
            query = ""

        parsed = parsed._replace(query=query, fragment="")
        return urlunparse(parsed)
