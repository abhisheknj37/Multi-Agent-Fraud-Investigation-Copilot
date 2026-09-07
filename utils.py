import streamlit as st
import pandas as pd

def setup(title):
    st.set_page_config(page_title=title, page_icon="🛡️", layout="wide")
    st.markdown("""
    <style>
    .stApp{background:#06111f;color:#e8eef7}
    [data-testid="stSidebar"]{background:#071525;border-right:1px solid #17304c}
    .block-container{padding-top:1.2rem}
    .metric{background:#0b1b2d;border:1px solid #1c3854;border-radius:10px;padding:18px;min-height:105px}
    .metric-value{font-size:28px;font-weight:750}.delta{color:#43d39e;font-size:12px;margin-top:8px}
    .card{background:#0b1b2d;border:1px solid #1c3854;border-radius:10px;padding:18px;margin-bottom:12px}
    .risk-high{color:#ff5b6e;font-weight:800}.risk-med{color:#ffc533;font-weight:800}.risk-low{color:#43d39e;font-weight:800}
    .hero{background:linear-gradient(135deg,#0b1d32,#0a1423);border:1px solid #21415f;border-radius:12px;padding:20px}
    div.stButton>button{border-radius:7px}
    </style>
    """, unsafe_allow_html=True)

def sidebar():
    with st.sidebar:
        st.markdown("## 🛡️ FraudGuard AI")
        st.caption("Investigate. Understand. Prevent.")
        st.markdown("---")
        pages = {
            "🏠 Dashboard":"app.py",
            "💳 Transactions":"pages/1_Transactions.py",
            "🔎 Investigations":"pages/2_Investigations.py",
            "🕸️ Network Analysis":"pages/3_Network_Analysis.py",
            "🤖 AI Copilot":"pages/4_AI_Copilot.py",
            "📁 Cases":"pages/5_Cases.py",
            "📄 Reports":"pages/6_Reports.py",
            "🔔 Alerts":"pages/7_Alerts.py",
            "👥 Customers":"pages/8_Customers.py",
            "🏪 Merchants":"pages/9_Merchants.py",
            "📋 Audit Logs":"pages/10_Audit_Logs.py",
            "⚙️ Settings":"pages/11_Settings.py",
        }
        for label,path in pages.items():
            if st.button(label, width="stretch"):
                st.switch_page(path)
        st.markdown("---")
        st.caption("Analyst")
        st.write("fraud.team@bank.com")
        st.caption("● Online")

def header(title, subtitle="", description=""):
    st.markdown(f"## {title}")
    if subtitle: st.markdown(f"### {subtitle}")
    if description: st.caption(description)

def risk_badge(score):
    cls = "risk-high" if score >= 70 else "risk-med" if score >= 40 else "risk-low"
    label = "HIGH RISK" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f'<span class="{cls}">● {score}% {label}</span>'

def tx_data():
    return pd.DataFrame([
        ["TXN1003","C101","₹85,000","Delhi","91%","High Risk","Investigate"],
        ["TXN1098","C452","₹72,000","Mumbai","87%","High Risk","Investigate"],
        ["TXN1201","C389","₹45,500","Dubai","82%","High Risk","Investigate"],
        ["TXN1276","C782","₹12,000","Bengaluru","45%","Medium","Investigate"],
        ["TXN1302","C671","₹2,500","Bengaluru","12%","Low","Clear"],
    ], columns=["TXN ID","CUSTOMER","AMOUNT","LOCATION","RISK","STATUS","ACTION"])
