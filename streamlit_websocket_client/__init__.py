"""
Streamlit WebSocket Client
A Streamlit component for real-time WebSocket communication
"""

from .websocket_client import connect, WebSocketConnection

__version__ = "0.1.0"
__all__ = ["connect", "WebSocketConnection"]