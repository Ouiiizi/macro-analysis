import streamlit as st
import pandas as pd
import requests
from io import StringIO
import plotly.graph_objects as go
from scipy import stats
import numpy as np

@st.cache_data(ttl=600)  
def fetch_sharesansar_live():
    url = "https://www.sharesansar.com/today-share-price"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        dfs = pd.read_html(StringIO(r.text))
        if dfs:
            df = dfs[0]
            # Clean up the dataframe
            df = df.dropna(subset=['Symbol', 'LTP'])
            return df
    except Exception as e:
        st.error(f"Error fetching from ShareSansar API: {e}")
        return None
    return None

def NepseLive():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 36px; border-bottom: none; margin-bottom: 0px;">Live NEPSE Market Archive</h1>
        <p style="font-family: 'Courier New', Courier, monospace; font-size: 16px; color: #5a5a5a;">Real-Time Data Provided by ShareSansar API</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Fetching live stock data from ShareSansar..."):
        df = fetch_sharesansar_live()
    
    if df is None or df.empty:
        st.warning("Currently unable to fetch market data. The market might be closed or the connection failed.")
        return

    symbols = df['Symbol'].unique().tolist()
    
    st.markdown("###  Market Selection")
    selected_symbol = st.selectbox("Select a Company Symbol for Live Analysis", sorted(symbols))
    
    company_data = df[df['Symbol'] == selected_symbol].iloc[0]
    
    # Extract keys and clean numericals
    try:
        ltp = float(company_data['LTP'])
        open_p = float(company_data['Open'])
        high_p = float(company_data['High'])
        low_p = float(company_data['Low'])
        vol = float(company_data['Vol'])
        turnover = float(company_data['Turnover'])
        d120 = float(company_data['120 Days'])
        d180 = float(company_data['180 Days'])
        high_52 = float(company_data['52 Weeks High'])
        low_52 = float(company_data['52 Weeks Low'])
    except ValueError:
        st.warning("Selected symbol has incomplete numeric data.")
        return

    # Metrics Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Live Price (LTP)", f"Rs. {ltp:,.2f}", f"Open: {open_p}")
    col2.metric("Day High / Low", f"{high_p} / {low_p}")
    col3.metric("Trade Volume", f"{vol:,.0f} units")
    col4.metric("Turnover", f"Rs. {turnover:,.0f}")
    
    st.markdown("---")
    st.markdown(f"###  {selected_symbol} Synthesized Trajectory & Projection")
    st.markdown("Utilizing ShareSansar's 180-Day, 120-Day, and 52-Week metrics to construct a simulated historical regression map for projection.")
    
    # We construct a synthetic timeline using the actual moving averages and highs/lows
    # Timeline x-axis mapping (mock days into the past to current day)
    # -180: 180 days ago average
    # -120: 120 days ago average
    # 0: Current LTP
    
    # For a visually appealing projection, we interpolate data points between moving averages to present
    x_hist = np.linspace(-180, 0, 100)
    
    # Let's do a simple polynomial or linear curve fitting from the known key stats
    # Known anchors: (-180, d180), (-120, d120), (0, ltp)
    anchors_x = [-180, -120, 0]
    anchors_y = [d180, d120, ltp]
    
    # Regression on the anchors to project the general trend
    slope, intercept, r_value, p_value, std_err = stats.linregress(anchors_x, anchors_y)
    
    # Simulated Historical Path (to look like a graph rather than a straight line)
    # We use a polyfit of degree 2 to give it a curve, plus some random noise bound by 52w high/low
    poly = np.poly1d(np.polyfit(anchors_x, anchors_y, 2))
    y_hist_smooth = poly(x_hist)
    
    # Add minor noise based on volatility (high-low spread normalized)
    volatility = (high_p - low_p) * 0.5
    noise = np.random.normal(0, volatility if volatility > 0 else 1, len(x_hist))
    y_hist = y_hist_smooth + noise
    
    # Clip to 52 week limits
    y_hist = np.clip(y_hist, low_52, high_52)
    y_hist[-1] = ltp # Ensure last point is exactly LTP
    
    # Projection (next 30 days) based on the linear trend of the anchors
    x_proj = np.linspace(1, 30, 30)
    y_proj = slope * x_proj + intercept
    
    fig = go.Figure()
    
    # History trace
    fig.add_trace(go.Scatter(
        x=x_hist, y=y_hist, 
        mode='lines', 
        name='Estimated History', 
        line=dict(color='#2b2b2b', width=2)
    ))
    
    # Anchors
    fig.add_trace(go.Scatter(
        x=anchors_x, y=anchors_y, 
        mode='markers', 
        name='Sharesansar Key Averages', 
        marker=dict(size=12, color='#1c1c1c', symbol='diamond')
    ))
    
    # Next 30 Days Projection
    fig.add_trace(go.Scatter(
        x=x_proj, y=y_proj, 
        mode='lines+markers', 
        name='Next 30D Projection', 
        line=dict(color='#8c5f39', width=2, dash='dot'),
        marker=dict(size=6, color='#8c5f39')
    ))
    
    # 52 Week High / Low Bounds
    fig.add_hline(y=high_52, line_dash="dash", line_color="#b25f44", annotation_text="52W High")
    fig.add_hline(y=low_52, line_dash="dash", line_color="#b25f44", annotation_text="52W Low")
    
    fig.update_layout(
        title=f"Trend & Projection: {selected_symbol}",
        yaxis_title="Stock Price (NPR)",
        xaxis_title="Time (Days from Today)",
        hovermode="closest",
        template="simple_white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander(f"View Full Live Table Data for {selected_symbol}"):
        st.dataframe(pd.DataFrame(company_data).T, use_container_width=True)
