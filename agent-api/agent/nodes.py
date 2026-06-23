import logging
import subprocess
from enum import Enum
from typing import Literal

from langchain.messages import AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langgraph.graph import END

from .models import AgentState
from .tools import get_user_submissions, multiply

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class LLMProvider(Enum):
    LOCAL_OLLAMA = "ollama"
    GOOGLE_GEMENI = "google_gemini"


def initialize_llm(provider: LLMProvider) -> BaseChatModel:
    """
    Initializes and configures the LLM based on the selected provider.
    """
    if provider is LLMProvider.LOCAL_OLLAMA:
        return ChatOllama(model="phi3:3.8b", num_predict=100)

    if provider is LLMProvider.GOOGLE_GEMENI:
        base_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
        return base_llm.bind_tools([multiply, get_user_submissions])

    raise ValueError(f"Unsupported LLM provider: {provider}")


SUPPORTED_COMMANDS = ["/test", "/pm2 list", "/memory", "/temp"]

_GEMINI_LLM = None
_OLLAMA_LLM = None


def get_gemini_llm() -> ChatGoogleGenerativeAI:
    global _GEMINI_LLM
    if _GEMINI_LLM is None:
        _GEMINI_LLM = initialize_llm(LLMProvider.GOOGLE_GEMENI)
    return _GEMINI_LLM


def get_ollama_llm() -> ChatOllama:
    global _OLLAMA_LLM
    if _OLLAMA_LLM is None:
        _OLLAMA_LLM = initialize_llm(LLMProvider.LOCAL_OLLAMA)
    return _OLLAMA_LLM


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
        result: AIMessage = get_gemini_llm().invoke(state.messages)
        return {"messages": [result], "llm_failed": False}
    except Exception as e:
        logger.exception(e)
    return {"llm_failed": True}


def local_llm_node(state: AgentState) -> AgentState:
    logger.debug("In local_llm_node")
    result: AIMessage = get_ollama_llm().invoke(state.messages)
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
        return "tools"

    return END
