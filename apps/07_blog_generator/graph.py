from langgraph.graph import StateGraph, START , END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt , Command
from typing import Literal
from state import BlogState
from agents import get_llm, researcher_agent, writer_agent, editor_agent

MAX_REVISION = 3

#### Node - Edges
#### Define the Nodes

## Researcher Node
def researcher_node(state:BlogState):
    """Researcher Agent generates (or revises) the research outline """
    llm = get_llm()
    research_data = researcher_agent(
        llm=llm,
        topic=state.topic,
        audience=state.audience,
        research_fb = state.research_fb
    )
    state.research = research_data
    state.research_fb = ""
    return state

def human_review_research_node(state:BlogState):
    """Pause and ask the human to approve the research or send the feedback"""
    decision = interrupt({
        "stage":"researcher_review",
        "research":state.research,
        "instructions":(
            "Reply with 'approve' to continue to writing "
            "or describe what need to be changed to send it back to the researcher"
        )
    })
    if isinstance(decision, dict):
        action = decision.get("action","approve")
        feedback = decision.get("feedback","")
    else:
        text = str(decision)
        action = "approve" if text.lower() in ['approve', 'approved', 'ok', 'yes', 'process',""] else "revise"
        feedback = text if action != "approve" else ""

    state.research_fb = feedback
    return state
## Writer Node
def writer_node(state:BlogState):
    """Writer Agent produce the full draft blog based on researched content (or revise it)"""
    llm = get_llm()
    draft_data = writer_agent(
        llm=llm,
        topic=state.topic,
        audience=state.audience,
        draft_fb = state.draft_fb
    )
    state.draft = draft_data
    state.draft_fb = ""
    return state

def human_review_draft_node(state:BlogState):
    """Pause and ask the human to approve the draft or send the feedback"""
    decision = interrupt({
        "stage":"draft_review",
        "draft":state.draft,
        "instructions":(
            "Reply with 'approve' to publish final  blog and send to the editor "
            "or describe what need to be changed to send it back to the writer"
        )
    })
    if isinstance(decision, dict):
        action = decision.get("action","approve")
        feedback = decision.get("feedback","")
    else:
        text = str(decision)
        action = "approve" if text.lower() in ['approve', 'approved', 'ok', 'yes', 'process',""] else "revise"
        feedback = text if action != "approve" else ""

    state.draft_fb = feedback
    return state
## Editor Node
def editor_node(state:BlogState):
    llm =get_llm()
    final = editor_agent(
        llm = llm,
        topic = state.topic,
        draft = state.draft
    )
    state.final_blog = final
    return state

## Conditional Edges

def route_after_research_review(state:BlogState)-> Literal["research","write"]:
    if state.research_fb:
        return "research"
    else:
        return "write"
def route_after_draft_review(state:BlogState)->Literal["edit","write"]:
    if state.draft_fb and state.revision_count < MAX_REVISION:
        return "write"
    else:
        return "edit"

#### Build and compile the graph
def build_blog_graph():
    builder = StateGraph(BlogState)

    ### Add Nodes
    builder.add_node("research", researcher_node)
    builder.add_node("research_review", human_review_research_node)
    builder.add_node("write", writer_node)
    builder.add_node("write_review", human_review_draft_node)
    builder.add_node("edit", editor_node)
    ### Add edges
    builder.add_edge(START,"research")
    builder.add_edge("research","research_review")
    builder.add_conditional_edges("research_review",
                                  route_after_research_review,
                                  {"research":"research","write":"write"})
    builder.add_edge("write","write_review")
    builder.add_conditional_edges("write_review",
                                  route_after_draft_review,
                                  {"write":"write","edit":"edit"})
    builder.add_edge("edit",END)

    graph = builder.compile(checkpointer=InMemorySaver())
    return graph
    ### Compile graph