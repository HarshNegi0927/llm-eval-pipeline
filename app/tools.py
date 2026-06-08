import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from langchain_core.tools import tool
from io import StringIO
import json

# Global dataframe store
df_store = {"df": None}

def load_dataframe(file):
    """Load uploaded CSV into global store"""
    df_store["df"] = pd.read_csv(file)
    return df_store["df"]

@tool
def get_dataframe_info(dummy: str = "") -> str:
    """Get basic info about the loaded dataframe - shape, columns, dtypes"""
    df = df_store["df"]
    if df is None:
        return "No dataframe loaded yet"
    
    info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "sample": df.head(3).to_string()
    }
    return json.dumps(info, default=str)

@tool
def get_statistics(column_name: str) -> str:
    """Get descriptive statistics for a specific column"""
    df = df_store["df"]
    if df is None:
        return "No dataframe loaded"
    if column_name not in df.columns:
        return f"Column '{column_name}' not found. Available: {list(df.columns)}"
    
    stats = df[column_name].describe().to_dict()
    return json.dumps(stats, default=str)

@tool
def find_correlations(dummy: str = "") -> str:
    """Find correlations between numeric columns"""
    df = df_store["df"]
    if df is None:
        return "No dataframe loaded"
    
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr().round(2).to_dict()
    return json.dumps(corr, default=str)

@tool
def detect_outliers(column_name: str) -> str:
    """Detect outliers in a column using IQR method"""
    df = df_store["df"]
    if df is None:
        return "No dataframe loaded"
    if column_name not in df.columns:
        return f"Column '{column_name}' not found"
    
    Q1 = df[column_name].quantile(0.25)
    Q3 = df[column_name].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df[(df[column_name] < Q1 - 1.5*IQR) | 
                  (df[column_name] > Q3 + 1.5*IQR)]
    
    return f"Found {len(outliers)} outliers in '{column_name}' out of {len(df)} rows"

@tool
def get_value_counts(column_name: str) -> str:
    """Get value counts for categorical columns"""
    df = df_store["df"]
    if df is None:
        return "No dataframe loaded"
    if column_name not in df.columns:
        return f"Column '{column_name}' not found"
    
    counts = df[column_name].value_counts().head(10).to_dict()
    return json.dumps(counts, default=str)

# Export all tools as list
analysis_tools = [
    get_dataframe_info,
    get_statistics,
    find_correlations,
    detect_outliers,
    get_value_counts
]