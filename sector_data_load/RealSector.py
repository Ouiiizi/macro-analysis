import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import os
import numpy as np

st.set_page_config(page_title="Real Sector Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .css-1d391kg {background-color: #0e1117; color: #e0e0e7;}
    .stButton>button {background-color: #4a90e2; color: white; border-radius: 8px;}
    .stSelectbox {background-color: #1e1e1e; color: #e0e0e7;}
</style>
""", unsafe_allow_html=True)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "RealSector")
CSV_FILES = { 
    "GDP at Constant Prices": "GDPAtConstantPrices.csv",
    "GDP by Expenditure Category": "GDPByExpenditureCategory.csv",
    "Gross Domestic Savings": "GNDIandSavings.csv"
}

def load_csv(child_name):
    file_path = os.path.join(DATA_DIR, CSV_FILES[child_name])
    df = pd.read_csv(file_path, skiprows=1)
    df.columns = [col.strip() for col in df.columns]

 
    df_long = df.melt(id_vars=[df.columns[0]], var_name='Year', value_name='Value')
    df_long.rename(columns={df.columns[0]: "Category"}, inplace=True)
    
 
    df_long['Value'] = df_long['Value'].astype(str).str.replace(",", "").astype(float)
    return df_long

def show_graph(df, category=None):
    title = f"{category} Trend Over Time" if category else "All Categories Trend Over Time"
    st.subheader(f" {title}")
    try:
        if category:
            chart_data = df[df['Category'] == category].set_index('Year')[['Value']]
            
            chart_data.columns = [category]
        else:
            chart_data = df.pivot(index='Year', columns='Category', values='Value')
            
        st.line_chart(chart_data, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render chart: {e}")


def regression_projection(df, category):
    df_cat = df[df['Category'] == category]
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


def child_buttons(df):
    
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
       
            chart_data = df[df['Category'].isin(selected_sectors)].pivot(index='Year', columns='Category', values='Value')
            st.line_chart(chart_data, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering chart: {e}")
    else:
        st.warning("Please select at least one category to visualize.")

    st.markdown("---")
    
    st.subheader(" Detailed Analysis")
    
    col_sel, col_btn = st.columns([2, 1])
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



def gdp_cp():
    st.header("GDP at Constant Prices")
    df = load_csv("GDP at Constant Prices")
    child_buttons(df)

def gdp_expenditure():
    st.header("GDP by Expenditure Category")
    df = load_csv("GDP by Expenditure Category")
    child_buttons(df)

def gds():
    st.header("Gross Domestic Savings")
    df = load_csv("Gross Domestic Savings")
    child_buttons(df)


def RealSector():
    st.title("Real Sector Dashboard")
    children = {
        "GDP at Constant Prices": gdp_cp,
        "GDP by Expenditure Category": gdp_expenditure,
        "Gross Domestic Savings": gds
    }

    if "real_sector_child" not in st.session_state:
        st.session_state.real_sector_child = "GDP at Constant Prices"

    child = st.sidebar.selectbox(
        "Select Data Category",
        list(children.keys()),
        index=list(children.keys()).index(st.session_state.real_sector_child)
    )
    st.session_state.real_sector_child = child
    children[child]()