from enum import Enum
from functools import lru_cache

from agent.tools import get_user_submissions, multiply
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama


class LLMProvider(Enum):
    LOCAL_OLLAMA = "ollama"
    GOOGLE_GEMENI = "google_gemini"


def _initialize_llm(provider: LLMProvider) -> BaseChatModel:
    """
    Initializes and configures the LLM based on the selected provider.
    """
    if provider is LLMProvider.LOCAL_OLLAMA:
        return ChatOllama(model="phi3:3.8b", num_predict=100)

    if provider is LLMProvider.GOOGLE_GEMENI:
        base_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
        return base_llm.bind_tools([multiply, get_user_submissions])

    raise ValueError(f"Unsupported LLM provider: {provider}")


@lru_cache
def get_ollama_llm() -> ChatOllama:
    return _initialize_llm(LLMProvider.LOCAL_OLLAMA)


@lru_cache
def get_gemini_llm() -> ChatGoogleGenerativeAI:
    return _initialize_llm(LLMProvider.GOOGLE_GEMENI)
