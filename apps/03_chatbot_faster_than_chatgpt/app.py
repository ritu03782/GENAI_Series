from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st

llm = ChatGroq(model="openai/gpt-oss-20b", streaming=True)
search = GoogleSerperAPIWrapper()
tools = [search.run]

if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()
if "history" not in st.session_state:
    st.session_state.history = []

agent = create_agent(
            model = llm,
            tools = tools,
            checkpointer = st.session_state.memory,
            system_prompt = "You are a amazing ai agent and can search on google as well"
        )

### Building Web Interface..
st.subheader("💭 QuickAnswer - Answers at the speed of thought")

for message in st.session_state.history:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

query = st.chat_input("Ask Anything ?")
if query:
    st.chat_message("user").markdown(query)
    st.session_state.history.append({"role":"user", "content":query})
    
    response = agent.stream(
               {"messages":[{"role":"user", "content":query}]},
               {"configurable":{"thread_id":"usd123"}},
               stream_mode = "messages"
    ) ### return tuple (chunk, metadata)

    ai_container = st.chat_message("ai")
    with ai_container:
        space = st.empty()
        message = ""

        for chunk in response:
            content = chunk[0].content
            message = message+content
            space.write(message)
            

        st.session_state.history.append({"role":"ai", "content":message})



