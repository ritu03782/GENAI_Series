import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

### GET LLM
def get_llm(model_name:str="openai/gpt-oss-20b" , temperature:float = 0.5):
    api_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(model=model_name, temperature=temperature, api_key=api_key)
    return llm


### Research Agent
RESEARCHER_PROMPT = ChatPromptTemplate.from_messages([
    {"role":"system", "content":"""
      "You are a Research Agent. Given a blog topic and target audience , produce a clear,"
      "structured research outline. Include:\n"
      "1, 5-7 key points the blog should cover\n"
      "2, Important facts, stats, or examples for each point\n"
      "3, Suggested angle or hook\n"
      "Be concise. Use bullet points. Do NOT write the full blog yet."
     """},
    {"role":"user", "content":"Topic:{topic} , "
     "Audience:{audience}, {research_hints}, Write the research outline now."}
])

def researcher_agent(llm:ChatGroq, topic:str, audience:str, research_fb:str="")->str:
    research_hints = f"The human provided this feedback on your previous research - please address it: {research_fb}"
    if not research_fb:
        research_hints = "This is your first attempt"
    chain = RESEARCHER_PROMPT|llm
    result = chain.invoke({
        "topic":topic,
        "audience":audience,
        "research_hints":research_hints
    })
    return result.content

### WRITER AGENT
WRITER_PROMPT = ChatPromptTemplate.from_messages([
    {"role":"system", "content":"""
      "You are a Blog Writer Agent. Using the research notes provided, write a complete,"
      "engaging blog post.\n"
      "Rules:\n"
      "1, Length 500-800 words\n"
      "2, Structure: catchy tittle, intro hook, 3-5 sections with H2 headings, conclusion\n"
      "3, Tone: clear, friendly, suited to the target audience\n"
      "4, Use markdown formatting\n"
      "5, Do NOT add a word count line at the end"
     """},
    {"role":"user", "content":"""
            Topic:{topic},
            Audience: {audience}
            Research Noted :{research}
            {revision_hints}
            Write full blog post now
    """}
])
def writer_agent(llm:ChatGroq, topic:str, audience:str, research:str="",draft_fb:str="")->str:
    revision_hints = f"The human provided this feedback on your previous draft and asked for these changes: {draft_fb}. Please apply these changes during writting the vlog"
    if not draft_fb :
        revision_hints = "This is your first attempt"
    chain = WRITER_PROMPT|llm
    result = chain.invoke({
        "topic":topic,
        "audience":audience,
        "research":research,
        "revision_hints":revision_hints
    })
    return result.content

#### Editor Agent:
EDITOR_PROMPT = ChatPromptTemplate.from_messages([
    {"role":"system", "content":"""
      "You are an editor agent. The final quality gate before publishing.\n"
      "Take the draft and produce the FINAL polished version.Specifically:\n"
      "- Fix grammar, spelling, and awkward phrasing\n"
      "- Tighten wordy sentences\n"
      "- Improve flow and transitions between sections\n"
      "- Make the title and intro more compelling if needed\n"
      "- Keep the same structure and rigorous formatting\n"
      "- Blog Wording should look like human, not a AI and don't use any special chars and complex / fancy words.\n"
      "Output only the final polished blog post - no commentary\n"
     """},
    {"role":"user", "content":"""
            Topic:{topic},
            Draft :{draft}
            
            Return the published blog post
    """}
])

def editor_agent(llm:ChatGroq, topic:str, draft:str = "")->str:
    chain = EDITOR_PROMPT|llm
    result = chain.invoke({
        "topic":topic,
        "draft":draft
    })
    return result.content