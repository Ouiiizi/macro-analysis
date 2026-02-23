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
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Public Finances")
CSV_FILES = {
    "Government Budget Operations": "GovNBudgetOperations.csv",
    "GoN Revenue": "GoNrevenue.csv",
    "Debt Ownership": "DebtOwnership.csv",
    "Net Domestic Borrowings": "NetDomesticBorrowingsGON.csv"
}

# -----------------------------
# Load CSV and melt into long format
# -----------------------------
def load_csv(child_name):
    file_path = os.path.join(DATA_DIR, CSV_FILES[child_name])
    
    if child_name == "Government Budget Operations":
        df = pd.read_csv(file_path)
        category_col = df.columns[0]
        df_long = df.melt(id_vars=[category_col], var_name='Year', value_name='Value')
        df_long.rename(columns={category_col: "Category"}, inplace=True)
        
    elif child_name == "GoN Revenue":
        df = pd.read_csv(file_path, skiprows=1)
        # Handle multi-line header/metadata
        if "Annual" in str(df.iloc[0]):
            df = df.iloc[1:].reset_index(drop=True)
        category_col = df.columns[0]
        # Drop columns with all NaN values (like "Unnamed: 2")
        df = df.dropna(axis=1, how='all')
        df_long = df.melt(id_vars=[category_col], var_name='Year', value_name='Value')
        df_long.rename(columns={category_col: "Category"}, inplace=True)
        
    elif child_name == "Debt Ownership":
        df = pd.read_csv(file_path)
        if 'S.N.' in df.columns:
            df = df.drop(columns=['S.N.'])
        # Skip metadata row if present
        if "Mid-Jul" in str(df.iloc[0]):
             df = df.iloc[1:].reset_index(drop=True)
        category_col = df.columns[0]
        df_long = df.melt(id_vars=[category_col], var_name='Year', value_name='Value')
        df_long.rename(columns={category_col: "Category"}, inplace=True)
        
    elif child_name == "Net Domestic Borrowings":
        df = pd.read_csv(file_path)
        # The file has a structured format:
        # Col 0 (Headings): empty or A, B, C
        # Col 1 (Labels): Gross Borrowings, T-Bills..., Payments, T-Bills...
        # Col 2-4: Years
        
        # Clean columns: drop 'how=all' columns (usually the empty space between labels and numbers)
        df_clean = df.copy()
        # Find labels in Col 0 or Col 1
        # Fill NaN in the first two columns to make string manipulation easier
        df_clean.iloc[:, 0] = df_clean.iloc[:, 0].fillna('')
        df_clean.iloc[:, 1] = df_clean.iloc[:, 1].fillna('')
        
        # Merge the first two columns to capture full label (e.g., 'A Gross Borrowings')
        df_clean['Category'] = df_clean.iloc[:, 0].astype(str) + " " + df_clean.iloc[:, 1].astype(str)
        df_clean['Category'] = df_clean['Category'].str.strip()
        
        # Track main sections to prefix sub-items
        current_section = ""
        new_categories = []
        for cat in df_clean['Category']:
            if cat in ["Gross Borrowings", "Payments", "Net Domestic Borrowings (NDB) (A-B)"]:
                current_section = cat
                new_categories.append(cat)
            elif current_section and cat:
                new_categories.append(f"{current_section} - {cat}")
            else:
                new_categories.append(cat)
        
        df_clean['Category'] = new_categories
        
        # Columns with numbers (identify years)
        value_cols = [col for col in df_clean.columns if any(yr in col for yr in ["2022", "2023", "2024", "2025"])]
        
        df_long = df_clean.melt(id_vars=['Category'], value_vars=value_cols, var_name='Year', value_name='Value')

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
            chart_data = df[df['Category'] == category].set_index('Year')[['Value']]
            chart_data.columns = [category]
        else:
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
        st.write(" ") 
        run_reg = st.button("Run Regression", use_container_width=True)

    if run_reg:
        regression_projection(df, selected_category)

    st.write(" ")
    with st.expander(" View Raw Data Table"):
        st.dataframe(df[df['Category'] == selected_category], use_container_width=True)

# -----------------------------
# Child pages
# -----------------------------
def budget_ops():
    st.header("Government Budget Operations")
    df = load_csv("Government Budget Operations")
    child_buttons(df)

def gon_revenue():
    st.header("GoN Revenue Analysis")
    df = load_csv("GoN Revenue")
    child_buttons(df)

def debt_ownership():
    st.header("Domestic Debt Ownership")
    df = load_csv("Debt Ownership")
    child_buttons(df)

def net_borrowing():
    st.header("Net Domestic Borrowings")
    df = load_csv("Net Domestic Borrowings")
    child_buttons(df)

# -----------------------------
# Main PublicFinances
# -----------------------------
def PublicFinances():
    st.title("Public Finances Dashboard")
    children = {
        "Budget Operations": budget_ops,
        "GoN Revenue": gon_revenue,
        "Debt Ownership": debt_ownership,
        "Net Borrowings": net_borrowing
    }

    if "public_finances_child" not in st.session_state:
        st.session_state.public_finances_child = "Budget Operations"

    child = st.sidebar.selectbox(
        "Select Data Category",
        list(children.keys()),
        index=list(children.keys()).index(st.session_state.public_finances_child)
    )
    st.session_state.public_finances_child = child
    children[child]()
