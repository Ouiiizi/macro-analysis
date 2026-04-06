import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats
import re

from sector_data_load import RealSector, ExternalSector, PriceChanges, PublicFinances, NepseLive
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def show_overview():
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h1 style="font-size: 48px; border-bottom: none;">Macroeconomic Data Archive</h1>
        <p style="font-family: 'Courier New', Courier, monospace; font-size: 18px; color: #5a5a5a;">Centralized Repository & Statistical Projections</p>
    </div>
    <hr style="margin-bottom: 40px; border-top: 1px solid #1c1c1c;">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown("""
        ### I. The Meaning of Macroeconomics
        Macroeconomics is the branch of economics that studies the behavior, structure, and performance of an economy as a whole. Rather than focusing on individual markets or consumers, it examines large-scale aggregate factors—such as inflation, price levels, rate of economic growth, national income, gross domestic product (GDP), and changes in employment.
        
        <br>

        ### II. The Importance of Economic Literacy
        Understanding macroeconomic indicators provides a critical, high-level view of economic health. It allows policymakers to formulate monetary and fiscal policies, assists businesses in making strategic investment decisions, and enables citizens to comprehend the broader forces affecting their personal finances. In an interconnected global economy, tracking these factors is absolutely vital for forecasting future stability and commerce.
        
        <br>

        ### III. Purpose of this Archive
        This unified repository was constructed to serve as a formal modern archive for important economic data records. By centralizing datasets across **Real Sectors, External Sectors, Public Finances, and Price Changes**, we aim to provide a streamlined, distraction-free tool for researchers and analysts. 
        
        Furthermore, the integrated statistical regression and projection features empower users to not only observe historical trends but mathematically extrapolate future economic trajectories in the context of **Federal Democratic Republic of Nepal**.
        """, unsafe_allow_html=True)

if "show_intro" not in st.session_state:
    st.session_state.show_intro = True

if st.session_state.show_intro:
    show_overview()
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        st.write(" ") 
        if st.button("↑ ENTER ARCHIVE", use_container_width=True):
            st.session_state.show_intro = False
            st.rerun()
else:

    with st.sidebar:
        parent = option_menu(
            menu_title="Archive Index",
            options=["Real Sector", "External Sector", "Price Changes", "Public Finances", "Live Stock Market (NEPSE)"],
            icons=['building', 'globe', 'tag', 'bank', 'graph-up-arrow'],
            menu_icon="archive",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#fdfbf7", "border-radius": "0px", "border": "1px solid #1c1c1c"},
                "icon": {"color": "#1c1c1c", "font-size": "18px"}, 
                "nav-link": {"font-family": "Courier New, Courier, monospace", "font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#f4f0ec", "color": "#1c1c1c", "border-radius": "0px"},
                "nav-link-selected": {"background-color": "#1c1c1c", "color": "#fdfbf7", "font-weight": "bold"},
            }
        )

    if parent == "Real Sector":
        RealSector.RealSector()
    elif parent == "External Sector":
        ExternalSector.ExternalSector()
    elif parent == "Price Changes":
        PriceChanges.PriceChanges()
    elif parent == "Public Finances":
        PublicFinances.PublicFinances()
    elif parent == "Live Stock Market (NEPSE)":
        NepseLive.NepseLive()
