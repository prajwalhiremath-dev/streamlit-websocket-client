"""
Unit tests for streamlit-websocket-client
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_websocket_client import connect, WebSocketConnection


class TestWebSocketConnection:
    """Test WebSocketConnection class"""
    
    def test_connection_initialization(self):
        """Test connection object initialization"""
        conn = WebSocketConnection(
            state="CONNECTING",
            last_message=None,
            error=None,
            ready_state=0,
            _key="test"
        )
        
        assert conn.state == "CONNECTING"
        assert conn.last_message is None
        assert conn.error is None
        assert conn.ready_state == 0
        assert conn._key == "test"
    
    def test_is_open(self):
        """Test is_open method"""
        # Test open connection
        conn = WebSocketConnection(state="OPEN", ready_state=1)
        assert conn.is_open() is True
        
        # Test closed connection
        conn = WebSocketConnection(state="CLOSED", ready_state=3)
        assert conn.is_open() is False
        
        # Test connecting
        conn = WebSocketConnection(state="CONNECTING", ready_state=0)
        assert conn.is_open() is False
    
    def test_send_message(self):
        """Test send method"""
        conn = WebSocketConnection(_key="test")
        
        # Test string message
        conn.send("Hello")
        assert conn._send_queue == "Hello"
        
        # Test dict message
        test_dict = {"type": "test", "data": 123}
        conn.send(test_dict)
        assert conn._send_queue == json.dumps(test_dict)
        
        # Test list message
        test_list = [1, 2, 3]
        conn.send(test_list)
        assert conn._send_queue == json.dumps(test_list)
    
    def test_to_dict(self):
        """Test to_dict method"""
        conn = WebSocketConnection(
            state="OPEN",
            last_message="test message",
            error=None,
            ready_state=1,
            _key="test"
        )
        
        result = conn.to_dict()
        assert isinstance(result, dict)
        assert result['state'] == "OPEN"
        assert result['last_message'] == "test message"
        assert result['error'] is None
        assert result['ready_state'] == 1


class TestConnect:
    """Test connect function"""
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    @patch('streamlit.session_state', new_callable=dict)
    def test_connect_basic(self, mock_session_state, mock_component):
        """Test basic connection"""
        # Mock component return value
        mock_component.return_value = {
            "state": "OPEN",
            "last_message": "Hello",
            "error": None,
            "ready_state": 1
        }
        
        # Test connect
        conn = connect(
            url="wss://test.com",
            key="test_connection"
        )
        
        # Verify component was called with correct args
        mock_component.assert_called_once()
        call_args = mock_component.call_args[1]
        assert call_args['url'] == "wss://test.com"
        assert call_args['key'] == "test_connection"
        assert call_args['auto_reconnect'] is True
        
        # Verify connection object
        assert conn.state == "OPEN"
        assert conn.last_message == "Hello"
        assert conn.is_open() is True
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_connect_with_headers(self, mock_component):
        """Test connection with headers"""
        mock_component.return_value = None
        
        headers = {"Authorization": "Bearer token123"}
        conn = connect(
            url="wss://test.com",
            key="test",
            headers=headers
        )
        
        call_args = mock_component.call_args[1]
        assert call_args['headers'] == headers
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_connect_with_protocols(self, mock_component):
        """Test connection with protocols"""
        mock_component.return_value = None
        
        protocols = ["chat", "superchat"]
        conn = connect(
            url="wss://test.com",
            key="test",
            protocols=protocols
        )
        
        call_args = mock_component.call_args[1]
        assert call_args['protocols'] == protocols
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_connect_reconnect_settings(self, mock_component):
        """Test connection with reconnect settings"""
        mock_component.return_value = None
        
        conn = connect(
            url="wss://test.com",
            key="test",
            auto_reconnect=False,
            reconnect_interval=5000,
            max_reconnect_attempts=3
        )
        
        call_args = mock_component.call_args[1]
        assert call_args['auto_reconnect'] is False
        assert call_args['reconnect_interval'] == 5000
        assert call_args['max_reconnect_attempts'] == 3
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_connect_none_response(self, mock_component):
        """Test connection when component returns None"""
        mock_component.return_value = None
        
        conn = connect(
            url="wss://test.com",
            key="test"
        )
        
        assert conn.state == "CONNECTING"
        assert conn.last_message is None
        assert conn.error is None
        assert conn.ready_state == 0
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_connect_error_state(self, mock_component):
        """Test connection in error state"""
        mock_component.return_value = {
            "state": "ERROR",
            "last_message": None,
            "error": "Connection refused",
            "ready_state": 3
        }
        
        conn = connect(
            url="wss://test.com",
            key="test"
        )
        
        assert conn.state == "ERROR"
        assert conn.error == "Connection refused"
        assert conn.is_open() is False


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_invalid_url(self, mock_component):
        """Test handling of invalid URLs"""
        mock_component.return_value = {
            "state": "ERROR",
            "error": "Invalid URL",
            "last_message": None,
            "ready_state": 3
        }
        
        conn = connect(
            url="not-a-valid-url",
            key="test"
        )
        
        assert conn.state == "ERROR"
        assert "Invalid" in conn.error
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_large_message(self, mock_component):
        """Test handling of large messages"""
        large_message = {"data": "x" * 10000}  # 10KB message
        
        mock_component.return_value = {
            "state": "OPEN",
            "last_message": large_message,
            "error": None,
            "ready_state": 1
        }
        
        conn = connect(url="wss://test.com", key="test")
        assert conn.last_message == large_message
    
    def test_connection_send_unicode(self):
        """Test sending unicode messages"""
        conn = WebSocketConnection(_key="test")
        
        # Test unicode string
        unicode_msg = "Hello 世界 🌍"
        conn.send(unicode_msg)
        assert conn._send_queue == unicode_msg
        
        # Test unicode in dict
        unicode_dict = {"message": "Hello 世界", "emoji": "🚀"}
        conn.send(unicode_dict)
        assert json.loads(conn._send_queue) == unicode_dict
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_connection_timeout(self, mock_component):
        """Test connection timeout scenario"""
        mock_component.return_value = {
            "state": "ERROR",
            "last_message": None,
            "error": "Connection timeout",
            "ready_state": 3
        }
        
        conn = connect(
            url="wss://test.com",
            key="test"
        )
        
        assert conn.state == "ERROR"
        assert "timeout" in conn.error.lower()
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_rapid_reconnects(self, mock_component):
        """Test rapid reconnection attempts"""
        # Simulate multiple connection states
        states = [
            {"state": "CONNECTING", "ready_state": 0},
            {"state": "ERROR", "error": "Failed", "ready_state": 3},
            {"state": "CONNECTING", "ready_state": 0},
            {"state": "OPEN", "ready_state": 1}
        ]
        
        mock_component.side_effect = states
        
        # Multiple connection attempts
        for i in range(len(states)):
            conn = connect(url="wss://test.com", key=f"test_{i}")
            
        # Last connection should be open
        assert conn.state == "OPEN"


class TestIntegration:
    """Integration tests with Streamlit"""
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    @patch('streamlit.session_state', new_callable=dict)
    def test_session_state_persistence(self, mock_session_state, mock_component):
        """Test that connection persists in session state"""
        mock_component.return_value = {
            "state": "OPEN",
            "last_message": "test",
            "error": None,
            "ready_state": 1
        }
        
        # First connection
        conn1 = connect(url="wss://test.com", key="persist_test")
        
        # Verify stored in session state
        assert "_websocket_persist_test" in mock_session_state
        
        # Second call should reuse session state
        conn2 = connect(url="wss://test.com", key="persist_test")
        
        # Should be the same connection
        assert conn1._key == conn2._key
    
    @patch('streamlit_websocket_client.websocket_client._websocket_component')
    def test_multiple_connections(self, mock_component):
        """Test multiple simultaneous connections"""
        mock_component.return_value = {
            "state": "OPEN",
            "ready_state": 1
        }
        
        # Create multiple connections
        conn1 = connect(url="wss://server1.com", key="conn1")
        conn2 = connect(url="wss://server2.com", key="conn2")
        conn3 = connect(url="wss://server3.com", key="conn3")
        
        # All should be independent
        assert conn1._key == "conn1"
        assert conn2._key == "conn2"
        assert conn3._key == "conn3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])