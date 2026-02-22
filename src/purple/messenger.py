"""Messenger for A2A agent-to-agent communication.

Implements A2A SDK communication for Purple Agent test fixture.

This module re-exports from common.messenger for backward compatibility.
"""

from common.messenger import Messenger

__all__ = ["Messenger"]
