import streamlit as st
from utils import setup, sidebar, header
setup("Network Analysis"); sidebar(); header("Network Analysis","Fraud Ring Detection","Explore relationships between customers, devices, IPs and merchants.")
st.markdown("### Relationship Graph")
st.graphviz_chart("""
graph LR
C101((Customer C101)) -- shared device --> DEV[Device DEV-X8F2]
C101 -- shared IP --> IP[IP 185.44.1.7]
C101 -- transaction --> M[TechWorld Electronics]
C389((Customer C389)) -- shared device --> DEV
C452((Customer C452)) -- shared IP --> IP
C782((Customer C782)) -- transaction --> M
""")
c1,c2,c3=st.columns(3)
c1.metric("Connected Accounts","6"); c2.metric("Shared Devices","2"); c3.metric("Fraud Ring Risk","89%")
st.markdown("### Network Findings")
st.warning("C101 is connected to 6 accounts through shared device/IP signals. 3 accounts have high-risk transactions.")
