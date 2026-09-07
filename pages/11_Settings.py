import streamlit as st
from utils import setup, sidebar, header
setup("Settings"); sidebar(); header("Settings","System Configuration","Configure investigation and analyst preferences.")
st.checkbox("Human approval required before action",True)
st.checkbox("Record full evidence trail",True)
st.checkbox("Enable AI investigation summaries",True)
st.slider("High-risk threshold",50,100,70)
st.selectbox("Default report format",["PDF","JSON","CSV"])
st.success("Settings saved locally for this prototype.")
