import streamlit as st
from utils import setup, sidebar, header
setup("AI Copilot"); sidebar(); header("AI Investigation Copilot","Ask questions about a transaction","Evidence-grounded analyst assistant.")
if "chat" not in st.session_state: st.session_state.chat=[]
for role,msg in st.session_state.chat:
    with st.chat_message(role): st.write(msg)
for q in ["Why is TXN1003 suspicious?","Show the strongest evidence","Is this an account takeover?","Explain the risk score"]:
    if st.button(q): st.session_state.chat += [("user",q),("assistant","TXN1003 is high risk because of amount deviation, new location, unknown device, high-risk IP, transaction velocity and links to other accounts. The strongest evidence is the combination of independent behavioral and network signals.")]; st.rerun()
prompt=st.chat_input("Ask anything about this transaction...")
if prompt:
    st.session_state.chat += [("user",prompt),("assistant","Based on the available evidence, the case remains high risk. I recommend manual review and escalation before any irreversible action.")]; st.rerun()
