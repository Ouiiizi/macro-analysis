import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats
import re

from sector_data_load import RealSector, ExternalSector, PriceChanges, PublicFinances

st.set_page_config(layout="wide")

parent = st.sidebar.selectbox("Select Macroeconomic Sector", ["Real Sector", "External Sector", "Price Changes", "Public Finances"])


if parent == "Real Sector":
    RealSector.RealSector()
elif parent == "External Sector":
    ExternalSector.ExternalSector()
elif parent == "Price Changes":
    PriceChanges.PriceChanges()
elif parent == "Public Finances":
    PublicFinances.PublicFinances()
