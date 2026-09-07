import streamlit as st
from utils import setup, sidebar, header, tx_data
setup("Transactions"); sidebar(); header("Transactions","Transaction Monitoring","Search, filter and investigate financial activity.")
st.text_input("🔎 Search transactions, customers, devices, IPs, cases...", placeholder="TXN1003 / C101 / 185.44.1.7")
st.multiselect("Filters",["High Risk","Medium Risk","Low Risk","International","New Device"],default=["High Risk"])
st.dataframe(tx_data(), width="stretch", hide_index=True)
st.markdown("### Selected Transaction")
c1,c2,c3,c4=st.columns(4)
for c,label,value in zip([c1,c2,c3,c4],["Transaction","Customer","Amount","Location"],["TXN1003","C101","₹85,000","Delhi"]):
    c.metric(label,value)
if st.button("🔎 Investigate TXN1003", type="primary"):
    st.switch_page("pages/2_Investigations.py")
