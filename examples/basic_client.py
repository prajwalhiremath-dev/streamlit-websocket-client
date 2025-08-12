"""
Basic WebSocket Client Example
Demonstrates connecting to a WebSocket server and displaying real-time data
"""

import streamlit as st
import streamlit_websocket_client as swc
import json
from datetime import datetime

st.set_page_config(
    page_title="WebSocket Real-time Dashboard",
    page_icon="🔌",
    layout="wide"
)

st.title("🔌 Real-time WebSocket Dashboard")
st.markdown("This example shows how to connect to a WebSocket server and display live data.")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # WebSocket URL input
    ws_url = st.text_input(
        "WebSocket URL",
        value="wss://ws.postman-echo.com/raw",  # Free echo server for testing
        help="Enter the WebSocket server URL (e.g., wss://example.com/ws)"
    )
    
    # Connection options
    auto_reconnect = st.checkbox("Auto-reconnect", value=True)
    reconnect_interval = st.slider(
        "Reconnect interval (seconds)", 
        min_value=1, 
        max_value=10, 
        value=3
    )
    
    # Authentication (if needed)
    use_auth = st.checkbox("Use Authentication")
    if use_auth:
        auth_token = st.text_input("Auth Token", type="password")
        headers = {"Authorization": f"Bearer {auth_token}"}
    else:
        headers = None

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Data Stream")
    
    # Create WebSocket connection
    conn = swc.connect(
        url=ws_url,
        key="main_connection",
        headers=headers,
        auto_reconnect=auto_reconnect,
        reconnect_interval=reconnect_interval * 1000,  # Convert to ms
        height=0  # Invisible component
    )
    
    # Display connection status
    status_color = {
        "CONNECTING": "🟡",
        "OPEN": "🟢",
        "CLOSED": "🔴",
        "ERROR": "🔴"
    }
    
    st.metric(
        "Connection Status",
        conn.state,
        delta=None,
        help=f"WebSocket ready state: {conn.ready_state}"
    )
    
    # Show status indicator
    st.markdown(f"{status_color.get(conn.state, '⚪')} **{conn.state}**")
    
    if conn.error:
        st.error(f"Connection error: {conn.error}")
    
    # Display received messages
    if conn.last_message:
        st.info("Latest Message Received:")
        
        # Try to parse as JSON for pretty display
        try:
            if isinstance(conn.last_message, str):
                message_data = json.loads(conn.last_message)
                st.json(message_data)
            else:
                st.json(conn.last_message)
        except:
            st.code(conn.last_message)
        
        # Store messages in session state for history
        if "message_history" not in st.session_state:
            st.session_state.message_history = []
        
        st.session_state.message_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": conn.last_message
        })
        
        # Keep only last 10 messages
        st.session_state.message_history = st.session_state.message_history[-10:]

with col2:
    st.subheader("Send Message")
    
    # Message input
    message_type = st.radio("Message Type", ["Text", "JSON"])
    
    if message_type == "Text":
        message = st.text_area("Message", height=100)
        if st.button("Send Text", disabled=not conn.is_open()):
            if message:
                conn.send(message)
                st.success("Message sent!")
    else:
        # JSON input with example
        default_json = '{"type": "ping", "timestamp": "' + datetime.now().isoformat() + '"}'
        message = st.text_area("JSON Message", value=default_json, height=100)
        if st.button("Send JSON", disabled=not conn.is_open()):
            try:
                json_msg = json.loads(message)
                conn.send(json_msg)
                st.success("JSON message sent!")
            except json.JSONDecodeError:
                st.error("Invalid JSON format")

# Message History
st.subheader("Message History")
if "message_history" in st.session_state and st.session_state.message_history:
    history_df = []
    for item in st.session_state.message_history:
        history_df.append({
            "Time": item["timestamp"],
            "Message": str(item["message"])[:100] + "..." if len(str(item["message"])) > 100 else str(item["message"])
        })
    
    st.table(history_df)
else:
    st.info("No messages received yet. Send a message to see it echoed back!")

# Tips
with st.expander("💡 Tips"):
    st.markdown("""
    ### Testing WebSocket Connections
    
    1. **Echo Server**: The default URL (wss://ws.postman-echo.com/raw) is a free echo server that returns any message you send.
    
    2. **Local Development**: To test with a local WebSocket server:
       ```python
       # Simple WebSocket server (save as server.py)
       import asyncio
       import websockets
       
       async def echo(websocket, path):
           async for message in websocket:
               await websocket.send(f"Echo: {message}")
       
       start_server = websockets.serve(echo, "localhost", 8765)
       asyncio.get_event_loop().run_until_complete(start_server)
       asyncio.get_event_loop().run_forever()
       ```
       Then connect to `ws://localhost:8765`
    
    3. **Real-time Data**: For production use, connect to your actual WebSocket API endpoints for live data feeds, chat systems, or IoT devices.
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using streamlit-websocket-client")