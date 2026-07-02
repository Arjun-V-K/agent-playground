import logging
from datetime import datetime
from typing import Annotated

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from .models import InputOutputMessage
from .nodes import (
    analyze_input,
    command_node,
    llm_node,
    routing_function_llm_or_command,
    routing_function_tool_or_end,
)
from .tools import get_user_submissions, multiply

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]


SYSTEM_PROMPT = SystemMessage(
    content="You are WhatsappBot created by Arjun, a friendly assistant in a WhatsApp group chat with four people - Arjun, Rohith, Mubaasim and Dhinesh. "
    f"Currently it is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {datetime.now().strftime('%A')} "
    "Answer in three or four sentences only, unless asked for more detail."
)


def construct_agent_graph(saver):
    graph = StateGraph(AgentState)

    graph.add_node("analyze_input", analyze_input)
    graph.add_node("llm_node", llm_node)
    graph.add_node("command_node", command_node)
    graph.add_node("tool_node", ToolNode([multiply, get_user_submissions]))

    graph.add_edge(START, "analyze_input")
    graph.add_conditional_edges(
        "analyze_input",
        routing_function_llm_or_command,
        {"command_node": "command_node", "llm_node": "llm_node"},
    )
    graph.add_conditional_edges(
        "llm_node",
        routing_function_tool_or_end,
        {"tool_node": "tool_node", END: END},
    )
    graph.add_edge("tool_node", "llm_node")
    graph.add_edge("command_node", END)

    return graph.compile(checkpointer=saver)


async def run_agent(agent, user_input: InputOutputMessage) -> AIMessage:

    if not user_input.msg.startswith("/"):
        user_input.msg = f"[{user_input.senderName}]: {user_input.msg}"

    messages_to_send = [HumanMessage(content=user_input.msg)]

    # TODO: look into other config options and move this
    config = {
        "recursion_limit": 10,  # Prevent infinite loops
        "configurable": {"thread_id": "main-thread-chess-group"},
    }

    current_state = await agent.aget_state(config)

    if not current_state.values.get("messages"):
        # This is a new thread, prepend the system message
        messages_to_send.insert(0, SYSTEM_PROMPT)

    logger.debug(f"Intital Messages: {messages_to_send}")
    result: AgentState = await agent.ainvoke(
        AgentState(messages=messages_to_send), config=config
    )
    logger.debug(f"Final Messages: {result['messages']}")
    return result["messages"][-1].content
