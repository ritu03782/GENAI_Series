# ✍️ AI Blog Studio

An AI-powered blog generation application built with **Python, Streamlit, and LangGraph**. It provides a structured workflow for researching topics, generating blog drafts, reviewing AI-generated content, incorporating human feedback, and producing downloadable Markdown articles.

## 🚀 Overview

AI Blog Studio combines AI-assisted content generation with human-in-the-loop review. Instead of generating an article in a single step, the application organizes the process into multiple stages, allowing users to inspect content and provide feedback before proceeding.

The application also includes a blog history interface for accessing previously saved articles and tracking their workflow progress.

## ✨ Features

- **AI-powered blog workflow:** Connects to a LangGraph workflow for research, drafting, and final content generation.
- **Human-in-the-loop review:** Presents review checkpoints where users can inspect generated content.
- **Feedback and revision requests:** Allows reviewers to submit improvement instructions to the workflow.
- **Approval-based progression:** Enables users to approve content and continue to the next stage.
- **Workflow progress indicator:** Displays the current stage of blog generation.
- **Blog history:** Lists previously saved blogs and their latest recorded stages.
- **Load and delete blogs:** Reopen saved blog records or delete them from the application's storage.
- **Article preview:** Renders the final blog as formatted Markdown.
- **Markdown source viewer:** Displays the underlying Markdown content.
- **Download functionality:** Downloads the completed article as a `.md` file.
- **Session state management:** Preserves interface state across Streamlit reruns.
- **Error handling:** Displays errors encountered during workflow execution.

## 🔄 Workflow

The application follows this general process:

1. **Enter topic and audience:** Specify the subject of the blog and its intended readers.
2. **Research:** Start the LangGraph workflow to process the requested topic.
3. **Research review:** Inspect the research output and approve it or request changes.
4. **Draft generation:** Continue the workflow to generate a blog draft.
5. **Draft review:** Review the draft and provide feedback where necessary.
6. **Final blog:** View the completed article, inspect its Markdown source, and download it.

The exact node sequence, revision behavior, and checkpoint handling depend on the implementation in `graph.py`.

## 🛠️ Tech Stack

| Technology                    | Purpose                                                  |
| ----------------------------- | -------------------------------------------------------- |
| Python                        | Core application logic                                   |
| Streamlit                     | Web-based user interface                                 |
| LangGraph                     | Workflow orchestration and human-in-the-loop execution   |
| LangChain ecosystem           | AI workflow integrations, if configured in the graph     |
| SQLite or configured database | Blog history persistence, depending on `blog_storage.py` |
| python-dotenv                 | Environment variable loading                             |
| UUID                          | Unique workflow and event identifiers                    |

**Note:** The exact LLM provider, model, research integrations, and database implementation are determined by the supporting modules and environment configuration.

## 📁 Project Structure

A typical project structure for this application is:

```text
07_blog_generator/
│
├── app.py                  # Streamlit application and UI
├── graph.py                # LangGraph workflow definition
├── blog_storage.py         # Blog persistence operations
├── .env                    # Environment variables and API keys
├── .gitignore              # Files excluded from version control
├── requirements.txt        # Python dependencies
└── blog_history.db         # Local database, if SQLite is configured
└── agents.py               # Containing Researcher, Writer, Editor prompts and agent
└── state.py                # Containing Graph state storing values across multiple nodes of graph
```

The actual filenames and database location may differ depending on your implementation.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ritu03782/GENAI_Series/tree/main/apps/07_blog_generator
cd 07_blog_generator
```

### 2. Create a virtual environment

**Windows — PowerShell**

```powershell
python -m venv env
```

Activate it:

```powershell
.\env\Scripts\Activate.ps1
```

If activation is blocked by your PowerShell execution policy, use the appropriate environment activation method for your setup.

### 3. Install dependencies

If your project already contains `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

Otherwise, install the dependencies required by your actual implementation and generate a dependency file after verifying the application works.

### 4. Configure environment variables

Create a `.env` file in the project directory and add the environment variables required by your configured LLM provider and integrations.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

The variable above is an example for a Groq-based setup; use the actual variable names expected by your project.

**Security:** Never commit your real API keys or other secrets to a public repository. Add `.env` to `.gitignore`.

### 5. Run the application

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser to use AI Blog Studio.

## 🧠 How It Works

### LangGraph workflow

The application imports the graph builder:

```python
from graph import build_blog_graph
```

The graph is initialized through a cached resource:

```python
@st.cache_resource
def get_graph():
    return build_blog_graph()
```

The compiled graph is invoked with the blog topic and target audience.

### Human-in-the-loop execution

The application checks the graph state for pending interrupts. When a review checkpoint is found, the corresponding content is presented to the user.

Review decisions are sent to LangGraph through resume commands:

```python
Command(
    resume={
        "action": "approve",
        "feedback": ""
    }
)
```

Revision requests use a similar structure, with the action set to `"revise"` and the reviewer's feedback included.

The graph must explicitly implement these actions for them to work as intended.

### Workflow identification

Each blog receives a unique thread ID. This ID is passed through the LangGraph configuration so that a compatible checkpointer can associate execution state with the correct workflow.

### Blog persistence

The application imports storage functions from `blog_storage.py` to initialize storage and list, load, save, or delete blog records.

Persistent saving must be invoked at the appropriate points in the workflow; defining a save helper alone does not automatically save every change.

## 📚 Learning Objectives

This project provides practical experience with:

- Building interactive Python applications with Streamlit.
- Managing state across application reruns.
- Designing multi-step AI workflows using LangGraph.
- Implementing human-in-the-loop interaction patterns.
- Passing feedback between users and AI workflows.
- Working with structured dictionaries and workflow state.
- Persisting application data and maintaining revision history.
- Handling exceptions and debugging AI application workflows.
- Generating and downloading Markdown documents.

## 🔒 Security and Limitations

- API keys should be stored in environment variables rather than hardcoded in source files.
- Persistent blog history depends on the configured storage implementation.
- Resuming an interrupted workflow requires a compatible LangGraph checkpointer and the correct thread ID.
- Revision requests depend on the graph's implementation of the revision action.
- The application provides Markdown downloads; automatic publication to an external blogging platform is not included in the described interface.
- Generated content should be reviewed for factual accuracy, quality, and appropriate sourcing before publication.

## 🚧 Future Improvements

Potential enhancements include:

- Automatic persistence after each workflow transition.
- Improved restoration of interrupted workflows.
- Version comparison between research and draft revisions.
- Editing and saving the final article within the interface.
- Exporting articles to PDF or DOCX.
- Configurable writing tone, length, and content structure.
- Research-source citations and source verification.
- Authentication and multi-user workspace support.
- Publishing integrations for supported blogging platforms.
- Automated tests for graph transitions and storage operations.

## 👨‍💻 Author

**Ritu Singh**

B.Tech Computer Science and Engineering

Institute of Engineering and Technology, Lucknow

## 📄 License

Choose an appropriate open-source license before distributing this project. If you intend to use the MIT License, add a `LICENSE` file containing its full license text.
