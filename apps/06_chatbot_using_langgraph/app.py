from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
import streamlit as st

class ChatState(BaseModel):
    messages:Annotated[list, add_messages]

llm = ChatGroq(model ="openai/gpt-oss-20b")

def chatBotNode(state:ChatState) -> ChatState:
    res = llm.invoke(state.messages)
    return {"messages": [res]}

graph = StateGraph(ChatState)

memory = InMemorySaver()

graph.add_node("chatBot" ,chatBotNode)

graph.add_edge(START, "chatBot")
graph.add_edge("chatBot", END)

ChatGraph = graph.compile(checkpointer = memory)

st.title("🤖 ChatBot")
st.subheader("Feel free to ask anything you want to know")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ChatGraph" not in st.session_state:
    st.session_state.ChatGraph = ChatGraph
# Display existing history
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

query = st.chat_input("What's in your mind today")

if query: 
    st.chat_message("user").markdown(query)
    st.session_state.messages.append({"role":"user","content":query})
    res = st.session_state.ChatGraph.invoke(
        {"messages":[{"role":"user" , "content" : query}]},
        {"configurable":{"thread_id":"my-bot-1"}}
    )
    result = res["messages"][-1].content
    st.chat_message("ai").markdown(result)
    st.session_state.messages.append({"role":"ai","content":result})








