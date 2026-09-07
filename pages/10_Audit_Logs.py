import streamlit as st
from utils import setup, sidebar, header
setup("Audit Logs"); sidebar(); header("Audit Logs","Traceable Investigation Activity","Every AI and analyst action is recorded.")
st.dataframe([
["10:24:11","CASE-001","Transaction Agent","Completed","7 anomalies"],
["10:24:14","CASE-001","Customer Agent","Completed","Baseline deviation"],
["10:24:17","CASE-001","Risk Agent","Completed","91% risk"],
["10:24:21","CASE-001","Report Agent","Completed","Evidence report"],
["10:26:03","CASE-001","Analyst","Escalated","Manual review"],
],columns=["TIME","CASE","ACTOR","ACTION","DETAIL"],hide_index=True,width="stretch")
