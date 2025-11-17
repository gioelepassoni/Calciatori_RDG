import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Football Stats Manager", layout="wide")
st.title("⚽ Football Stats Manager")

# Default file path
default_file = "NUOVO_CALCIATORI_RDG_with_player_name_fixed_dropdown.xlsx"

# Check if file exists
try:
    players_df = pd.read_excel(default_file, sheet_name="Players")
    matches_df = pd.read_excel(default_file, sheet_name="Matches")
    lineups_df = pd.read_excel(default_file, sheet_name="Team Lineups")
    st.success("Loaded default Excel file from GitHub repo.")
except FileNotFoundError:
    st.error("Default Excel file not found. Please upload one.")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    players_df = pd.read_excel(uploaded_file, sheet_name="Players")
    matches_df = pd.read_excel(uploaded_file, sheet_name="Matches")
    lineups_df = pd.read_excel(uploaded_file, sheet_name="Team Lineups")

