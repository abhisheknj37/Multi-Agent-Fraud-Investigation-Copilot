import streamlit as st
from utils import setup, sidebar, header
setup("Merchants"); sidebar(); header("Merchants","Merchant Risk Intelligence","Monitor merchant-level fraud signals.")
st.dataframe([
["TechWorld Electronics","Electronics","High","₹85,000","14"],
["Global Crypto Exchange","Crypto","Critical","₹51,000","27"],
["Amazon","Retail","Low","₹2,400","0"],
["Uber","Transport","Low","₹800","0"],
],columns=["MERCHANT","CATEGORY","RISK","LARGEST TXN","ALERTS"],hide_index=True,width="stretch")
