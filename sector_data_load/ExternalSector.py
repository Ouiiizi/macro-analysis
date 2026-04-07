import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy import stats
import os
import numpy as np

st.markdown("""
<style>
    /* Modern Archive-esque Theme */
    div.stButton > button {
        background-color: #f4f0ec;
        color: #1c1c1c;
        border: 1px solid #1c1c1c;
        border-radius: 0px;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #1c1c1c;
        color: #fdfbf7;
    }
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        border-bottom: 2px solid #2b2b2b;
        padding-bottom: 5px;
    }
    div[data-baseweb="select"] > div {
        border-radius: 0px;
        border: 1px solid #1c1c1c;
    }
    .streamlit-expanderHeader {
        font-family: 'Courier New', Courier, monospace;
        border-bottom: 1px solid #2b2b2b;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "External Sector")
CSV_FILES = {
    "Exports": "Exports.csv",
    "Imports": "Imports.csv",
    "Foreign Employment": "ForeignEmploymentCount.csv",
    "USD Conversion Rates": "USDConversionRates.csv"
}

def load_csv(child_name):
    file_path = os.path.join(DATA_DIR, CSV_FILES[child_name])

    if child_name in ["Exports", "Imports", "Foreign Employment"]:
        df = pd.read_csv(file_path)

        if 'S.N.' in df.columns:
            df = df.drop(columns=['S.N.'])
        elif 'S.No.' in df.columns:
            df = df.drop(columns=['S.No.'])

        if df.iloc[0].isna().any() or (df.iloc[0] == "Annual").any():
            df = df.iloc[1:].reset_index(drop=True)

        category_col = df.columns[0]
        df_long = df.melt(id_vars=[category_col], var_name='Year', value_name='Value')
        df_long.rename(columns={category_col: "Category"}, inplace=True)

    else:
        df = pd.read_csv(file_path, skiprows=1)

        df.columns = [col.strip() if 'Unnamed' not in col else 'Year' for col in df.columns]
        df_long = df.melt(id_vars=['Year'], var_name='Category', value_name='Value')

        df_long = df_long[df_long['Category'] != 'Middle']

    df_long['Value'] = pd.to_numeric(df_long['Value'].astype(str).str.replace(",", ""), errors='coerce')
    df_long = df_long.dropna(subset=['Value'])
    return df_long

def show_graph(df, category=None):
    """Render a clean, interactive Streamlit line chart for combined or individual data."""
    title = f"{category} Trend Over Time" if category else "All Categories Trend Over Time"
    st.subheader(f" {title}")

    try:
        import plotly.express as px
        chart_data_filtered = df[df['Category'] == category] if category else df
        fig = px.line(chart_data_filtered, x='Year', y='Value', color='Category', markers=True, template='simple_white')
        fig.update_layout(yaxis_title="Value", xaxis_title="Year", hovermode="closest", margin=dict(l=20, r=20, t=10, b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render chart: {e}")

def regression_projection(df, category):
    """Simple linear regression with a projection point."""
    df_cat = df[df['Category'] == category]
    if df_cat.empty:
        st.warning(f"No data found for {category}")
        return

    y_values = df_cat['Value'].values
    years = df_cat['Year'].tolist()
    x_indices = list(range(len(y_values)))

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_indices, y_values)

    st.markdown(f"## Analysis: {category}")

    col1, col2 = st.columns(2)
    col1.write(f"**Confidence (R-squared):** {r_value**2:.3f}")

    next_x = len(x_indices)
    next_val = slope * next_x + intercept
    col2.write(f"**Projected value for next step:** {next_val:,.2f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=y_values, mode='markers', name='Actual Data', marker=dict(size=8, color='blue')))
    fig.add_trace(go.Scatter(x=years, y=[slope * i + intercept for i in x_indices], mode='lines', name='Trend Line', line=dict(color='red', width=2)))

    next_year = "Next Period"
    fig.add_trace(go.Scatter(x=[next_year], y=[next_val], mode='markers', name='Projection', marker=dict(size=12, color='green')))

    fig.update_layout(
        title=f"Regression & Projection: {category}",
        yaxis_title="Value",
        xaxis_title="Year",
        hovermode="closest",
        xaxis=dict(tickangle=-45)
    )

    st.plotly_chart(fig, use_container_width=True)

def child_buttons(df):
    """Interactive UI for data visualization and analysis."""
    categories = df['Category'].unique().tolist()

    st.subheader(" Trend Visualization")

    with st.expander(" Filter Categories"):
        selected_sectors = st.multiselect(
            "Select Categories to Display",
            options=categories,
            default=categories,
            key=f"ms_{df.iloc[0,0]}"
        )

    if selected_sectors:
        try:
            import plotly.express as px
            chart_data_filtered = df[df['Category'].isin(selected_sectors)]
            fig = px.line(chart_data_filtered, x='Year', y='Value', color='Category', markers=True, template='simple_white')
            fig.update_layout(yaxis_title="Value", xaxis_title="Year", hovermode="closest", margin=dict(l=20, r=20, t=10, b=20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering chart: {e}")
    else:
        st.warning("Please select at least one category to visualize.")

    st.markdown("---")

    st.subheader(" Detailed Analysis")

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_category = st.selectbox("Select Category for In-depth Tools", categories)
    with col_btn:
        st.write(" ")
        run_reg = st.button("Run Regression", use_container_width=True)

    if run_reg:
        regression_projection(df, selected_category)

    st.write(" ")
    with st.expander(" View Raw Data Table"):
        st.dataframe(df[df['Category'] == selected_category], use_container_width=True)

def exports():
    st.header("Exports Analysis")
    df = load_csv("Exports")
    child_buttons(df)

def imports():
    st.header("Imports Analysis")
    df = load_csv("Imports")
    child_buttons(df)

def foreign_employment():
    st.header("Foreign Employment Count")
    df = load_csv("Foreign Employment")
    child_buttons(df)

def usd_rates():
    st.header("USD Conversion Rates")
    df = load_csv("USD Conversion Rates")
    child_buttons(df)

def ExternalSector():
    st.title("External Sector Dashboard")
    children = {
        "Exports": exports,
        "Imports": imports,
        "Foreign Employment": foreign_employment,
        "USD Conversion Rates": usd_rates
    }

    if "external_sector_child" not in st.session_state:
        st.session_state.external_sector_child = "Exports"

    child = st.sidebar.selectbox(
        "Select Data Category",
        list(children.keys()),
        index=list(children.keys()).index(st.session_state.external_sector_child)
    )
    st.session_state.external_sector_child = child
    children[child]()