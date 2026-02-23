import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import os
import numpy as np

# Custom CSS for premium look
st.markdown("""
<style>
    .css-1d391kg {background-color: #0e1117; color: #e0e0e7;}
    .stButton>button {background-color: #4a90e2; color: white; border-radius: 8px;}
    .stSelectbox {background-color: #1e1e1e; color: #e0e0e7;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data directory
# -----------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "External Sector")
CSV_FILES = {
    "Exports": "Exports.csv",
    "Imports": "Imports.csv",
    "Foreign Employment": "ForeignEmploymentCount.csv",
    "USD Conversion Rates": "USDConversionRates.csv"
}

# -----------------------------
# Load CSV and melt into long format
# -----------------------------
def load_csv(child_name):
    file_path = os.path.join(DATA_DIR, CSV_FILES[child_name])
    
    # Handle files with multi-line headers or S.N. columns
    if child_name in ["Exports", "Imports", "Foreign Employment"]:
        df = pd.read_csv(file_path)
        # Drop S.N. column if it exists
        if 'S.N.' in df.columns:
            df = df.drop(columns=['S.N.'])
        elif 'S.No.' in df.columns:
            df = df.drop(columns=['S.No.'])
        
        # Skip the meta-data row (like "Annual, Annual") if present
        if df.iloc[0].isna().any() or (df.iloc[0] == "Annual").any():
            df = df.iloc[1:].reset_index(drop=True)
            
        category_col = df.columns[0]
        df_long = df.melt(id_vars=[category_col], var_name='Year', value_name='Value')
        df_long.rename(columns={category_col: "Category"}, inplace=True)
        
    else: # USD Conversion Rates
        df = pd.read_csv(file_path, skiprows=1)
        # headers are Buying, Selling, Middle. First col is Year.
        df.columns = [col.strip() if 'Unnamed' not in col else 'Year' for col in df.columns]
        df_long = df.melt(id_vars=['Year'], var_name='Category', value_name='Value')
        # Remove 'Middle' category as requested
        df_long = df_long[df_long['Category'] != 'Middle']

    # Clean numbers
    df_long['Value'] = pd.to_numeric(df_long['Value'].astype(str).str.replace(",", ""), errors='coerce')
    df_long = df_long.dropna(subset=['Value'])
    return df_long

# -----------------------------
# Graphing
# -----------------------------
def show_graph(df, category=None):
    """Render a clean, interactive Streamlit line chart for combined or individual data."""
    title = f"{category} Trend Over Time" if category else "All Categories Trend Over Time"
    st.subheader(f"📈 {title}")
    
    try:
        if category:
            # Filter for one category, pivot to get Year as index
            chart_data = df[df['Category'] == category].set_index('Year')[['Value']]
            chart_data.columns = [category]
        else:
            # Pivot all sectors: Year as index, Categories as columns
            chart_data = df.pivot(index='Year', columns='Category', values='Value')
            
        st.line_chart(chart_data, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render chart: {e}")

# -----------------------------
# Regression + Projection
# -----------------------------
def regression_projection(df, category):
    """Simple linear regression with a projection point."""
    df_cat = df[df['Category'] == category]
    if df_cat.empty:
        st.warning(f"No data found for {category}")
        return
        
    y_values = df_cat['Value'].values
    years = df_cat['Year'].tolist()
    x_indices = list(range(len(y_values)))

    # Calculate regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_indices, y_values)
    
    st.markdown(f"## Analysis: {category}")
    
    col1, col2 = st.columns(2)
    col1.write(f"**Confidence (R-squared):** {r_value**2:.3f}")
    
    # Projection for next step
    next_x = len(x_indices)
    next_val = slope * next_x + intercept
    col2.write(f"**Projected value for next step:** {next_val:,.2f}")

    # Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(years, y_values, 'bo', label='Actual Data', markersize=8)
    ax.plot(years, [slope * i + intercept for i in x_indices], 'r-', label='Trend Line', linewidth=2)
    
    # Add the projection point (green dot)
    next_year = "Next Period" 
    ax.plot(next_year, next_val, 'go', markersize=12, label='Projection')
    
    ax.set_title(f"Regression & Projection: {category}", fontsize=14)
    ax.set_ylabel("Value")
    plt.xticks(rotation=45)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig, use_container_width=True)
    plt.close()

# -----------------------------
# UI Logic
# -----------------------------
def child_buttons(df):
    """Interactive UI for data visualization and analysis."""
    categories = df['Category'].unique().tolist()
    
    # 1. MAIN TREND VISUALIZATION
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
            chart_data = df[df['Category'].isin(selected_sectors)].pivot(index='Year', columns='Category', values='Value')
            st.line_chart(chart_data, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering chart: {e}")
    else:
        st.warning("Please select at least one category to visualize.")

    st.markdown("---")
    
    # 2. DETAILED ANALYSIS SECTION
    st.subheader("🔍 Detailed Analysis")
    
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_category = st.selectbox("Select Category for In-depth Tools", categories)
    with col_btn:
        st.write(" ") # alignment spacer
        run_reg = st.button("Run Regression", use_container_width=True)

    if run_reg:
        regression_projection(df, selected_category)

    st.write(" ")
    with st.expander(" View Raw Data Table"):
        st.dataframe(df[df['Category'] == selected_category], use_container_width=True)

# -----------------------------
# Child pages
# -----------------------------
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

# -----------------------------
# Main ExternalSector
# -----------------------------
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