from typing import Annotated

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from .nodes import (
    analyze_input,
    command_node,
    gemini_node,
    local_llm_node,
    routing_function_llm_or_command,
    routing_function_local_or_tool_or_end,
)
from .tools import get_user_submissions, multiply


class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]


SYSTEM_PROMPT = SystemMessage(
    content="You are WhatsappBot created by Arjun, a friendly assistant in a WhatsApp group chat with four people - Arjun, Rohith, Mubaasim and Dhinesh. Answer casual, random questions clearly and briefly."
)


def construct_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_input", analyze_input)
    graph.add_node("gemini_node", gemini_node)
    graph.add_node("command_node", command_node)
    graph.add_node("local_llm_node", local_llm_node)
    graph.add_node("tool_node", ToolNode([multiply, get_user_submissions]))

    graph.add_edge(START, "analyze_input")
    graph.add_conditional_edges(
        "analyze_input",
        routing_function_llm_or_command,
        {"command_node": "command_node", "gemini_node": "gemini_node"},
    )
    graph.add_conditional_edges(
        "gemini_node",
        routing_function_local_or_tool_or_end,
        {"local_llm_node": "local_llm_node", "tool_node": "tool_node", END: END},
    )
    graph.add_edge("tool_node", "gemini_node")
    graph.add_edge("command_node", END)
    graph.add_edge("local_llm_node", END)

    return graph.compile()


def run_agent(user_input: str) -> AIMessage:
    agent = construct_agent_graph()
    initial_state = AgentState(
        messages=[SYSTEM_PROMPT] + [HumanMessage(content=user_input)]
    )
    config = {"recursion_limit": 10}  # Prevent infinite loops
    result: AgentState = agent.invoke(initial_state, config=config)
    return result["messages"][-1].content
