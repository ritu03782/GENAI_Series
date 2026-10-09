from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

import streamlit as st
from streamlit_mic_recorder import mic_recorder
from groq import Groq

import os

# -------- Session state ------------#

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

if "agent" not in st.session_state:
    st.session_state.agent = None

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "messages" not in st.session_state:
    st.session_state.messages = []

#-------- GROQ CLIENT -----------#
#-------- Used for Speech-to-Text--------#

groq_client = Groq(
    api_key = os.getenv("GROQ_API_KEY")
)

#---------Process Document---------#

def process_document(path):
    loader = PyPDFDirectoryLoader(path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
    docs = splitter.split_documents(documents = docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_db = InMemoryVectorStore.from_documents(
        documents = docs,
        embedding = embeddings
    )

#------LLM--------#

    llm = ChatGroq(
        model=  "openai/gpt-oss-20b"
    )

#-------Retriever Tool------#
    @tool 
    def retrieve_context(query:str):
        """Retrieve documents relevant to a query from the knowledge base"""
        context = ""
        docs = vector_db.similarity_search(query=query, k=3)
        for doc in docs:
            context += doc.page_content + "\n\n"
        return context

#------system_prompt------#
    system_prompt = """You are a helpful assistent that answers questions using retrieved context
        My knowledge base consists of the details from the uploaded document.
        As always use 'retrieve_context' tool for questions requiring external knowledge"""

#-------memeory-------#

    memory = InMemorySaver()

#-------agent---------#

    agent = create_agent(
        model = llm,
        tools = [retrieve_context],
        system_prompt = system_prompt,
        checkpointer = memory,
    )
    st.session_state.agent = agent
    st.session_state.document_uploaded = True

#---------PDF upload---------#
if not st.session_state.document_uploaded:
    uploaded = st.file_uploader(label = "Select PDF Files", type=["pdf"], accept_multiple_files=True)
    if uploaded:
        with st.spinner("Processing..."):
            path = "./doc_files/"
            for file in uploaded:
                with open(path + file.name, "wb") as f:
                    f.write(file.getvalue())
            process_document(path)
            st.rerun()

#------Chat Interface--------#

if st.session_state.document_uploaded and st.session_state.agent:
    st.title("📚 Document Chatbot")
    st.caption("Ask questions using text or 🎤 voice.")

    #------display Chat History----------#
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        st.chat_message(role).markdown(content)

#--------Chat Input + Microphone --------#
    col1, col2 = st.columns([8,1])
    with col1:
        text_query = st.chat_input("Ask anything related to uploaded documents....")
    
    
    with col2:
        audio = mic_recorder(
            start_prompt="🎤 Speak",
            stop_prompt="⏹️ Stop",
            just_once=True,
            use_container_width=True,
            format="wav"
        )

#-----Determine query-------#

    query = None

    if text_query:
        query = text_query

    elif audio:
        with st.spinner("🎧 Converting speech to text..."):
            try:
                transcription = groq_client.audio.transcriptions.create(
                    file=(
                        "audio.wav",
                        audio["bytes"]
                    ),
                    model="whisper-large-v3-turbo",
                    response_format="text"
                )
                query = transcription.strip() # type: ignore
            except Exception as e:
                st.error(
                    f"Speech recognition failed: {e}"
                )

    if query:
        st.session_state.messages.append({"role":"user","content":query})
        response = st.session_state.agent.invoke(
            {"messages":[{"role":"user","content":query}]},
            {"configurable":{"thread_id":1}}
        )
        answer = response["messages"][-1].content
        st.session_state.messages.append({"role":"ai","content":answer})
        st.rerun()
