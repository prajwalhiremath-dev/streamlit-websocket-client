"""
WebSocket Chat Application Example
Demonstrates a real-time chat interface using streamlit-websocket-client
"""

import streamlit as st
import streamlit_websocket_client as swc
import json
from datetime import datetime
import uuid

st.set_page_config(
    page_title="WebSocket Chat",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "username" not in st.session_state:
    st.session_state.username = f"User_{st.session_state.user_id}"

st.title("💬 WebSocket Chat Room")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Username input
    username = st.text_input("Username", value=st.session_state.username)
    if username != st.session_state.username:
        st.session_state.username = username
    
    # Server URL
    server_url = st.text_input(
        "WebSocket Server",
        value="wss://ws.postman-echo.com/raw",
        help="Enter your chat server WebSocket URL"
    )
    
    # Connection status
    st.markdown("### Connection Info")

# Main chat interface
chat_container = st.container()
input_container = st.container()

# Create WebSocket connection
conn = swc.connect(
    url=server_url,
    key="chat_connection",
    auto_reconnect=True,
    reconnect_interval=2000,
    max_reconnect_attempts=10
)

# Update sidebar with connection status
with st.sidebar:
    if conn.state == "OPEN":
        st.success(f"🟢 Connected")
    elif conn.state == "CONNECTING":
        st.warning(f"🟡 Connecting...")
    elif conn.state == "CLOSED":
        st.error(f"🔴 Disconnected")
    elif conn.state == "ERROR":
        st.error(f"🔴 Error: {conn.error}")
    
    st.text(f"Ready State: {conn.ready_state}")
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Handle received messages
if conn.last_message:
    try:
        # Try to parse as JSON (for structured chat messages)
        if isinstance(conn.last_message, str):
            try:
                msg_data = json.loads(conn.last_message)
            except:
                # If not JSON, treat as plain text
                msg_data = {
                    "type": "message",
                    "user": "System",
                    "content": conn.last_message,
                    "timestamp": datetime.now().isoformat()
                }
        else:
            msg_data = conn.last_message
        
        # Add to message history if it's a new message
        if msg_data not in st.session_state.messages:
            st.session_state.messages.append(msg_data)
    except Exception as e:
        st.error(f"Error processing message: {e}")

# Display chat messages
with chat_container:
    st.markdown("### Chat Messages")
    
    # Create a scrollable area for messages
    message_area = st.container()
    
    with message_area:
        for msg in st.session_state.messages:
            if isinstance(msg, dict):
                user = msg.get("user", "Unknown")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                msg_type = msg.get("type", "message")
                
                # Different styling for different message types
                if msg_type == "system":
                    st.info(f"🔔 {content}")
                elif user == st.session_state.username:
                    # Current user's messages (right-aligned)
                    col1, col2 = st.columns([1, 3])
                    with col2:
                        st.markdown(
                            f"""
                            <div style="text-align: right; background-color: #007bff; color: white; 
                                        padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>{user}</strong><br>
                                {content}<br>
                                <small style="opacity: 0.7;">{timestamp[:19]}</small>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    # Other users' messages (left-aligned)
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(
                            f"""
                            <div style="background-color: #f1f1f1; color: black; 
                                        padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>{user}</strong><br>
                                {content}<br>
                                <small style="opacity: 0.7;">{timestamp[:19]}</small>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                # Fallback for non-dict messages
                st.text(str(msg))

# Input area
with input_container:
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        message_input = st.text_input(
            "Type a message...",
            key="message_input",
            placeholder="Enter your message and press Enter",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    # Additional message options
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("👋 Send Hello"):
            message_input = "Hello everyone! 👋"
            send_button = True
    
    with col4:
        if st.button("😊 Send Emoji"):
            message_input = "😊 👍 ❤️"
            send_button = True
    
    with col5:
        if st.button("📍 Send Location"):
            message_input = "📍 I'm here!"
            send_button = True

# Send message
if (message_input and send_button) or (message_input and st.session_state.get("enter_pressed")):
    if conn.is_open():
        # Create structured message
        chat_message = {
            "type": "message",
            "user": st.session_state.username,
            "content": message_input,
            "timestamp": datetime.now().isoformat(),
            "user_id": st.session_state.user_id
        }
        
        # Send message
        conn.send(chat_message)
        
        # Add to local message history (for echo servers)
        st.session_state.messages.append(chat_message)
        
        # Clear input
        st.rerun()
    else:
        st.error("⚠️ Not connected to server. Please wait for connection...")

# Display typing indicator
if conn.is_open():
    st.markdown(
        """
        <style>
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        .typing-indicator {
            animation: pulse 1.5s infinite;
            color: #666;
            font-style: italic;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Footer with statistics
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Messages", len(st.session_state.messages))

with col2:
    st.metric("Connection Status", conn.state)

with col3:
    if st.session_state.messages:
        last_msg_time = st.session_state.messages[-1].get("timestamp", "N/A")
        st.metric("Last Message", last_msg_time[:19] if isinstance(last_msg_time, str) else "N/A")