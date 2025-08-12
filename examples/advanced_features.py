"""
Advanced WebSocket Features Example
Demonstrates error handling, reconnection, multiple connections, and authentication
"""

import streamlit as st
import streamlit_websocket_client as swc
import json
from datetime import datetime
import time

st.set_page_config(
    page_title="Advanced WebSocket Features",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Advanced WebSocket Features")

# Tabs for different examples
tab1, tab2, tab3, tab4 = st.tabs([
    "Error Handling", 
    "Multiple Connections", 
    "Authentication", 
    "Performance Testing"
])

# Tab 1: Error Handling
with tab1:
    st.header("Error Handling & Reconnection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Connection Settings")
        
        # URLs for testing different scenarios
        test_scenario = st.selectbox(
            "Test Scenario",
            [
                "Valid Echo Server",
                "Invalid URL",
                "Non-existent Server",
                "Malformed URL"
            ]
        )
        
        url_map = {
            "Valid Echo Server": "wss://ws.postman-echo.com/raw",
            "Invalid URL": "wss://this-server-does-not-exist-12345.com/ws",
            "Non-existent Server": "ws://localhost:9999",
            "Malformed URL": "not-a-websocket-url"
        }
        
        test_url = url_map[test_scenario]
        
        # Reconnection settings
        auto_reconnect = st.checkbox("Enable Auto-Reconnect", value=True)
        max_attempts = st.slider("Max Reconnect Attempts", 1, 10, 5)
        reconnect_interval = st.slider("Reconnect Interval (seconds)", 1, 10, 3)
    
    with col2:
        st.subheader("Connection Test")
        
        # Test connection with error handling
        try:
            conn = swc.connect(
                url=test_url,
                key="error_test",
                auto_reconnect=auto_reconnect,
                max_reconnect_attempts=max_attempts,
                reconnect_interval=reconnect_interval * 1000
            )
            
            # Display status
            status_color = {
                "CONNECTING": "🟡",
                "OPEN": "🟢",
                "CLOSED": "🔴",
                "ERROR": "🔴"
            }
            
            st.markdown(f"### {status_color.get(conn.state, '⚪')} Status: {conn.state}")
            
            if conn.error:
                st.error(f"Error Details: {conn.error}")
            
            # Connection details
            st.json({
                "URL": test_url,
                "State": conn.state,
                "Ready State": conn.ready_state,
                "Error": conn.error,
                "Auto Reconnect": auto_reconnect,
                "Max Attempts": max_attempts
            })
            
            # Test sending message
            if conn.is_open():
                if st.button("Send Test Message"):
                    conn.send({"type": "test", "timestamp": datetime.now().isoformat()})
                    st.success("Message sent!")
                
                if conn.last_message:
                    st.info(f"Received: {conn.last_message}")
            
        except Exception as e:
            st.error(f"Component Error: {str(e)}")
            st.exception(e)

# Tab 2: Multiple Connections
with tab2:
    st.header("Multiple Simultaneous Connections")
    
    st.info("This example shows how to manage multiple WebSocket connections simultaneously.")
    
    # Connection configuration
    num_connections = st.slider("Number of Connections", 1, 5, 3)
    
    # Create multiple connections
    cols = st.columns(num_connections)
    
    for i in range(num_connections):
        with cols[i]:
            st.subheader(f"Connection {i+1}")
            
            # Each connection can have different settings
            url = st.text_input(
                f"URL {i+1}",
                value="wss://ws.postman-echo.com/raw",
                key=f"url_{i}"
            )
            
            # Create connection
            conn = swc.connect(
                url=url,
                key=f"multi_conn_{i}",
                auto_reconnect=True
            )
            
            # Status indicator
            if conn.state == "OPEN":
                st.success("🟢 Connected")
            elif conn.state == "CONNECTING":
                st.warning("🟡 Connecting...")
            else:
                st.error(f"🔴 {conn.state}")
            
            # Send message
            msg = st.text_input(f"Message {i+1}", key=f"msg_{i}")
            if st.button(f"Send", key=f"send_{i}"):
                if conn.is_open():
                    conn.send(msg)
                    st.success("Sent!")
                else:
                    st.error("Not connected")
            
            # Display received
            if conn.last_message:
                st.code(conn.last_message)

# Tab 3: Authentication
with tab3:
    st.header("Authentication Examples")
    
    auth_method = st.radio(
        "Authentication Method",
        ["No Auth", "Bearer Token", "API Key", "Custom Headers"]
    )
    
    headers = {}
    
    if auth_method == "Bearer Token":
        token = st.text_input("Bearer Token", type="password")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    
    elif auth_method == "API Key":
        api_key = st.text_input("API Key", type="password")
        key_header = st.text_input("Header Name", value="X-API-Key")
        if api_key and key_header:
            headers[key_header] = api_key
    
    elif auth_method == "Custom Headers":
        st.markdown("Add custom headers (one per line, format: `Key: Value`)")
        custom_headers = st.text_area("Headers", height=100)
        if custom_headers:
            for line in custom_headers.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
    
    # Display headers (masked)
    if headers:
        st.markdown("### Headers to be sent:")
        masked_headers = {}
        for k, v in headers.items():
            if k.lower() in ['authorization', 'x-api-key', 'api-key']:
                masked_headers[k] = v[:10] + "..." if len(v) > 10 else "***"
            else:
                masked_headers[k] = v
        st.json(masked_headers)
    
    # Test connection with auth
    ws_url = st.text_input(
        "WebSocket URL",
        value="wss://ws.postman-echo.com/raw",
        help="Use a WebSocket server that supports authentication"
    )
    
    if st.button("Connect with Authentication"):
        conn = swc.connect(
            url=ws_url,
            key="auth_test",
            headers=headers,
            auto_reconnect=False  # Don't auto-reconnect for auth tests
        )
        
        if conn.state == "OPEN":
            st.success("✅ Successfully connected with authentication!")
        elif conn.state == "ERROR":
            st.error(f"❌ Authentication failed: {conn.error}")
        else:
            st.warning(f"⏳ Connection state: {conn.state}")

# Tab 4: Performance Testing
with tab4:
    st.header("Performance & Stress Testing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Test Configuration")
        
        message_size = st.select_slider(
            "Message Size",
            options=[10, 100, 1000, 10000, 100000],
            format_func=lambda x: f"{x:,} bytes"
        )
        
        message_rate = st.slider(
            "Messages per second",
            1, 100, 10
        )
        
        test_duration = st.slider(
            "Test Duration (seconds)",
            1, 60, 10
        )
    
    with col2:
        st.subheader("Performance Metrics")
        
        if "perf_metrics" not in st.session_state:
            st.session_state.perf_metrics = {
                "sent": 0,
                "received": 0,
                "errors": 0,
                "start_time": None
            }
        
        metrics = st.session_state.perf_metrics
        
        metric1, metric2, metric3 = st.columns(3)
        with metric1:
            st.metric("Messages Sent", metrics["sent"])
        with metric2:
            st.metric("Messages Received", metrics["received"])
        with metric3:
            st.metric("Errors", metrics["errors"])
    
    # Performance test
    if st.button("Start Performance Test", type="primary"):
        conn = swc.connect(
            url="wss://ws.postman-echo.com/raw",
            key="perf_test"
        )
        
        if conn.is_open():
            st.session_state.perf_metrics["start_time"] = time.time()
            st.session_state.perf_metrics["sent"] = 0
            st.session_state.perf_metrics["received"] = 0
            st.session_state.perf_metrics["errors"] = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Generate test message
            test_data = "x" * message_size
            
            start_time = time.time()
            messages_to_send = int(message_rate * test_duration)
            
            for i in range(messages_to_send):
                try:
                    # Send message
                    conn.send({
                        "seq": i,
                        "data": test_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.session_state.perf_metrics["sent"] += 1
                    
                    # Update progress
                    progress = (i + 1) / messages_to_send
                    progress_bar.progress(progress)
                    status_text.text(f"Sending message {i+1}/{messages_to_send}")
                    
                    # Rate limiting
                    time.sleep(1.0 / message_rate)
                    
                except Exception as e:
                    st.session_state.perf_metrics["errors"] += 1
                    st.error(f"Error: {e}")
            
            # Calculate results
            elapsed = time.time() - start_time
            st.success(f"Test completed in {elapsed:.2f} seconds")
            
            # Performance summary
            st.markdown("### Performance Summary")
            st.json({
                "Total Messages": st.session_state.perf_metrics["sent"],
                "Success Rate": f"{(1 - metrics['errors']/max(metrics['sent'], 1)) * 100:.1f}%",
                "Average Rate": f"{metrics['sent']/elapsed:.1f} msg/sec",
                "Total Data Sent": f"{metrics['sent'] * message_size / 1024 / 1024:.2f} MB"
            })
        else:
            st.error("Failed to connect for performance test")

# Footer
st.markdown("---")
st.caption(
    "These examples demonstrate advanced features of streamlit-websocket-client including "
    "error handling, multiple connections, authentication, and performance testing."
)