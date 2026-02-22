"""TraceReporter for async fire-and-forget trace reporting.

Sends trace data from Purple agents to Green agent's /traces endpoint.
Uses fire-and-forget pattern for non-blocking trace collection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
from loguru import logger

if TYPE_CHECKING:
    from common.models import InteractionStep


class TraceReporter:
    """Async trace reporter for sending traces to Green agent."""

    def __init__(self, green_url: str, timeout: float = 5.0) -> None:
        """Initialize TraceReporter.

        Args:
            green_url: Base URL of Green agent (e.g., "http://green:8000")
            timeout: HTTP request timeout in seconds (default: 5.0)
        """
        self.green_url = green_url
        self._timeout = timeout

    async def send_traces(self, traces: list[InteractionStep]) -> None:
        """Send traces to Green agent's /traces endpoint.

        Fire-and-forget pattern: sends traces asynchronously without blocking.
        Gracefully handles errors (Green unavailability, timeouts, HTTP errors).

        Args:
            traces: List of InteractionStep traces to send
        """
        try:
            # Serialize traces to JSON-compatible format
            traces_data = [
                {
                    "step_id": trace.step_id,
                    "trace_id": trace.trace_id,
                    "call_type": trace.call_type.value,
                    "start_time": trace.start_time.isoformat(),
                    "end_time": trace.end_time.isoformat(),
                    "latency": trace.latency,
                    "error": trace.error,
                    "parent_step_id": trace.parent_step_id,
                }
                for trace in traces
            ]

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                await client.post(
                    f"{self.green_url}/traces",
                    json={"traces": traces_data},
                )
                logger.debug(f"Sent {len(traces)} traces to {self.green_url}/traces")

        except httpx.TimeoutException:
            logger.warning(f"Timeout sending traces to {self.green_url}/traces")
        except httpx.HTTPStatusError as e:
            logger.warning(
                f"HTTP error {e.response.status_code} sending traces to {self.green_url}/traces"
            )
        except Exception as e:
            logger.warning(f"Error sending traces to {self.green_url}/traces: {e}")
