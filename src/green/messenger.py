"""Messenger for A2A agent-to-agent communication.

Implements real agent communication using A2A SDK for authentic coordination measurement.

This module re-exports from common.messenger for backward compatibility.
"""

from common.messenger import Messenger

__all__ = ["Messenger"]
