"""
Streamlit WebSocket Client Library
A bidirectional component for real-time WebSocket communication in Streamlit apps.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any, Union, List
import json
from dataclasses import dataclass, asdict
import os
from pathlib import Path
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Development vs Production mode
_DEVELOP_MODE = os.getenv("STREAMLIT_WEBSOCKET_DEVELOP", "").lower() == "true"

if _DEVELOP_MODE:
    # Development: Point to localhost where npm dev server runs
    _websocket_component = components.declare_component(
        "streamlit_websocket_client",
        url="http://localhost:3001",
    )
else:
    # Production: Use built frontend files
    parent_dir = Path(__file__).parent
    build_dir = parent_dir / "frontend" / "build"
    _websocket_component = components.declare_component(
        "streamlit_websocket_client",
        path=str(build_dir)
    )


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection with its current state and data."""
    
    state: str = "CONNECTING"  # CONNECTING, OPEN, CLOSED, ERROR
    last_message: Optional[Any] = None
    error: Optional[str] = None
    ready_state: int = 0  # 0=CONNECTING, 1=OPEN, 2=CLOSING, 3=CLOSED
    _key: str = ""
    _send_queue: Optional[Any] = None
    
    def send(self, message: Union[str, dict, list]) -> None:
        """Send a message through the WebSocket connection."""
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        
        # This will be picked up by the frontend component
        self._send_queue = message
    
    def is_open(self) -> bool:
        """Check if the connection is open and ready."""
        return self.state == "OPEN" and self.ready_state == 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert connection state to dictionary."""
        return asdict(self)


def connect(
    url: str,
    key: str,
    headers: Optional[Dict[str, str]] = None,
    protocols: Optional[List[str]] = None,
    auto_reconnect: bool = True,
    reconnect_interval: int = 3000,
    max_reconnect_attempts: int = 5,
    default: Optional[Any] = None,
    height: int = 0
) -> WebSocketConnection:
    """
    Create a WebSocket client connection to the specified URL.
    
    Args:
        url: WebSocket server URL (e.g., "wss://example.com/ws")
        key: Unique key for this component instance
        headers: Optional HTTP headers for authentication
        protocols: Optional list of WebSocket subprotocols
        auto_reconnect: Whether to automatically reconnect on disconnect
        reconnect_interval: Time in ms between reconnection attempts
        max_reconnect_attempts: Maximum number of reconnection attempts
        default: Default value to return if no connection data exists
        height: Component height (0 for invisible component)
    
    Returns:
        WebSocketConnection object with current state and last message
    """
    
    # Validate URL
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    if not url.startswith(('ws://', 'wss://')):
        raise ValueError("URL must start with ws:// or wss://")
    
    # Validate key
    if not key or not isinstance(key, str):
        raise ValueError("Key must be a non-empty string")
    
    # Get the current connection state from session state if it exists
    session_key = f"_websocket_{key}"
    send_key = f"{session_key}_send"
    
    # Check if we need to send a message
    send_message = None
    if send_key in st.session_state:
        send_message = st.session_state[send_key]
        # Clear the send queue after reading
        del st.session_state[send_key]
    
    try:
        # Call the frontend component
        component_value = _websocket_component(
            url=url,
            key=key,
            headers=headers or {},
            protocols=protocols or [],
            auto_reconnect=auto_reconnect,
            reconnect_interval=reconnect_interval,
            max_reconnect_attempts=max_reconnect_attempts,
            send_message=send_message,
            default=default,
            height=height
        )
    except Exception as e:
        logger.error(f"Error creating WebSocket component: {e}")
        return WebSocketConnection(
            state="ERROR",
            last_message=None,
            error=str(e),
            ready_state=3,
            _key=key
        )
    
    # Parse the component value
    if component_value is None:
        return WebSocketConnection(
            state="CONNECTING",
            last_message=None,
            error=None,
            ready_state=0,
            _key=key
        )
    
    # Create connection object from component data
    conn = WebSocketConnection(
        state=component_value.get("state", "CONNECTING"),
        last_message=component_value.get("last_message"),
        error=component_value.get("error"),
        ready_state=component_value.get("ready_state", 0),
        _key=key
    )
    
    # Store connection in session state for persistence
    st.session_state[session_key] = conn
    
    # Handle outgoing messages
    if hasattr(conn, '_send_queue') and conn._send_queue:
        st.session_state[send_key] = conn._send_queue
        # Force a rerun to send the message
        st.rerun()
    
    return conn


# For backward compatibility and convenience
import streamlit as st

__all__ = ["connect", "WebSocketConnection"]