import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📊 Real-Time Stock Price Dashboard")

# Sidebar
ticker = st.sidebar.text_input("Stock Ticker", "RELIANCE.NS")
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])
ma_window = st.sidebar.slider("Moving Average Window", 5, 50, 20)

@st.cache_data(ttl=60)
def load_data(ticker, period):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

df = load_data(ticker, period)

if df.empty:
    st.error("Invalid ticker or no data available.")
    st.stop()

# Moving Average
df["MA"] = df["Close"].rolling(ma_window).mean()

# Candlestick Chart
fig = go.Figure()
fig.add_candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price"
)
fig.add_scatter(
    x=df.index,
    y=df["MA"],
    mode="lines",
    name=f"MA {ma_window}"
)

fig.update_layout(height=500, xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Last Close", f"₹{df['Close'][-1]:.2f}")
col2.metric("High", f"₹{df['High'].max():.2f}")
col3.metric("Low", f"₹{df['Low'].min():.2f}")

st.caption("Data source: Yahoo Finance | Auto-refresh every 60s")
