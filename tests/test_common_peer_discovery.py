"""Tests for common PeerDiscovery for discovering peer agents.

RED phase: These tests should FAIL initially since common.peer_discovery doesn't exist yet.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.peer_discovery import PeerDiscovery


@pytest.fixture
def static_peers():
    """Sample static peers configuration."""
    return ["http://agent1:8000", "http://agent2:8000", "http://agent3:8000"]


@pytest.fixture
def green_peers_response():
    """Sample response from Green's /peers endpoint."""
    return {
        "peers": [
            "http://agent1:8000",
            "http://agent2:8000",
            "http://agent3:8000",
            "http://agent4:8000",
        ]
    }


class TestPeerDiscoveryInitialization:
    """Test PeerDiscovery initialization."""

    def test_peer_discovery_accepts_static_peers(self, static_peers):
        """PeerDiscovery initializes with static peers configuration."""
        discovery = PeerDiscovery(static_peers=static_peers)
        assert discovery is not None

    def test_peer_discovery_accepts_green_url(self):
        """PeerDiscovery initializes with Green registry URL."""
        discovery = PeerDiscovery(green_url="http://green:8000")
        assert discovery is not None

    def test_peer_discovery_accepts_both_sources(self, static_peers):
        """PeerDiscovery can use both static and Green registry sources."""
        discovery = PeerDiscovery(static_peers=static_peers, green_url="http://green:8000")
        assert discovery is not None

    def test_peer_discovery_has_default_ttl(self):
        """PeerDiscovery has default cache TTL."""
        discovery = PeerDiscovery(static_peers=["http://agent1:8000"])
        # Default TTL should be reasonable (e.g., 60 seconds)
        assert discovery._cache_ttl >= 10.0

    def test_peer_discovery_accepts_custom_ttl(self):
        """PeerDiscovery accepts custom cache TTL."""
        discovery = PeerDiscovery(static_peers=["http://agent1:8000"], cache_ttl=120.0)
        assert discovery._cache_ttl == 120.0


class TestPeerDiscoveryStaticPeers:
    """Test static peers functionality."""

    @pytest.mark.asyncio
    async def test_get_peers_returns_static_peers(self, static_peers):
        """get_peers returns static peers when configured."""
        discovery = PeerDiscovery(static_peers=static_peers)
        peers = await discovery.get_peers()
        assert peers == static_peers

    @pytest.mark.asyncio
    async def test_get_peers_returns_empty_when_no_peers(self):
        """get_peers returns empty list when no peers configured."""
        discovery = PeerDiscovery()
        peers = await discovery.get_peers()
        assert peers == []

    @pytest.mark.asyncio
    async def test_static_peers_are_cached(self, static_peers):
        """Static peers are cached (no repeated computation)."""
        discovery = PeerDiscovery(static_peers=static_peers)

        # First call
        peers1 = await discovery.get_peers()
        # Second call should use cached value
        peers2 = await discovery.get_peers()

        assert peers1 == peers2
        assert peers1 is peers2  # Same object reference


class TestPeerDiscoveryGreenRegistry:
    """Test Green registry lookup functionality."""

    @pytest.mark.asyncio
    async def test_get_peers_queries_green_registry(self, green_peers_response):
        """get_peers queries Green's /peers endpoint."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.json.return_value = green_peers_response
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(green_url="http://green:8000")
            peers = await discovery.get_peers()

            # Verify GET was called to /peers endpoint
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert call_args[0][0] == "http://green:8000/peers"
            assert peers == green_peers_response["peers"]

    @pytest.mark.asyncio
    async def test_green_registry_combines_with_static_peers(
        self, static_peers, green_peers_response
    ):
        """Combines static peers and Green registry peers."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.json.return_value = green_peers_response
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(static_peers=static_peers, green_url="http://green:8000")
            peers = await discovery.get_peers()

            # Should contain all peers from both sources (deduplicated)
            expected = list(set(static_peers + green_peers_response["peers"]))
            assert set(peers) == set(expected)


class TestPeerDiscoveryCaching:
    """Test peer list caching."""

    @pytest.mark.asyncio
    async def test_peers_are_cached_with_ttl(self, green_peers_response):
        """Peers are cached and reused within TTL."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.json.return_value = green_peers_response
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(green_url="http://green:8000", cache_ttl=60.0)

            # First call
            peers1 = await discovery.get_peers()
            # Second call should use cache (no new HTTP request)
            peers2 = await discovery.get_peers()

            # Only one HTTP request should be made
            assert mock_client.get.call_count == 1
            assert peers1 == peers2

    @pytest.mark.asyncio
    async def test_cache_expires_after_ttl(self, green_peers_response):
        """Cache expires after TTL and fetches fresh data."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.json.return_value = green_peers_response
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            # Very short TTL for testing
            discovery = PeerDiscovery(green_url="http://green:8000", cache_ttl=0.01)

            # First call
            await discovery.get_peers()
            # Wait for cache to expire
            import asyncio

            await asyncio.sleep(0.02)
            # Second call should fetch fresh data
            await discovery.get_peers()

            # Two HTTP requests should be made
            assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_manual_cache_invalidation(self, green_peers_response):
        """Cache can be manually invalidated."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.json.return_value = green_peers_response
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(green_url="http://green:8000", cache_ttl=60.0)

            # First call
            await discovery.get_peers()
            # Invalidate cache
            discovery.invalidate_cache()
            # Second call should fetch fresh data
            await discovery.get_peers()

            # Two HTTP requests should be made
            assert mock_client.get.call_count == 2


class TestPeerDiscoveryErrorHandling:
    """Test graceful error handling."""

    @pytest.mark.asyncio
    async def test_handles_green_unavailable(self):
        """Graceful handling of Green unavailability."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            # Simulate connection error
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(green_url="http://green:8000")

            # Should return empty list when Green unavailable
            peers = await discovery.get_peers()
            assert peers == []

    @pytest.mark.asyncio
    async def test_handles_timeout(self):
        """Graceful handling of timeout."""
        import httpx

        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            # Simulate timeout
            mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(green_url="http://green:8000", timeout=5.0)

            # Should return empty list on timeout
            peers = await discovery.get_peers()
            assert peers == []

    @pytest.mark.asyncio
    async def test_handles_invalid_json_response(self):
        """Graceful handling of invalid JSON response."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            # Invalid JSON response (missing "peers" key)
            mock_response.json.return_value = {"data": []}
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(green_url="http://green:8000")

            # Should return empty list on invalid response
            peers = await discovery.get_peers()
            assert peers == []

    @pytest.mark.asyncio
    async def test_handles_http_error(self):
        """Graceful handling of HTTP errors (4xx, 5xx)."""
        import httpx

        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            # Simulate HTTP error response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.get = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Server error", request=MagicMock(), response=mock_response
                )
            )
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(green_url="http://green:8000")

            # Should return empty list on HTTP error
            peers = await discovery.get_peers()
            assert peers == []

    @pytest.mark.asyncio
    async def test_fallback_to_static_when_green_fails(self, static_peers):
        """Falls back to static peers when Green registry fails."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(static_peers=static_peers, green_url="http://green:8000")

            # Should return static peers when Green fails
            peers = await discovery.get_peers()
            assert set(peers) == set(static_peers)


class TestPeerDiscoveryEdgeCases:
    """Test edge cases."""

    @pytest.mark.asyncio
    async def test_deduplicates_peers(self):
        """Removes duplicate peers from combined sources."""
        with patch("common.peer_discovery.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            # Green returns same peers as static
            mock_response.json.return_value = {
                "peers": ["http://agent1:8000", "http://agent2:8000"]
            }
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            discovery = PeerDiscovery(
                static_peers=["http://agent1:8000", "http://agent2:8000"],
                green_url="http://green:8000",
            )

            peers = await discovery.get_peers()

            # Should have no duplicates
            assert len(peers) == len(set(peers))
            assert len(peers) == 2

    @pytest.mark.asyncio
    async def test_preserves_order_when_no_duplicates(self):
        """Preserves original order when no duplicates."""
        discovery = PeerDiscovery(
            static_peers=[
                "http://agent1:8000",
                "http://agent2:8000",
                "http://agent3:8000",
            ]
        )

        peers = await discovery.get_peers()

        # Order should be preserved
        assert peers == [
            "http://agent1:8000",
            "http://agent2:8000",
            "http://agent3:8000",
        ]
