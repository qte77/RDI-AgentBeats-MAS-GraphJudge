"""PeerDiscovery for discovering peer agents via static config and Green registry.

Discovers peer agents from two sources:
1. Static configuration (provided at initialization)
2. Green registry lookup via /peers endpoint

Implements caching with configurable TTL for efficient peer discovery.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import httpx
from loguru import logger

if TYPE_CHECKING:
    pass


class PeerDiscovery:
    """Peer discovery for finding agent peers via static config and Green registry."""

    def __init__(
        self,
        static_peers: list[str] | None = None,
        green_url: str | None = None,
        cache_ttl: float = 60.0,
        timeout: float = 5.0,
    ) -> None:
        """Initialize PeerDiscovery.

        Args:
            static_peers: List of static peer URLs (e.g., ["http://agent1:8000"])
            green_url: Base URL of Green agent for registry lookup (e.g., "http://green:8000")
            cache_ttl: Cache time-to-live in seconds (default: 60.0)
            timeout: HTTP request timeout in seconds (default: 5.0)
        """
        self._static_peers = static_peers or []
        self._green_url = green_url
        self._cache_ttl = cache_ttl
        self._timeout = timeout

        # Cache state
        self._cached_peers: list[str] | None = None
        self._cache_timestamp: float | None = None

    async def get_peers(self) -> list[str]:
        """Get list of peer agent URLs.

        Combines static peers and Green registry peers, with caching.
        Returns empty list if no peers are available or on error.

        Returns:
            List of peer agent URLs
        """
        # Check cache validity
        if self._is_cache_valid():
            return self._cached_peers or []

        # Collect peers from all sources
        peers: list[str] = []

        # Add static peers
        peers.extend(self._static_peers)

        # Query Green registry if configured
        if self._green_url:
            green_peers = await self._fetch_green_peers()
            if green_peers:  # Only extend if we got results
                peers.extend(green_peers)

        # Deduplicate while preserving order
        unique_peers = list(dict.fromkeys(peers))

        # Update cache
        self._cached_peers = unique_peers
        self._cache_timestamp = time.time()

        return unique_peers

    def invalidate_cache(self) -> None:
        """Manually invalidate the peer cache.

        Forces next get_peers() call to fetch fresh data.
        """
        self._cached_peers = None
        self._cache_timestamp = None

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid.

        Returns:
            True if cache is valid and can be used
        """
        if self._cached_peers is None or self._cache_timestamp is None:
            return False

        age = time.time() - self._cache_timestamp
        return age < self._cache_ttl

    async def _fetch_green_peers(self) -> list[str]:
        """Fetch peers from Green registry.

        Returns:
            List of peer URLs from Green registry, or empty list on error
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self._green_url}/peers")
                response.raise_for_status()
                data = response.json()

            # Extract peers from response (outside async context)
            if isinstance(data, dict) and "peers" in data:
                peers = data["peers"]
                if isinstance(peers, list):
                    return peers

            logger.warning(f"Invalid response format from {self._green_url}/peers: {data}")
            return []

        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching peers from {self._green_url}/peers")
            return []
        except httpx.HTTPStatusError as e:
            logger.warning(
                f"HTTP error {e.response.status_code} fetching peers from {self._green_url}/peers"
            )
            return []
        except Exception as e:
            logger.warning(f"Error fetching peers from {self._green_url}/peers: {e}")
            return []
