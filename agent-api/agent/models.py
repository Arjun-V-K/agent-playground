from typing import Annotated, Literal

from langchain.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel


class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    message_type: Literal["command", "llm"] | None = None
    llm_failed: bool = False


class InputOutputMessage(BaseModel):
    msg: str
    senderName: str = None
