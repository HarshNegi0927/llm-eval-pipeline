from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from tools import df_store
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error
from sklearn.cluster import KMeans

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

@tool
def detect_problem_type(dummy: str = "") -> str:
    """Detect whether dataset is suitable for classification, regression, or clustering"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    suggestions = []
    
    for col in cat_cols:
        unique = df[col].nunique()
        if 2 <= unique <= 10:
            suggestions.append({
                "target": col,
                "type": "classification",
                "unique_classes": unique
            })
    
    for col in numeric_cols:
        if col.lower() not in ['id', 'index']:
            suggestions.append({
                "target": col,
                "type": "regression",
                "range": f"{df[col].min():.2f} to {df[col].max():.2f}"
            })
    
    suggestions.append({
        "type": "clustering",
        "note": "Group similar records — no target needed"
    })
    
    return json.dumps(suggestions[:5], default=str)

@tool
def train_classification_model(target_column: str) -> str:
    """Train a classification model on the given target column"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    if target_column not in df.columns:
        return f"Column '{target_column}' not found"
    
    try:
        df_clean = df.copy()
        
        # Encode categoricals
        le = LabelEncoder()
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = le.fit_transform(df_clean[col].astype(str))
        
        X = df_clean.drop(columns=[target_column])
        y = df_clean[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_acc = accuracy_score(y_test, rf.predict(X_test))
        
        # Feature importance
        feat_imp = dict(zip(
            X.columns,
            rf.feature_importances_.round(3)
        ))
        top_features = dict(sorted(feat_imp.items(), key=lambda x: x[1], reverse=True)[:5])
        
        result = {
            "model": "Random Forest Classifier",
            "target": target_column,
            "accuracy": f"{rf_acc*100:.2f}%",
            "train_size": len(X_train),
            "test_size": len(X_test),
            "top_features": top_features
        }
        
        return json.dumps(result, default=str)
    
    except Exception as e:
        return f"Error training model: {str(e)}"

@tool
def train_regression_model(target_column: str) -> str:
    """Train a regression model on the given target column"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    if target_column not in df.columns:
        return f"Column '{target_column}' not found"
    
    try:
        df_clean = df.copy()
        
        le = LabelEncoder()
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = le.fit_transform(df_clean[col].astype(str))
        
        X = df_clean.drop(columns=[target_column])
        y = df_clean[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_r2 = r2_score(y_test, rf.predict(X_test))
        rf_rmse = np.sqrt(mean_squared_error(y_test, rf.predict(X_test)))
        
        feat_imp = dict(zip(
            X.columns,
            rf.feature_importances_.round(3)
        ))
        top_features = dict(sorted(feat_imp.items(), key=lambda x: x[1], reverse=True)[:5])
        
        result = {
            "model": "Random Forest Regressor",
            "target": target_column,
            "r2_score": f"{rf_r2:.4f}",
            "rmse": f"{rf_rmse:.2f}",
            "train_size": len(X_train),
            "test_size": len(X_test),
            "top_features": top_features
        }
        
        return json.dumps(result, default=str)
    
    except Exception as e:
        return f"Error training model: {str(e)}"

@tool
def run_clustering(n_clusters: str = "3") -> str:
    """Run KMeans clustering on numeric columns"""
    df = df_store["df"]
    if df is None:
        return "No data loaded"
    
    try:
        n = int(n_clusters)
        numeric_df = df.select_dtypes(include=[np.number]).dropna()
        
        kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
        labels = kmeans.fit_predict(numeric_df)
        
        numeric_df = numeric_df.copy()
        numeric_df['cluster'] = labels
        
        cluster_summary = numeric_df.groupby('cluster').mean().round(2).to_dict()
        cluster_sizes = pd.Series(labels).value_counts().to_dict()
        
        result = {
            "n_clusters": n,
            "cluster_sizes": cluster_sizes,
            "cluster_profiles": cluster_summary,
            "inertia": round(kmeans.inertia_, 2)
        }
        
        return json.dumps(result, default=str)
    
    except Exception as e:
        return f"Error clustering: {str(e)}"

ml_tools = [
    detect_problem_type,
    train_classification_model,
    train_regression_model,
    run_clustering
]

llm_with_tools = llm.bind_tools(ml_tools)

def run_ml_agent(query: str) -> str:
    """ML Agent — detects problem type, trains models, reports metrics"""
    
    system = """You are an Expert ML Agent.

Your job:
1. Call detect_problem_type FIRST to understand the data
2. Based on results, train the most suitable model
3. For classification: call train_classification_model
4. For regression: call train_regression_model  
5. For clustering: call run_clustering

Then provide:
- Best Model Recommendation with reasoning
- Model Performance Metrics
- Top 5 Important Features
- Business Insights from the model

Be specific with numbers."""

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
                    (t for t in ml_tools if t.name == tool_name), None
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
    
    return "ML Analysis Complete"