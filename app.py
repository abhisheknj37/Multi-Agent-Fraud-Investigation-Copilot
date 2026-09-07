import streamlit as st
from utils import setup, sidebar, header, risk_badge, tx_data

setup("FraudGuard AI")
sidebar()
header("Dashboard", "Welcome back, Analyst", "Here's what's happening with fraud investigations today.")

cols = st.columns(4)
metrics = [("50,000","Total Transactions","↑ 12% from last week"),
           ("1,284","Fraud Alerts","↑ 8% from last week"),
           ("247","High Risk Transactions","↑ 24% from last week"),
           ("38","Detected Fraud Rings","↑ 5% from last week")]
for c,(a,b,d) in zip(cols,metrics):
    with c:
        st.markdown(f'<div class="metric"><div class="metric-value">{a}</div><div>{b}</div><div class="delta">{d}</div></div>', unsafe_allow_html=True)

st.markdown("### Recent Transactions")
df = tx_data()
st.dataframe(df, width="stretch", hide_index=True)

left,right = st.columns(2)
with left:
    st.markdown("### Fraud Trends")
    st.line_chart({"Total Transactions":[1100,1350,1600,1900,2300,2800,3200,3600],
                   "Fraud Alerts":[250,300,340,410,500,610,720,900]})
with right:
    st.markdown("### Risk Distribution")
    st.bar_chart({"Alerts":[247,403,634]}, horizontal=True)

st.markdown("### Fraud Network Analysis")
st.info("C101 is connected to C389, C452 and C782 through a shared device, IP address and merchant. Open Network Analysis for the full relationship graph.")

st.markdown("### AI Investigation Copilot")
st.success("Ready to investigate suspicious transactions and explain risk signals.")
