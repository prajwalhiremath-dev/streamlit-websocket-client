"""
Live Financial Dashboard Example
Demonstrates real-time data visualization using streamlit-websocket-client
"""

import streamlit as st
import streamlit_websocket_client as swc
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="Live Trading Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if "price_history" not in st.session_state:
    st.session_state.price_history = []
if "volume_history" not in st.session_state:
    st.session_state.volume_history = []
if "trades_history" not in st.session_state:
    st.session_state.trades_history = []

st.title("📊 Live Cryptocurrency Trading Dashboard")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Select trading pair
    trading_pair = st.selectbox(
        "Trading Pair",
        ["btcusdt", "ethusdt", "bnbusdt", "adausdt", "dogeusdt"],
        index=0
    )
    
    # Chart settings
    st.subheader("Chart Settings")
    max_points = st.slider("Max Data Points", 50, 500, 200)
    update_interval = st.slider("Update Interval (ms)", 100, 2000, 500)
    
    # Display settings
    show_volume = st.checkbox("Show Volume Chart", value=True)
    show_trades = st.checkbox("Show Recent Trades", value=True)
    show_orderbook = st.checkbox("Show Order Book", value=True)
    
    st.markdown("---")
    st.markdown("### Data Source")
    st.info("Connected to Binance WebSocket API")

# Create main layout
if show_orderbook:
    col1, col2 = st.columns([3, 1])
else:
    col1 = st.container()
    col2 = None

# Connect to Binance WebSocket
ws_url = f"wss://stream.binance.com:9443/ws/{trading_pair}@trade"
conn = swc.connect(
    url=ws_url,
    key=f"binance_{trading_pair}",
    auto_reconnect=True,
    reconnect_interval=3000
)

# Connection status
status_placeholder = st.empty()
with status_placeholder.container():
    if conn.state == "OPEN":
        st.success(f"🟢 Connected to {trading_pair.upper()} stream")
    elif conn.state == "CONNECTING":
        st.warning("🟡 Connecting to Binance...")
    else:
        st.error(f"🔴 Connection {conn.state}")

# Process incoming trade data
current_price = 0
current_volume = 0

if conn.last_message:
    try:
        trade_data = json.loads(conn.last_message) if isinstance(conn.last_message, str) else conn.last_message
        
        # Extract trade information
        current_price = float(trade_data.get('p', 0))
        current_volume = float(trade_data.get('q', 0))
        trade_time = datetime.fromtimestamp(trade_data.get('T', 0) / 1000)
        is_buyer_maker = trade_data.get('m', False)
        
        # Update history
        st.session_state.price_history.append({
            'time': trade_time,
            'price': current_price,
            'volume': current_volume,
            'side': 'sell' if is_buyer_maker else 'buy'
        })
        
        # Keep only recent data points
        st.session_state.price_history = st.session_state.price_history[-max_points:]
        
    except Exception as e:
        st.error(f"Error processing trade data: {e}")

# Main content area
with col1:
    # Price metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    if st.session_state.price_history:
        df = pd.DataFrame(st.session_state.price_history)
        current_price = df['price'].iloc[-1]
        
        # Calculate metrics
        if len(df) > 1:
            price_change = current_price - df['price'].iloc[0]
            price_change_pct = (price_change / df['price'].iloc[0]) * 100
            total_volume = df['volume'].sum()
            avg_price = df['price'].mean()
        else:
            price_change = 0
            price_change_pct = 0
            total_volume = current_volume
            avg_price = current_price
        
        with metric_col1:
            st.metric(
                "Current Price",
                f"${current_price:,.2f}",
                f"{price_change:+,.2f} ({price_change_pct:+.2f}%)"
            )
        
        with metric_col2:
            st.metric(
                "24h Volume",
                f"{total_volume:,.4f}",
                f"{trading_pair.upper()}"
            )
        
        with metric_col3:
            st.metric(
                "Average Price",
                f"${avg_price:,.2f}"
            )
        
        with metric_col4:
            buy_trades = len(df[df['side'] == 'buy'])
            sell_trades = len(df[df['side'] == 'sell'])
            st.metric(
                "Buy/Sell Ratio",
                f"{buy_trades}/{sell_trades}"
            )
    
    # Price chart
    st.subheader("Price Chart")
    
    if st.session_state.price_history:
        df = pd.DataFrame(st.session_state.price_history)
        
        # Create candlestick-like chart
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['price'],
            mode='lines',
            name='Price',
            line=dict(color='#00D4FF', width=2)
        ))
        
        # Add buy/sell markers
        buy_df = df[df['side'] == 'buy']
        sell_df = df[df['side'] == 'sell']
        
        fig.add_trace(go.Scatter(
            x=buy_df['time'],
            y=buy_df['price'],
            mode='markers',
            name='Buy',
            marker=dict(color='green', size=8, symbol='triangle-up')
        ))
        
        fig.add_trace(go.Scatter(
            x=sell_df['time'],
            y=sell_df['price'],
            mode='markers',
            name='Sell',
            marker=dict(color='red', size=8, symbol='triangle-down')
        ))
        
        fig.update_layout(
            title=f"{trading_pair.upper()} Price",
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            hovermode='x unified',
            template='plotly_dark',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for trade data...")
    
    # Volume chart
    if show_volume and st.session_state.price_history:
        st.subheader("Volume Analysis")
        
        df = pd.DataFrame(st.session_state.price_history)
        
        # Create volume bars
        fig_volume = go.Figure()
        
        colors = ['green' if side == 'buy' else 'red' for side in df['side']]
        
        fig_volume.add_trace(go.Bar(
            x=df['time'],
            y=df['volume'],
            name='Volume',
            marker_color=colors
        ))
        
        fig_volume.update_layout(
            title="Trade Volume",
            xaxis_title="Time",
            yaxis_title="Volume",
            template='plotly_dark',
            height=300
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)

# Order book simulation (right column)
if col2 and show_orderbook:
    with col2:
        st.subheader("Order Book")
        st.caption("(Simulated)")
        
        # Generate fake order book data
        if current_price > 0:
            spread = current_price * 0.001
            
            # Bids
            st.markdown("**Bids** 🟢")
            bids = []
            for i in range(5):
                price = current_price - (spread * (i + 1))
                amount = np.random.uniform(0.1, 2.0)
                bids.append({
                    'Price': f"${price:,.2f}",
                    'Amount': f"{amount:,.4f}"
                })
            st.dataframe(pd.DataFrame(bids), hide_index=True)
            
            # Current price
            st.metric("Mid Price", f"${current_price:,.2f}")
            
            # Asks
            st.markdown("**Asks** 🔴")
            asks = []
            for i in range(5):
                price = current_price + (spread * (i + 1))
                amount = np.random.uniform(0.1, 2.0)
                asks.append({
                    'Price': f"${price:,.2f}",
                    'Amount': f"{amount:,.4f}"
                })
            st.dataframe(pd.DataFrame(asks), hide_index=True)

# Recent trades table
if show_trades and st.session_state.price_history:
    st.subheader("Recent Trades")
    
    df = pd.DataFrame(st.session_state.price_history[-20:])  # Last 20 trades
    df['time'] = df['time'].dt.strftime('%H:%M:%S')
    df['price'] = df['price'].apply(lambda x: f"${x:,.2f}")
    df['volume'] = df['volume'].apply(lambda x: f"{x:,.4f}")
    df['side'] = df['side'].apply(lambda x: "🟢 BUY" if x == 'buy' else "🔴 SELL")
    
    st.dataframe(
        df[['time', 'price', 'volume', 'side']],
        hide_index=True,
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption("Data provided by Binance WebSocket API. This is a demonstration of real-time data streaming capabilities.")