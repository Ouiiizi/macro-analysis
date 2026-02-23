import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats
import re

from sector_data_load import RealSector,ExpenditureSector,PriceChanges,PublicFinances

st.set_page_config(layout="wide")

parent = st.sidebar.selectbox("Select Macroeconomic Sector", ["Real Sector", "Expenditure Sector", "Price Changes", "Public Finances"])


if parent == "Real Sector":
    RealSector.RealSector()