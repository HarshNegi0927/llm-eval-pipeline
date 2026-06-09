import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import load_dataframe, df_store
from agents.orchestrator import run_multi_agent

st.set_page_config(
    page_title="Autonomous Data Analysis Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Autonomous Data Analysis Agent")
st.caption("Multi-Agent AI System — EDA + ML + Visualization")

# Initialize session state
if "query" not in st.session_state:
    st.session_state.query = ""
if "last_report" not in st.session_state:
    st.session_state.last_report = None
if "last_charts" not in st.session_state:
    st.session_state.last_charts = []

# Sidebar
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file:
        df = load_dataframe(uploaded_file)
        st.success(f"✅ Loaded: {df.shape[0]} rows, {df.shape[1]} cols")
        st.dataframe(df.head(), use_container_width=True)
    
    st.divider()
    st.markdown("### 🏗️ Agent Pipeline")
    st.markdown("""User Query
    ↓
Orchestrator
↓    ↓    ↓
EDA  ML  Viz
    ↓
Final Report""")

# Main area
if df_store["df"] is None:
    st.info("👈 Upload a CSV file to get started")
    st.stop()

df = df_store["df"]

# Quick stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", df.shape[0])
col2.metric("Columns", df.shape[1])
col3.metric("Missing Values", df.isnull().sum().sum())
col4.metric("Numeric Cols", len(df.select_dtypes(include='number').columns))

st.divider()

# Agent Query Section
st.subheader("🧠 Ask the Multi-Agent System")

# Example buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔍 Full Analysis"):
        st.session_state.query = "Do a complete analysis of this dataset"
with col2:
    if st.button("🤖 Train ML Model"):
        st.session_state.query = "Analyze data and train the best ML model"
with col3:
    if st.button("📊 Visualize Patterns"):
        st.session_state.query = "Find and visualize all key patterns in the data"

query = st.text_area(
    "Or type your question:",
    value=st.session_state.query,
    height=100,
    key="query_input",
    placeholder="e.g. Which city has highest revenue? What affects total price?"
)

# Sync session state
st.session_state.query = query

if st.button("🚀 Run Multi-Agent Analysis", type="primary"):
    if not st.session_state.query.strip():
        st.warning("Please enter a question!")
        st.stop()

    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    with st.spinner("Multi-Agent Pipeline Running..."):
        with status_col1:
            st.info("🎯 Orchestrator...")

        report, charts = run_multi_agent(st.session_state.query)

        # Save to session
        st.session_state.last_report = report
        st.session_state.last_charts = charts

        with status_col1:
            st.success("✅ Orchestrator")
        with status_col2:
            st.success("✅ EDA Agent")
        with status_col3:
            st.success("✅ ML Agent")
        with status_col4:
            st.success("✅ Viz Agent")

    # Clear query after run
    st.session_state.query = ""

# Show results if available
if st.session_state.last_report:
    st.divider()
    st.subheader("📋 Executive Report")
    st.markdown(st.session_state.last_report)

    if st.session_state.last_charts:
        st.divider()
        st.subheader("📊 Generated Visualizations")
        cols = st.columns(2)
        for i, chart in enumerate(st.session_state.last_charts):
            with cols[i % 2]:
                st.plotly_chart(chart["fig"], use_container_width=True)