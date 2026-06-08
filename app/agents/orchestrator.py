from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
import os
from dotenv import load_dotenv

load_dotenv()

# Import all agents
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.eda_agent import run_eda_agent
from agents.ml_agent import run_ml_agent
from agents.viz_agent import run_viz_agent, get_charts, clear_charts

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# State definition
class AgentState(TypedDict):
    query: str
    eda_result: str
    ml_result: str
    viz_result: str
    final_report: str
    agents_to_run: list

# Node functions
def orchestrator_node(state: AgentState) -> AgentState:
    """Decides which agents to run based on query"""
    
    query = state["query"]
    
    system = """You are an Orchestrator Agent. Based on the user query, decide which agents to run.
    
Return ONLY a JSON like this:
{
    "agents": ["eda", "ml", "viz"],
    "reasoning": "why these agents"
}

Agent descriptions:
- eda: for data exploration, statistics, missing values, correlations
- ml: for predictions, model training, feature importance, clustering  
- viz: for charts, visualizations, trends, patterns

Always include eda. Add ml if prediction/model mentioned. Add viz if chart/visual/plot mentioned.
If general analysis — run all three."""

    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=f"Query: {query}")
    ])
    
    import json
    import re
    
    try:
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            agents = parsed.get("agents", ["eda", "viz"])
        else:
            agents = ["eda", "viz"]
    except:
        agents = ["eda", "viz"]
    
    return {**state, "agents_to_run": agents}

def eda_node(state: AgentState) -> AgentState:
    """Run EDA Agent"""
    if "eda" not in state.get("agents_to_run", []):
        return {**state, "eda_result": ""}
    
    print("🔍 EDA Agent running...")
    result = run_eda_agent(state["query"])
    return {**state, "eda_result": result}

def ml_node(state: AgentState) -> AgentState:
    """Run ML Agent"""
    if "ml" not in state.get("agents_to_run", []):
        return {**state, "ml_result": ""}
    
    print("🤖 ML Agent running...")
    result = run_ml_agent(state["query"])
    return {**state, "ml_result": result}

def viz_node(state: AgentState) -> AgentState:
    """Run Viz Agent"""
    if "viz" not in state.get("agents_to_run", []):
        return {**state, "viz_result": ""}
    
    print("📊 Viz Agent running...")
    clear_charts()
    result = run_viz_agent(state["query"])
    return {**state, "viz_result": result}

def reporter_node(state: AgentState) -> AgentState:
    """Combines all agent outputs into final report"""
    
    combined = f"""
EDA FINDINGS:
{state.get('eda_result', 'N/A')}

ML INSIGHTS:
{state.get('ml_result', 'N/A')}

VISUALIZATION SUMMARY:
{state.get('viz_result', 'N/A')}
"""
    
    system = """You are a Senior Data Analyst writing an executive report.
    
Given findings from EDA, ML, and Visualization agents, create a structured report:

## 📊 Executive Summary
(2-3 lines — most important finding)

## 🔍 Data Quality
(key quality issues)

## 📈 Key Insights
(top 5 insights with numbers)

## 🤖 ML Recommendations  
(best model, accuracy, top features)

## 💡 Business Recommendations
(3 actionable recommendations)

Be specific. Use numbers. Keep it professional."""

    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=combined)
    ])
    
    return {**state, "final_report": response.content}

# Build LangGraph
def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("eda", eda_node)
    workflow.add_node("ml", ml_node)
    workflow.add_node("viz", viz_node)
    workflow.add_node("reporter", reporter_node)
    
    # Add edges
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "eda")
    workflow.add_edge("eda", "ml")
    workflow.add_edge("ml", "viz")
    workflow.add_edge("viz", "reporter")
    workflow.add_edge("reporter", END)
    
    return workflow.compile()

# Main function
graph = build_graph()

def run_multi_agent(query: str) -> tuple[str, list]:
    """Run full multi-agent pipeline"""
    
    initial_state = {
        "query": query,
        "eda_result": "",
        "ml_result": "",
        "viz_result": "",
        "final_report": "",
        "agents_to_run": []
    }
    
    result = graph.invoke(initial_state)
    charts = get_charts()
    
    return result["final_report"], charts