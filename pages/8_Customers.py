import streamlit as st
from utils import setup, sidebar, header
setup("Customers"); sidebar(); header("Customers","Customer Risk Profiles","Behavioral baselines and historical context.")
st.dataframe([
["C101","High","₹16,300","Bengaluru","6","2"],
["C452","High","₹12,400","Mumbai","4","1"],
["C389","High","₹8,900","Bengaluru","3","0"],
["C782","Medium","₹7,200","Bengaluru","4","0"],
["C671","Low","₹2,100","Bengaluru","3","0"],
],columns=["CUSTOMER","RISK","AVG TRANSACTION","USUAL LOCATION","AVG DAILY TXNS","DISPUTES"],hide_index=True,width="stretch")
