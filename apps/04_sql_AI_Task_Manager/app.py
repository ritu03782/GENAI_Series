from dotenv import load_dotenv
load_dotenv()

from pathlib import Path

import streamlit as st

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent


# -----------------------------
# DATABASE
# -----------------------------

DB_PATH = Path(__file__).resolve().parent / "my_tasks.db"

db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

db.run("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK (
        status IN ('pending', 'in_progress', 'completed')
    ) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")


# -----------------------------
# MODEL
# -----------------------------

model = ChatGroq(
    model="openai/gpt-oss-20b"
)


# -----------------------------
# SQL TOOLKIT
# -----------------------------

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=model
)

tools = toolkit.get_tools()


# -----------------------------
# SYSTEM PROMPT
# -----------------------------

system_prompt = """
You are a task management assistant connected to a SQLite database.

The database contains a table named `tasks` with:

id, title, description, status, created_at

Allowed status values:
- pending
- in_progress
- completed

Rules:

1. Always use the SQL database tools to answer questions about tasks.
2. Never invent or assume task data.
3. Only report data returned by the database.
4. When listing tasks, return at most 10 tasks.
5. Order task lists by created_at DESC.
6. For CREATE, UPDATE, or DELETE operations, verify the result using a SELECT query.
7. If no matching tasks exist, clearly tell the user that no matching tasks were found.
8. Present task lists in a clean table.
"""


# -----------------------------
# AGENT
# -----------------------------

@st.cache_resource
def get_agent():

    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )

    return agent


agent = get_agent()


# -----------------------------
# STREAMLIT UI
# -----------------------------

if "tasks" not in st.session_state:
    st.session_state.tasks = []


st.subheader("📋 TaskBot - Manage your todos")

st.markdown(
    "📌 AI task manager to help you manage your tasks"
)


# Display previous messages
for task in st.session_state.tasks:

    st.chat_message(task["role"]).markdown(
        task["content"]
    )


# Chat input
prompt = st.chat_input(
    "Ask me to manage your tasks..."
)


if prompt:

    # Display user message
    st.chat_message("user").markdown(prompt)

    st.session_state.tasks.append({
        "role": "user",
        "content": prompt
    })


    # Agent response
    with st.chat_message("assistant"):

        with st.spinner("Processing..."):

            response = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                {
                    "configurable": {
                        "thread_id": "1"
                    }
                }
            )


        result = response["messages"][-1].content

        st.markdown(result)

        st.session_state.tasks.append({
            "role": "assistant",
            "content": result
        })