from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from tools import df_store
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# Global chart store
chart_store = {"charts": []}

@tool
def create_distribution_charts(dummy: str = "") -> str:
    """Create distribution charts for all numeric columns"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in numeric_cols[:4]:
        fig = px.histogram(
            df, x=col,
            title=f"Distribution of {col}",
            color_discrete_sequence=["#6366f1"]
        )
        chart_store["charts"].append({"name": f"dist_{col}", "fig": fig})
        charts.append(f"Created histogram for {col}")
    
    return json.dumps({"created": charts})

@tool
def create_correlation_heatmap(dummy: str = "") -> str:
    """Create correlation heatmap for numeric columns"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr().round(2)
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale="RdBu",
        text=corr.values.round(2),
        texttemplate="%{text}",
    ))
    fig.update_layout(title="Correlation Heatmap")
    chart_store["charts"].append({"name": "correlation_heatmap", "fig": fig})
    
    return "Correlation heatmap created"

@tool
def create_categorical_charts(dummy: str = "") -> str:
    """Create bar charts for categorical columns"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    charts = []
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    for col in cat_cols[:3]:
        value_counts = df[col].value_counts().reset_index()
        value_counts.columns = [col, 'count']
        
        fig = px.bar(
            value_counts, x=col, y='count',
            title=f"{col} — Value Counts",
            color='count',
            color_continuous_scale="viridis"
        )
        chart_store["charts"].append({"name": f"bar_{col}", "fig": fig})
        charts.append(f"Created bar chart for {col}")
    
    return json.dumps({"created": charts})

@tool
def create_trend_chart(date_column: str) -> str:
    """Create time series trend chart if date column exists"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    if date_column not in df.columns:
        return f"Column '{date_column}' not found"
    
    try:
        df_temp = df.copy()
        df_temp[date_column] = pd.to_datetime(df_temp[date_column])
        
        numeric_cols = df_temp.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return "No numeric columns for trend"
        
        target_col = numeric_cols[0]
        trend_df = df_temp.groupby(date_column)[target_col].sum().reset_index()
        
        fig = px.line(
            trend_df, x=date_column, y=target_col,
            title=f"{target_col} Over Time",
            markers=True,
            color_discrete_sequence=["#6366f1"]
        )
        chart_store["charts"].append({"name": "trend_chart", "fig": fig})
        
        return f"Trend chart created for {target_col} over {date_column}"
    
    except Exception as e:
        return f"Error creating trend: {str(e)}"

@tool
def create_scatter_plot(columns: str) -> str:
    """Create scatter plot. Pass two column names separated by comma e.g. 'col1,col2'"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    try:
        cols = [c.strip() for c in columns.split(",")]
        if len(cols) < 2:
            return "Need two columns separated by comma"
        
        x_col, y_col = cols[0], cols[1]
        
        if x_col not in df.columns or y_col not in df.columns:
            return f"Columns not found. Available: {list(df.columns)}"
        
        fig = px.scatter(
            df, x=x_col, y=y_col,
            title=f"{x_col} vs {y_col}",
            trendline="ols",
            color_discrete_sequence=["#6366f1"]
        )
        chart_store["charts"].append({"name": f"scatter_{x_col}_{y_col}", "fig": fig})
        
        return f"Scatter plot created: {x_col} vs {y_col}"
    
    except Exception as e:
        return f"Error: {str(e)}"

viz_tools = [
    create_distribution_charts,
    create_correlation_heatmap,
    create_categorical_charts,
    create_trend_chart,
    create_scatter_plot
]

llm_with_tools = llm.bind_tools(viz_tools)

def run_viz_agent(query: str) -> str:
    """Viz Agent — creates all relevant charts and visualizations"""
    
    system = """You are an Expert Data Visualization Agent.

Your job:
1. ALWAYS call create_distribution_charts first
2. ALWAYS call create_correlation_heatmap
3. ALWAYS call create_categorical_charts
4. If date column exists, call create_trend_chart
5. Create scatter plot for top 2 correlated numeric columns

Then summarize:
- What charts were created
- Key visual patterns found
- Most interesting insight from visualizations"""

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
                    (t for t in viz_tools if t.name == tool_name), None
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
    
    return "Visualization Complete"

def get_charts():
    """Return all generated charts"""
    return chart_store["charts"]

def clear_charts():
    """Clear chart store"""
    chart_store["charts"] = []