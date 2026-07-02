import logging
import subprocess
from typing import Literal

from agent.llms import get_llm, get_model_configuration
from agent.models import AgentState
from langchain.messages import AIMessage
from langchain_core.messages import RemoveMessage, SystemMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langgraph.graph import END

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


SUPPORTED_COMMANDS = ["/test", "/pm2 list", "/memory", "/temp", "/switch"]


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
    elif command == "/switch":
        result = get_model_configuration().switch_model()
        result = f"Switched to {result} model"

    logger.debug(f"Ran command: {command} with result: {result}")
    return result


def command_node(state: AgentState) -> AgentState:
    logger.debug("In command_node")
    current_command = state.messages[-1].content
    command_output = f"Unsupported command. Available commands are {SUPPORTED_COMMANDS}"

    # Clear all messages expect SystemMessage
    if current_command == "/clear":
        delete_messages = [
            RemoveMessage(id=m.id)
            for m in state.messages
            if not isinstance(m, SystemMessage)
        ]
        return {"messages": delete_messages + [AIMessage(content="Memory cleared")]}

    if current_command in SUPPORTED_COMMANDS:
        command_output = run_command(current_command)
    logger.debug(f"Command Output set as {command_output}")
    return {"messages": [command_output]}


def llm_node(state: AgentState) -> AgentState:
    # TODO: error handling when llm fails
    logger.debug("In llm_node")
    llm = get_llm()

    # Trimming old messages
    trimmed_messages = trim_messages(
        state.messages,
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=512,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )

    logger.debug(
        f"All messages : {state.messages} \n Trimmed messages: {trimmed_messages}"
    )
    result: AIMessage = llm.invoke(trimmed_messages)

    messages_to_remove = [m for m in state.messages if m not in trimmed_messages]

    return {
        "messages": [result] + [RemoveMessage(id=m.id) for m in messages_to_remove],
        "llm_failed": False,
    }


def routing_function_llm_or_command(
    state: AgentState,
) -> Literal["command_node", "llm_node"]:
    logger.debug("In routing_function_llm_or_command")
    if state.message_type == "command":
        return "command_node"
    elif state.message_type == "llm":
        return "llm_node"


def routing_function_tool_or_end(
    state: AgentState,
) -> Literal["local_llm_node", "tool_node", "end"]:
    logger.debug("In routing_function_tool_or_end")

    last_message = state.messages[-1]
    if last_message.tool_calls:
        return "tool_node"

    return END
