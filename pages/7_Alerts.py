import streamlit as st
from utils import setup, sidebar, header
setup("Alerts"); sidebar(); header("Alerts","Fraud Alert Queue","Prioritized alerts requiring analyst attention.")
for title,detail in [
("🔴 Critical — TXN1003","₹85,000 • C101 • 91% risk • 7 transactions/5 min"),
("🔴 Critical — TXN1098","₹72,000 • C452 • 87% risk • new device"),
("🟠 High — TXN1201","₹45,500 • C389 • 82% risk • international"),
("🟡 Medium — TXN1276","₹12,000 • C782 • 45% risk")]:
    st.markdown(f'<div class="card"><h4>{title}</h4>{detail}</div>',unsafe_allow_html=True)
