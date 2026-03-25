from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage, AIMessage

llm = ChatOllama(
    model = "phi3:3.8b"
)

human_msg = HumanMessage(content = "Hi who are you?")
messages = [human_msg]

result = llm.invoke(messages)

print(result.content)
