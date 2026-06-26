import logging
import subprocess
from typing import Literal

from agent.llms import get_gemini_llm, get_ollama_llm
from agent.models import AgentState
from langchain.messages import AIMessage
from langgraph.graph import END

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


SUPPORTED_COMMANDS = ["/test", "/pm2 list", "/memory", "/temp"]


def analyze_input(state: AgentState) -> AgentState:
    logger.debug("In analyze_input node")
    state.messages[-1].content = state.messages[-1].content.strip()

    if state.messages[-1].content.startswith("/"):
        state.message_type = "command"
    else:
        state.message_type = "llm"
    logger.debug(f"Set state.message_type to {state.message_type}")
    return state


def run_command(command: str):
    # Run command and capture output
    # TODO: Handle errors

    if command == "/pm2 list":
        result = subprocess.run(["pm2", "list"], capture_output=True, text=True)
        result = result.stdout
    elif command == "/test":
        result = "Test command"
    elif command == "/memory":
        result = subprocess.run(
            "cat /proc/meminfo | head -3", shell=True, capture_output=True, text=True
        )
        result = result.stdout
    elif command == "/temp":
        result = subprocess.run(
            ["vcgencmd", "measure_temp"], capture_output=True, text=True
        )
        result = result.stdout

    logger.debug(f"Ran command: {command} with result: {result}")
    return result


def command_node(state: AgentState) -> AgentState:
    logger.debug("In command_node")
    current_command = state.messages[-1].content
    command_output = f"Unsupported command. Available commands are {SUPPORTED_COMMANDS}"
    if current_command in SUPPORTED_COMMANDS:
        command_output = run_command(current_command)
    logger.debug(f"Command Output set as {command_output}")
    return {"messages": [command_output]}


def gemini_node(state: AgentState) -> AgentState:
    logger.debug("In gemini_node")
    try:
        llm = get_gemini_llm()
        result: AIMessage = llm.invoke(state.messages)
        return {"messages": [result], "llm_failed": False}
    except Exception as e:
        logger.exception(e)
    return {"llm_failed": True}


def local_llm_node(state: AgentState) -> AgentState:
    logger.debug("In local_llm_node")
    llm = get_ollama_llm()
    result: AIMessage = llm.invoke(state.messages)
    return {"messages": [result]}


def routing_function_llm_or_command(
    state: AgentState,
) -> Literal["command_node", "gemini_node"]:
    logger.debug("Routing to llm or command node")
    if state.message_type == "command":
        return "command_node"
    elif state.message_type == "llm":
        return "gemini_node"


def routing_function_local_or_tool_or_end(
    state: AgentState,
) -> Literal["local_llm_node", "tool_node", "end"]:
    logger.debug("Routing to local or tool or end")

    if state.llm_failed:
        return "local_llm_node"

    last_message = state.messages[-1]
    if last_message.tool_calls:
        return "tool_node"

    return END
