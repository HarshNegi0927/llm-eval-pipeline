from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from tools import analysis_tools, df_store
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# Bind tools to LLM
llm_with_tools = llm.bind_tools(analysis_tools)

def run_agent(query: str) -> str:
    try:
        system_prompt = """You are an expert data analyst AI agent.
        
Rules:
- Always call get_dataframe_info first to understand the data
- Give specific numbers and percentages
- End with 3 actionable business recommendations
- Be concise and clear"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]

        # Agentic loop
        for _ in range(8):
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            # Agar tool calls hain toh execute karo
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    # Tool dhundo aur run karo
                    tool_name = tool_call["name"]
                    tool_input = tool_call["args"]
                    
                    selected_tool = next(
                        (t for t in analysis_tools if t.name == tool_name), None
                    )
                    
                    if selected_tool:
                        tool_result = selected_tool.invoke(tool_input)
                    else:
                        tool_result = f"Tool {tool_name} not found"
                    
                    from langchain_core.messages import ToolMessage
                    messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"]
                        )
                    )
            else:
                # No more tool calls — final answer
                return response.content

        return "Max iterations reached"
        
    except Exception as e:
        return f"Error: {str(e)}"