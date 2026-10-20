
# ============================================================
# AI BLOG STUDIO
# Phase 1: Configuration, UI, and LangGraph connection
# Phase 2: Human review, feedback, and revision history
# Phase 3: SQLite persistence, final blog, download, and errors
# ============================================================

from dotenv import load_dotenv

load_dotenv()

import json
import uuid
from datetime import datetime

import streamlit as st
from langgraph.types import Command

from graph import build_blog_graph
from blog_storage import (
    initialize_db,
    save_blog,
    list_blogs,
    load_blog,
    delete_blog,
)


# ============================================================
# 1. PAGE CONFIGURATION AND DATABASE INITIALIZATION
# ============================================================

st.set_page_config(
    page_title="AI Blog Studio",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_db()


# ============================================================
# 2. GRAPH INITIALIZATION
# ============================================================

@st.cache_resource
def get_graph():
    """Create and cache the LangGraph workflow."""
    return build_blog_graph()


graph = get_graph()


# ============================================================
# 3. SESSION STATE INITIALIZATION
# ============================================================

def initialize_session():
    """Initialize session state without overwriting existing values."""

    defaults = {
        "thread_id": str(uuid.uuid4()),
        "started": False,
        "stage": "setup",
        "review_payload": None,
        "final_blog": "",
        "history": [],
        "topic": "",
        "audience": "AI and agentic AI developers",
        "last_error": "",
        "show_history": False,
        "topic_input": "",
        "audience_input": "AI and agentic AI developers",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session()


# ============================================================
# 4. GRAPH CONFIGURATION
# ============================================================

def current_config():
    """Return the configuration for the active graph thread."""

    return {
        "configurable": {
            "thread_id": st.session_state.thread_id,
        }
    }


# ============================================================
# 5. DATABASE PERSISTENCE
# ============================================================

def persist_current_blog():
    """Save the current blog, workflow state, and history to SQLite."""

    save_blog(
        {
            "thread_id": st.session_state.thread_id,
            "topic": (
                st.session_state.topic.strip()
                or "Untitled blog"
            ),
            "audience": st.session_state.audience,
            "stage": st.session_state.stage,
            "review_payload": st.session_state.review_payload,
            "final_blog": st.session_state.final_blog,
            "history": st.session_state.history,
        }
    )


# ============================================================
# 6. HISTORY HELPERS
# ============================================================

def record_event(
    stage,
    action,
    content="",
    feedback="",
):
    """Record an event and immediately persist the updated blog."""

    event = {
        "id": str(uuid.uuid4()),
        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "stage": str(stage),
        "action": action,
        "content": content or "",
        "feedback": feedback or "",
    }

    st.session_state.history.append(event)

    persist_current_blog()


def event_exists(stage, action, content=""):
    """Avoid duplicate review/completion events."""

    return any(
        event.get("stage") == str(stage)
        and event.get("action") == action
        and event.get("content", "") == (content or "")
        for event in st.session_state.history
    )


def get_payload_content(payload):
    """Extract readable text from supported graph payload fields."""

    if not isinstance(payload, dict):
        return str(payload or "")

    for key in ("research", "draft", "blog", "content"):
        value = payload.get(key)

        if isinstance(value, str) and value.strip():
            return value

    return ""


def get_stage_name(payload):
    """Convert graph stage values into readable labels."""

    stage = str(
        payload.get("stage", "review")
    ).lower()

    if "research" in stage:
        return "Research Review"

    if "draft" in stage:
        return "Draft Review"

    return stage.replace("_", " ").title()


# ============================================================
# 7. WORKFLOW STATE SYNCHRONIZATION
# ============================================================

def sync_workflow(result=None):
    """
    Synchronize Streamlit state with the latest LangGraph state.

    Pending interrupts take priority over final output.
    """

    snapshot = graph.get_state(current_config())# type:ignore

    # --------------------------------------------------------
    # A. Human-review interrupt
    # --------------------------------------------------------

    if snapshot.interrupts:
        payload = snapshot.interrupts[0].value

        if not isinstance(payload, dict):
            payload = {
                "content": str(payload),
                "stage": "review",
            }

        st.session_state.started = True
        st.session_state.review_payload = payload

        st.session_state.stage = str(
            payload.get("stage", "review")
        ).lower()

        content = get_payload_content(payload)
        stage_name = get_stage_name(payload)

        if not event_exists(
            stage_name,
            "Review requested",
            content,
        ):
            record_event(
                stage_name,
                "Review requested",
                content,
            )

        persist_current_blog()
        return

    # --------------------------------------------------------
    # B. No interrupt: inspect graph output
    # --------------------------------------------------------

    values = snapshot.values or {}

    final_blog = values.get("final_blog", "")

    if not final_blog and isinstance(result, dict):
        final_blog = result.get("final_blog", "")

    if final_blog:
        st.session_state.final_blog = final_blog
        st.session_state.stage = "final"
        st.session_state.review_payload = None

        if not event_exists(
            "Final Blog",
            "Completed",
            final_blog,
        ):
            record_event(
                "Final Blog",
                "Completed",
                final_blog,
            )

    else:
        st.session_state.stage = "processing"
        st.session_state.review_payload = None

    persist_current_blog()


# ============================================================
# 8. WORKSPACE RESET AND BLOG MANAGEMENT
# ============================================================

def start_new_blog():
    """Start a clean workspace without deleting saved blogs."""

    st.session_state.thread_id = str(uuid.uuid4())

    st.session_state.topic = ""
    st.session_state.audience = (
        "AI and agentic AI developers"
    )

    st.session_state.stage = "setup"
    st.session_state.started = False
    st.session_state.review_payload = None
    st.session_state.final_blog = ""
    st.session_state.history = []
    st.session_state.last_error = ""
    st.session_state.show_history = False

    # Update widget values before the next script rerun.
    st.session_state.topic_input = ""
    st.session_state.audience_input = (
        "AI and agentic AI developers"
    )


def open_saved_blog(thread_id):
    """Restore a saved blog's application state."""

    saved = load_blog(thread_id)

    if saved is None:
        st.session_state.last_error = (
            "The selected blog could not be found."
        )
        return

    st.session_state.thread_id = saved["thread_id"]
    st.session_state.topic = saved["topic"] or ""
    st.session_state.audience = saved["audience"] or ""
    st.session_state.stage = saved["stage"] or "setup"

    st.session_state.review_payload = (
        saved["review_payload"]
    )
    st.session_state.final_blog = saved["final_blog"] or ""
    st.session_state.history = saved["history"] or []

    st.session_state.started = (
        st.session_state.stage != "setup"
    )

    st.session_state.topic_input = st.session_state.topic
    st.session_state.audience_input = (
        st.session_state.audience
    )

    st.session_state.last_error = ""
    st.session_state.show_history = False


def delete_saved_blog(thread_id):
    """Delete a saved blog and reset if it is currently open."""

    delete_blog(thread_id)

    if st.session_state.thread_id == thread_id:
        start_new_blog()


# ============================================================
# 9. PAGE HEADER
# ============================================================

st.title("✍️ AI Blog Studio")

st.caption(
    "Your AI-powered writing workspace — "
    "research, review, draft, and publish."
)


# ============================================================
# 10. SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Create your blog")

    topic = st.text_area(
        "Blog topic",
        placeholder=(
            "e.g. What is MCP? "
            "A Developer's Guide for 2026"
        ),
        height=110,
        key="topic_input",
    )

    audience = st.text_input(
        "Target audience",
        key="audience_input",
    )

    st.divider()

    st.caption("YOUR WORKFLOW")

    st.markdown(
        """
        1. Research
        2. Research Review
        3. Draft Generation
        4. Draft Review
        5. Final Blog
        """
    )

    st.divider()

    st.caption("📚 YOUR BLOGS")

    saved_blogs = list_blogs()

    if not saved_blogs:
        st.caption(
            "Your saved blogs will appear here."
        )

    else:
        for blog in saved_blogs:
            blog_id = blog["thread_id"]

            title = (
                blog["topic"] or "Untitled blog"
            )

            if len(title) > 32:
                title = title[:32] + "…"

            col_open, col_delete = st.columns(
                [5, 1]
            )

            with col_open:
                st.button(
                    f"📝 {title}",
                    key=f"open_{blog_id}",
                    use_container_width=True,
                    help=(
                        "Open saved blog. "
                        f"Status: {blog['stage']}"
                    ),
                    on_click=open_saved_blog,
                    args=(blog_id,),
                )

            with col_delete:
                st.button(
                    "🗑️",
                    key=f"delete_{blog_id}",
                    help="Delete this blog",
                    on_click=delete_saved_blog,
                    args=(blog_id,),
                )

            st.caption(
                f"{blog['stage'].replace('_', ' ').title()} · "
                f"{blog['updated_at'][:16].replace('T', ' ')}"
            )

    st.divider()

    st.button(
        "＋ New Blog",
        use_container_width=True,
        on_click=start_new_blog,
    )


# ============================================================
# 11. WORKFLOW PROGRESS
# ============================================================

stage = st.session_state.stage

progress_values = {
    "setup": 0.0,
    "research": 0.2,
    "research_review": 0.4,
    "draft": 0.6,
    "draft_review": 0.8,
    "review": 0.4,
    "processing": 0.5,
    "final": 1.0,
}

st.subheader("Workflow progress")

st.progress(
    progress_values.get(stage, 0.0)
)

stage_labels = [
    "Research",
    "Research Review",
    "Draft",
    "Draft Review",
    "Final Blog",
]

progress_columns = st.columns(5)

for index, label in enumerate(stage_labels):
    with progress_columns[index]:
        st.markdown(
            f"**{index + 1}. {label}**"
        )


# ============================================================
# 12. START BLOG GENERATION
# ============================================================

if not st.session_state.started:
    st.subheader("Start a new article")

    st.write(
        "Enter your topic and target audience in "
        "the sidebar to begin."
    )

    if st.button(
        "Start blog generation",
        type="primary",
        use_container_width=True,
        disabled=(
            not topic.strip()
            or not audience.strip()
        ),
    ):
        try:
            st.session_state.topic = topic.strip()
            st.session_state.audience = audience.strip()

            st.session_state.stage = "research"
            st.session_state.last_error = ""

            # Save the initial blog record before invoking the graph.
            persist_current_blog()

            with st.spinner(
                "Researching your topic..."
            ):
                record_event(
                    "Research",
                    "Workflow started",
                    (
                        f"Topic: {st.session_state.topic}\n"
                        f"Audience: {st.session_state.audience}"
                    ),
                )

                result = graph.invoke(
                    {
                        "topic": st.session_state.topic,
                        "audience": st.session_state.audience,
                    }, # type:ignore
                    config=current_config(), # type:ignore
                )

                st.session_state.started = True

                sync_workflow(result)

            st.rerun()

        except Exception as error:
            st.session_state.last_error = str(error)
            persist_current_blog()

            st.error(
                f"Could not start the workflow: {error}"
            )


# ============================================================
# 13. HUMAN REVIEW
# ============================================================

if st.session_state.started:
    payload = st.session_state.review_payload

    stage = st.session_state.stage

    if payload is not None:
        stage_name = get_stage_name(payload)
        content = get_payload_content(payload)

        st.divider()

        st.subheader(
            f"📝 {stage_name}"
        )

        st.caption(
            "Review the output below before continuing "
            "to the next stage."
        )

        with st.container(border=True):
            st.markdown(
                content
                or "No displayable text in this payload."
            )

        extra_fields = {
            key: value
            for key, value in payload.items()
            if key not in (
                "research",
                "draft",
                "blog",
                "content",
            )
        }

        if extra_fields:
            with st.expander(
                "Checkpoint details"
            ):
                st.json(extra_fields)

        feedback = st.text_area(
            "Reviewer feedback",
            placeholder=(
                "Suggest improvements, corrections, "
                "or additional points..."
            ),
            key=(
                f"feedback_input_"
                f"{st.session_state.thread_id}_"
                f"{stage}"
            ),
            height=110,
        )
        
        st.caption(
            "Leave feedback blank if the content "
            "is ready for approval."
        )

        col_revise, col_approve = st.columns(2)

        # ----------------------------------------------------
        # REQUEST REVISION
        # ----------------------------------------------------

        with col_revise:
            if st.button(
                "Request revision",
                use_container_width=True,
                disabled=not feedback.strip(),
            ):
                try:
                    with st.spinner(
                        "Submitting feedback..."
                    ):
                        record_event(
                            stage_name,
                            "Revision requested",
                            content,
                            feedback.strip(),
                        )

                        result = graph.invoke(
                            Command(
                                resume={
                                    "action": "revise",
                                    "feedback": feedback.strip(),
                                }
                            ),
                            config=current_config(), # type:ignore
                        )

                        sync_workflow(result)

                    st.rerun()

                except Exception as error:
                    st.session_state.last_error = str(error)
                    persist_current_blog()

                    st.error(
                        "Revision failed. Confirm that your "
                        "graph supports the 'revise' action. "
                        f"Details: {error}"
                    )

        # ----------------------------------------------------
        # APPROVE AND CONTINUE
        # ----------------------------------------------------

        with col_approve:
            if st.button(
                "Approve and continue →",
                type="primary",
                use_container_width=True,
            ):
                try:
                    with st.spinner(
                        "Continuing the workflow..."
                    ):
                        record_event(
                            stage_name,
                            "Approved",
                            content,
                            feedback.strip(),
                        )

                        result = graph.invoke(
                            Command(
                                resume={
                                    "action": "approve",
                                    "feedback": feedback.strip(),
                                }
                            ),
                            config=current_config(),# type:ignore
                        )

                        sync_workflow(result)

                    st.rerun()

                except Exception as error:
                    st.session_state.last_error = str(error)
                    persist_current_blog()

                    st.error(
                        "Could not continue the workflow: "
                        f"{error}"
                    )


# ============================================================
# 14. FINAL BLOG
# ============================================================

elif (
    st.session_state.stage == "final"
    and st.session_state.final_blog
):
    st.divider()

    st.success("Your blog is ready!")

    tab_preview, tab_markdown = st.tabs(
        [
            "Article Preview",
            "Markdown Source",
        ]
    )

    with tab_preview:
        st.markdown(
            st.session_state.final_blog
        )

    with tab_markdown:
        st.text_area(
            "Final Markdown",
            value=st.session_state.final_blog,
            height=450,
            key="final_markdown_view",
        )

    st.download_button(
        "⬇️ Download final blog",
        data=st.session_state.final_blog,
        file_name="final_blog.md",
        mime="text/markdown",
        type="primary",
    )


# ============================================================
# 15. PROCESSING FALLBACK
# ============================================================

elif (
    st.session_state.started
    and st.session_state.stage == "processing"
):
    st.info(
        "The graph has no pending review interrupt and "
        "has not returned a final blog. Inspect the graph "
        "state to determine whether it has completed "
        "or stopped at an unexpected stage."
    )


# ============================================================
# 16. SHOW / HIDE HISTORY
# ============================================================

st.divider()

history_label = (
    "📕 Hide History"
    if st.session_state.show_history
    else "📜 Show History"
)

if st.button(
    history_label,
    use_container_width=True,
):
    st.session_state.show_history = (
        not st.session_state.show_history
    )

if st.session_state.show_history:
    st.subheader("📜 Blog History")

    # Refresh the saved record from SQLite.
    saved_blog = load_blog(
        st.session_state.thread_id
    )

    if saved_blog is not None:
        history = saved_blog.get("history", [])
    else:
        history = st.session_state.history

    if not history:
        st.info(
            "No history available for this blog yet."
        )

    else:
        st.caption(
            f"{len(history)} recorded event(s), "
            "newest first."
        )

        for event in reversed(history):
            timestamp = event.get("time", "")
            event_stage = event.get(
                "stage",
                "Unknown",
            )
            action = event.get(
                "action",
                "Event",
            )

            with st.expander(
                f"{action} · {event_stage} · {timestamp}"
            ):
                content = event.get("content", "")
                feedback = event.get("feedback", "")

                if content:
                    st.markdown("**Content / Details**")
                    st.markdown(content)

                if feedback:
                    st.markdown(
                        "**Reviewer feedback**"
                    )
                    st.write(feedback)

                if not content and not feedback:
                    st.caption(
                        "No additional details."
                    )


# ============================================================
# 17. ERROR DETAILS
# ============================================================

if st.session_state.last_error:
    with st.expander(
        "Last error details"
    ):
        st.code(
            st.session_state.last_error
        )


# ============================================================
# 18. FOOTER
# ============================================================

st.caption(
    "AI Blog Studio · "
    "Powered by your existing LangGraph workflow"
)

