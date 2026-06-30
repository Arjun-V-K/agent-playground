from enum import Enum
from functools import lru_cache

from agent.tools import get_user_submissions, multiply
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from pydantic import BaseModel


class LLMProvider(Enum):
    LOCAL_OLLAMA = "ollama"
    GOOGLE_GEMENI = "google_gemini"
    GROQ = "groq"


def _initialize_llm(provider: LLMProvider) -> BaseChatModel:
    """
    Initializes and configures the LLM based on the selected provider.
    """
    if provider is LLMProvider.LOCAL_OLLAMA:
        base_llm = ChatOllama(model="qwen2.5:3b", num_predict=500)

    if provider is LLMProvider.GOOGLE_GEMENI:
        base_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

    if provider is LLMProvider.GROQ:
        base_llm = ChatGroq(model="openai/gpt-oss-120b")

    return base_llm.bind_tools([multiply, get_user_submissions])


@lru_cache
def get_ollama_llm() -> ChatOllama:
    return _initialize_llm(LLMProvider.LOCAL_OLLAMA)


@lru_cache
def get_gemini_llm() -> ChatGoogleGenerativeAI:
    return _initialize_llm(LLMProvider.GOOGLE_GEMENI)


@lru_cache
def get_groq_llm() -> ChatGroq:
    return _initialize_llm(LLMProvider.GROQ)


class ModelType(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


class ModelConfiguration(BaseModel):
    model_type: ModelType = ModelType.LOCAL

    def switch_model(self) -> str:
        self.model_type = (
            ModelType.CLOUD if self.model_type is ModelType.LOCAL else ModelType.LOCAL
        )
        return self.model_type.value


_model_configuration = ModelConfiguration()


def get_model_configuration() -> ModelConfiguration:
    return _model_configuration


def get_llm() -> BaseChatModel:
    model_configuration = get_model_configuration()
    if model_configuration.model_type is ModelType.LOCAL:
        return get_ollama_llm()
    # TODO: Currently not using gemini, only Groq. Maybe come up with rotating model selection, for even user selection the same way we do for Local vs Cloud
    if model_configuration.model_type is ModelType.CLOUD:
        return get_groq_llm()

    raise ValueError(f"Unsupported model type: {model_configuration.model_type}")
