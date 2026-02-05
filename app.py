import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from yfinance.exceptions import YFRateLimitError

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Real-Time Stock Dashboard",
    layout="wide"
)

st.title("📊 Stock Price Dashboard")

# --------------------------------------------------
# Sidebar Controls
# --------------------------------------------------
st.sidebar.header("Settings")

ticker = st.sidebar.text_input(
    "Stock Ticker",
    value="RELIANCE.NS",
    help="Examples: RELIANCE.NS, TCS.NS, AAPL, MSFT"
).upper().strip()

period = st.sidebar.selectbox(
    "Historical Period",
    ["1mo", "3mo", "6mo", "1y"]
)

ma_window = st.sidebar.slider(
    "Moving Average Window",
    min_value=5,
    max_value=50,
    value=20
)

# --------------------------------------------------
# Data Loader (Safe + Cached)
# --------------------------------------------------
@st.cache_data(ttl=300)  # 5 minutes
def load_data(ticker: str, period: str):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

# --------------------------------------------------
# Fetch Data with Error Handling
# --------------------------------------------------
try:
    df = load_data(ticker, period)
except YFRateLimitError:
    st.warning(
        "⚠️ Yahoo Finance rate limit reached.\n\n"
        "Please wait a few minutes and refresh."
    )
    st.stop()
except Exception as e:
    st.error("❌ Unexpected error while fetching data.")
    st.stop()

if df.empty:
    st.error("❌ No data found. Please check the ticker symbol.")
    st.stop()

# --------------------------------------------------
# Feature Engineering
# --------------------------------------------------
df["MA"] = df["Close"].rolling(window=ma_window).mean()

# --------------------------------------------------
# Candlestick Chart
# --------------------------------------------------
fig = go.Figure()

fig.add_candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price"
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MA"],
        mode="lines",
        name=f"MA {ma_window}"
    )
)

fig.update_layout(
    height=500,
    xaxis_rangeslider_visible=False,
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Metrics
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Last Close", f"₹{df['Close'].iloc[-1]:.2f}")
col2.metric("High", f"₹{df['High'].max():.2f}")
col3.metric("Low", f"₹{df['Low'].min():.2f}")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.caption(
    "📌 Data Source: Yahoo Finance (via yfinance)\n"
    "• Cached for 5 minutes to avoid rate limiting"
)
