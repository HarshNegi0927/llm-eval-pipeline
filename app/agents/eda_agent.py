from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from tools import df_store
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# EDA Tools
@tool
def get_basic_info(dummy: str = "") -> str:
    """Get shape, columns, dtypes, missing values of dataframe"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict()
    }
    return json.dumps(info, default=str)

@tool
def get_descriptive_stats(dummy: str = "") -> str:
    """Get descriptive statistics for all numeric columns"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    stats = df.describe().round(2).to_dict()
    return json.dumps(stats, default=str)

@tool
def detect_all_outliers(dummy: str = "") -> str:
    """Detect outliers in all numeric columns using IQR"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_report = {}
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
        outlier_report[col] = {
            "outlier_count": len(outliers),
            "outlier_percentage": round(len(outliers)/len(df)*100, 2)
        }
    
    return json.dumps(outlier_report, default=str)

@tool
def get_correlations(dummy: str = "") -> str:
    """Get correlation matrix for numeric columns"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr().round(2).to_dict()
    return json.dumps(corr, default=str)

@tool
def get_categorical_summary(dummy: str = "") -> str:
    """Get value counts for all categorical columns"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    cat_cols = df.select_dtypes(include=['object']).columns
    summary = {}
    
    for col in cat_cols:
        summary[col] = {
            "unique_values": df[col].nunique(),
            "top_5": df[col].value_counts().head(5).to_dict()
        }
    
    return json.dumps(summary, default=str)

eda_tools = [
    get_basic_info,
    get_descriptive_stats,
    detect_all_outliers,
    get_correlations,
    get_categorical_summary
]

llm_with_tools = llm.bind_tools(eda_tools)

def run_eda_agent(query: str) -> str:
    """EDA Agent — analyzes data structure, stats, outliers, correlations"""
    
    system = """You are an Expert EDA (Exploratory Data Analysis) Agent.
    
Your job:
1. Call get_basic_info first ALWAYS
2. Then get_descriptive_stats
3. Then detect_all_outliers
4. Then get_correlations
5. Then get_categorical_summary

After collecting all info, provide:
- Data Quality Report (missing values, outliers)
- Key Statistical Findings
- Important Patterns & Correlations
- Data Health Score (out of 10)

Be specific with numbers. Format response clearly."""

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=query)
    ]
    
    for _ in range(10):
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_input = tool_call["args"]
                
                selected_tool = next(
                    (t for t in eda_tools if t.name == tool_name), None
                )
                
                tool_result = selected_tool.invoke(tool_input) if selected_tool else "Tool not found"
                
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"]
                    )
                )
        else:
            return response.content
    
    return "EDA Analysis Complete"