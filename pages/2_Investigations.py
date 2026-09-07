import streamlit as st
from utils import setup, sidebar, header, risk_badge
setup("Investigation"); sidebar(); header("Transaction Investigation","TXN1003 — ₹85,000","Human-in-the-loop investigation workspace.")
st.markdown('<div class="hero"><h2>🔴 HIGH RISK</h2><h1>91%</h1><p>Confidence: 98% • Manual investigation recommended</p></div>',unsafe_allow_html=True)
a,b=st.columns([2,1])
with a:
    st.markdown("### Transaction Details")
    st.json({"Transaction ID":"TXN1003","Customer ID":"C101","Amount":"₹85,000","Merchant":"TechWorld Electronics","Location":"Delhi","Date & Time":"Dec 10, 2024 10:12 AM","Device ID":"DEV-X8F2","IP Address":"185.44.1.7","Payment Method":"Credit Card ****4582"})
with b:
    st.markdown("### Risk Score"); st.metric("Risk","91%","HIGH RISK"); st.progress(.91)
st.markdown("### Agent Analysis")
for title,text in [
("🔍 Transaction Pattern Agent","7 transactions in the last 5 minutes; amount is 5.2× the customer's normal spending; new geography."),
("👤 Customer History Agent","C101 normally transacts in Bengaluru with an average ticket of ₹16,300. Delhi is new."),
("🧠 Risk Scoring Agent","Independent signals converge on high risk with 98% confidence.")]:
    st.markdown(f'<div class="card"><h4>{title}</h4>{text}</div>',unsafe_allow_html=True)
st.markdown("### Evidence Trail")
for x in ["Amount anomaly","Unusual location","Unknown device","High-risk IP","Shared device with 6 other accounts","Velocity anomaly"]:
    st.write("✓",x)
st.info("Quick Insight: The transaction shows multiple high-risk indicators including amount, geography, device, IP and velocity anomalies.")
st.markdown("### Analyst Actions")
c1,c2,c3=st.columns(3)
if c1.button("✅ Mark as Clear", width="stretch"): st.success("Transaction marked clear.")
if c2.button("🚨 Confirm Fraud", width="stretch"): st.error("Transaction confirmed as fraud.")
if c3.button("↗ Escalate", width="stretch"): st.warning("Case escalated.")
