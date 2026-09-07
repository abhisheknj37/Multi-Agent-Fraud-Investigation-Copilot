import streamlit as st
from utils import setup, sidebar, header
setup("Reports"); sidebar(); header("Reports","Investigation Reports","Audit-ready evidence-backed reports.")
st.markdown("### CASE-001 Investigation Report")
st.markdown('<div class="card"><b>Verdict:</b> High Risk<br><b>Score:</b> 91/100<br><b>Confidence:</b> 98%<br><br><b>Evidence:</b><br>• 7 transactions in 5 minutes<br>• 5.2× normal spending<br>• New Delhi location<br>• Unknown device<br>• High-risk IP<br>• Shared device network</div>',unsafe_allow_html=True)
if st.button("📄 Generate Report"): st.success("Report generated successfully.")
