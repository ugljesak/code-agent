import re
from typing import Annotated, List

from langchain_core.tools import Tool
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict

from src import config
from src.tools import run_python_code


SYSTEM_PROMPT = """You are a Python developer with experience in fixing buggy code.

You will be given:
1.  A buggy Python function.
2.  A test script (`check` function) that uses assertions to test the function.

Your goal is to provide a single, corrected Python code block containing only the fixed function.

Here is your plan:
1.  Analyze: Carefully read the buggy code and the test script to understand the bug.
2.  Hypothesize: Form a hypothesis about what is wrong.
3.  Write Fix: Write the full, corrected version of the function.
4.  Test Fix: You MUST test your fix. To do this, call the `run_python_code` tool with a script that includes both your fixed function and the original test script.
5.  Observe:
        If the tool returns 'Success', your fix is correct.
        If the tool returns an 'AssertionError' or other traceback, your fix is wrong. Analyze the error and go back to step 3.
6.  Final Answer: Once your fix passes the tool check (returns 'Success'), provide your final answer. Your final response must be only the corrected Python code block, formatted like this:
    ```python
    def fixed_function(arg1, arg2):
        # ... corrected logic ...
        return result
    ```
Do not include the test code or any other text in your final response.
"""

class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

def create_llm():
    return ChatOllama(
        model=config.MODEL_NAME,
        base_url=config.OLLAMA_BASE_URL,
        temperature=0.0
    )

def create_agent_node(model):
    
    def agent_node(state: AgentState) -> AgentState:
        response = model.invoke(state["messages"])
        return {"messages": [response]}
    
    return agent_node

def create_tool_node(tools):
    return ToolNode(tools=tools)

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "action"
    return "finish"


def create_agent():
    
    llm = create_llm()
    tools = [run_python_code]
    llm = llm.bind_tools(tools)

    agent_node = create_agent_node(llm)
    tool_node = create_tool_node(tools)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("action", tool_node)
    
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "action": "action",
            "finish": END,
        },
    )
    graph.add_edge("action", "agent")
    
    return graph.compile()


def run_agent(model, prompt: str) -> str:

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    
    inputs = {"messages": messages}
    
    try:
        final_state = model.invoke(inputs, config={"recursion_limit": config.AGENT_MAX_ITERATIONS})
        return final_state["messages"][-1].content
    except Exception as e:
        return f"Error during agent execution: {e}"


def display_graph(agent):
    
    from IPython.display import Image, display
    display(Image(agent.get_graph().draw_mermaid_png()))


def parse_final_code(llm_response: str) -> str:
    
    # for case that it has markdown format
    match = re.search(r"```python\n(.*?)```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    if "def " in llm_response:
        return llm_response.strip()
        
    return ""