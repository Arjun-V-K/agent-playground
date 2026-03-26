from typing import Annotated

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, add_messages

from pydantic import BaseModel

class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]

SYSTEM_PROMPT = SystemMessage(content = "You are Groot. You will reply with 'I am groot' to all questions.")

def get_llm() -> BaseChatModel:
    llm = ChatOllama(
        model = "tinyllama",
        num_predict=100
    )
    return llm

def llm_node(state: AgentState) -> AgentState:
    llm: BaseChatModel = get_llm()
    result: AIMessage = llm.invoke(state.messages)
    return {"messages" : [result]} # This will append the AI message to the state due to the add_messages reducer

def construct_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("llm_node", llm_node)
    
    graph.add_edge(START, "llm_node")
    graph.add_edge("llm_node", END)

    return graph.compile()

def run_agent(user_input: str) -> AIMessage:
    agent = construct_agent_graph()
    initial_state = AgentState(messages = [HumanMessage(content = user_input)])
    result: AgentState = agent.invoke(initial_state)
    return result['messages'][-1].content


def main():
    print(run_agent(HumanMessage("Hi, who are you?")))

if __name__ == '__main__':
    main()