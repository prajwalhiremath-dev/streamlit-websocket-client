# streamlit-websocket-client

A Streamlit component for real-time bidirectional WebSocket communication. Built to solve the challenge of real-time data streaming in Streamlit's execution model.

[![PyPI version](https://badge.fury.io/py/streamlit-websocket-client.svg)](https://badge.fury.io/py/streamlit-websocket-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/yourusername/streamlit-websocket-client-demo/main)

## 🎯 Features

- **Real-time Communication**: True WebSocket support with automatic "push-to-rerun" mechanism
- **Bidirectional**: Send and receive messages seamlessly
- **Auto-reconnection**: Built-in reconnection logic with configurable parameters
- **Simple API**: Easy to use with just a few lines of code
- **Session State Integration**: Properly manages connection lifecycle across Streamlit reruns
- **Type Safety**: Full TypeScript support on the frontend
- **Lightweight**: Minimal dependencies, leveraging Streamlit's component system

## 📦 Installation

```bash
pip install streamlit-websocket-client
```

## 🚀 Quick Start

```python
import streamlit as st
import streamlit_websocket_client as swc

# Connect to a WebSocket server
conn = swc.connect(
    url="wss://echo.websocket.org",
    key="my_connection"
)

# Display connection status
st.write(f"Connection state: {conn.state}")

# Send a message
if st.button("Send Hello"):
    conn.send("Hello, WebSocket!")

# Display received messages
if conn.last_message:
    st.write(f"Received: {conn.last_message}")
```

## 📖 API Reference

### `connect()`

Creates a WebSocket client connection.

```python
conn = swc.connect(
    url: str,                    # WebSocket URL (ws:// or wss://)
    key: str,                    # Unique component key
    headers: dict = None,        # Optional HTTP headers
    protocols: list = None,      # Optional subprotocols
    auto_reconnect: bool = True, # Auto-reconnect on disconnect
    reconnect_interval: int = 3000,  # Reconnect interval (ms)
    max_reconnect_attempts: int = 5,  # Max reconnection attempts
)
```

### `WebSocketConnection`

The connection object returned by `connect()`.

**Attributes:**
- `state`: Current connection state ("CONNECTING", "OPEN", "CLOSED", "ERROR")
- `last_message`: The most recent message received
- `error`: Error message if any
- `ready_state`: WebSocket ready state (0-3)

**Methods:**
- `send(message)`: Send a message (string, dict, or list)
- `is_open()`: Check if connection is open

## 🎨 Examples

### Live Dashboard

```python
import streamlit as st
import streamlit_websocket_client as swc
import json

st.title("📊 Live Trading Dashboard")

# Connect to trading data feed
conn = swc.connect(
    url="wss://stream.binance.com:9443/ws/btcusdt@trade",
    key="binance_stream"
)

if conn.last_message:
    data = json.loads(conn.last_message)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Price", f"${float(data['p']):.2f}")
    with col2:
        st.metric("Quantity", f"{float(data['q']):.4f}")
    with col3:
        st.metric("Time", data['T'])
```

### Chat Application

```python
import streamlit as st
import streamlit_websocket_client as swc

st.title("💬 WebSocket Chat")

# Connect to chat server
conn = swc.connect(
    url="wss://your-chat-server.com/ws",
    key="chat_connection",
    headers={"Authorization": f"Bearer {st.secrets['auth_token']}"}
)

# Display messages
if conn.last_message:
    with st.chat_message("assistant"):
        st.write(conn.last_message)

# Send messages
if prompt := st.chat_input("Type a message..."):
    with st.chat_message("user"):
        st.write(prompt)
    conn.send({"type": "message", "content": prompt})
```

### IoT Device Monitoring

```python
import streamlit as st
import streamlit_websocket_client as swc
import pandas as pd

st.title("🌡️ IoT Sensor Dashboard")

conn = swc.connect(
    url="wss://iot-gateway.example.com/sensors",
    key="iot_connection"
)

if conn.last_message:
    sensor_data = conn.last_message
    
    # Display real-time metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperature", f"{sensor_data['temp']}°C")
    with col2:
        st.metric("Humidity", f"{sensor_data['humidity']}%")
    with col3:
        st.metric("Pressure", f"{sensor_data['pressure']} hPa")
    
    # Update time series chart
    if "sensor_history" not in st.session_state:
        st.session_state.sensor_history = []
    
    st.session_state.sensor_history.append(sensor_data)
    df = pd.DataFrame(st.session_state.sensor_history[-100:])
    st.line_chart(df[['temp', 'humidity']])
```

## 🔧 Development

### Building from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/streamlit-websocket-client.git
cd streamlit-websocket-client
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
cd streamlit_websocket_client/frontend
npm install
```

3. Run in development mode:
```bash
# Terminal 1: Start the frontend dev server
cd streamlit_websocket_client/frontend
npm start

# Terminal 2: Run your Streamlit app with dev mode
export STREAMLIT_WEBSOCKET_DEVELOP=true
streamlit run examples/basic_client.py
```

### Running Tests

```bash
# Python tests
pytest tests/

# Frontend tests
cd streamlit_websocket_client/frontend
npm test
```

## 🏗️ Architecture

This library uses Streamlit's Bidirectional Component framework to achieve real-time updates:

1. **Frontend Component**: A React component that manages the WebSocket connection in the browser
2. **Python API**: Clean interface that communicates with the frontend
3. **Push-to-Rerun**: When messages arrive, the frontend triggers a Streamlit rerun
4. **Session State**: Maintains connection state across reruns

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of [Streamlit's Component framework](https://docs.streamlit.io/library/components)
- Inspired by the need for real-time data in Streamlit applications
- Thanks to the Streamlit community for feedback and suggestions

## 🔗