# 📚 PDF Document Chatbot with Voice Input

An AI-powered document question-answering application built with **Python, Streamlit, LangChain, Groq, and Hugging Face embeddings**. Upload PDF documents and ask questions using text or voice to retrieve relevant information and generate context-aware answers.

## ✨ Features

- **PDF Document Processing:** Load and process PDF files using LangChain document loaders.
- **Text Chunking:** Split documents into manageable chunks with overlapping text to preserve context.
- **Semantic Search:** Generate vector embeddings using `sentence-transformers/all-MiniLM-L6-v2` and retrieve relevant document passages.
- **AI-Powered Question Answering:** Use Groq-hosted LLMs through LangChain agents to answer questions using retrieved document context.
- **Voice Input:** Record voice queries directly in the Streamlit interface.
- **Speech-to-Text:** Convert spoken questions into text using Groq's Whisper transcription API.
- **Conversation History:** Display previous questions and answers during the session.
- **In-Memory Vector Storage:** Store document embeddings in an in-memory vector store for similarity-based retrieval.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| LangChain | Document processing and agent orchestration |
| LangGraph | Conversation checkpointing and memory |
| Groq API | LLM inference and speech transcription |
| Hugging Face Embeddings | Semantic representation of document text |
| InMemoryVectorStore | Vector storage and similarity search |
| PyPDFDirectoryLoader | PDF loading |
| RecursiveCharacterTextSplitter | Text chunking |
| streamlit-mic-recorder | Voice recording |

## ⚙️ How It Works

1. **Upload PDFs:** Select one or more PDF documents through the Streamlit interface.
2. **Extract and Split Text:** Load document content and divide it into chunks of 1,000 characters with 200-character overlap.
3. **Generate Embeddings:** Convert the text chunks into vector embeddings using a Hugging Face sentence-transformer model.
4. **Retrieve Context:** Search for the three most relevant document chunks using semantic similarity.
5. **Generate an Answer:** The LangChain agent invokes the retrieval tool and uses the Groq-hosted language model to formulate a response.
6. **Ask Through Voice:** Record a question, transcribe it using Whisper, and submit the resulting text to the same question-answering workflow.

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### 2. Create and activate a virtual environment

```bash
python -m venv env
```

Windows PowerShell:

```powershell
.\env\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install streamlit python-dotenv langchain-community langchain-text-splitters langchain-huggingface langchain-groq langchain langgraph sentence-transformers pypdf streamlit-mic-recorder groq
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Obtain your API key from the [Groq Console](https://console.groq.com/).

**Security:** Never commit your `.env` file or expose your API key in a public repository.

Add the following to `.gitignore`:

```gitignore
.env
env/
__pycache__/
doc_files/
```

### 5. Run the application

Save your Python application as `app.py` and run:

```bash
streamlit run app.py
```

Open the local URL provided by Streamlit in your browser.

## 📁 Project Structure

```text
pdf-document-chatbot/
├── app.py
├── doc_files/
├── .env
├── .gitignore
└── README.md
```

- `app.py` — PDF ingestion, embeddings, retrieval tool, agent, voice transcription, and Streamlit UI.
- `doc_files/` — Local directory used to store uploaded PDFs.
- `.env` — Stores the Groq API key.
- `.gitignore` — Excludes credentials, virtual environments, and uploaded documents from Git.

## 🔮 Future Improvements

- Add source citations, page numbers, and document references to answers.
- Support persistent vector databases such as Chroma or FAISS.
- Improve multi-document management and document deletion.
- Add conversation reset and session-specific memory.
- Improve error handling for empty, scanned, or unsupported PDFs.
- Add deployment support and secure API-key management.

## 🎯 Learning Outcomes

This project demonstrates practical experience with **Retrieval-Augmented Generation (RAG), vector embeddings, semantic search, LLM tool calling, conversational AI, speech-to-text integration, and Python application development**.

## 📄 License

This project is intended for educational and portfolio purposes. Add a license file if you intend to distribute it under specific reuse terms.
