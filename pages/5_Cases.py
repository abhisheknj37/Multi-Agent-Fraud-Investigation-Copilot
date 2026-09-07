import streamlit as st
from utils import setup, sidebar, header
setup("Cases"); sidebar(); header("Cases","Investigation Case Management","Track active investigations and analyst decisions.")
st.dataframe([
["CASE-001","TXN1003","C101","Account Takeover","Critical","Open"],
["CASE-002","TXN1098","C452","Card Fraud","High","Escalated"],
["CASE-003","TXN1201","C389","International Fraud","High","Open"],
["CASE-004","TXN1276","C782","Unusual Activity","Medium","Review"],
],columns=["CASE ID","TXN","CUSTOMER","TYPE","RISK","STATUS"],hide_index=True,width="stretch")
