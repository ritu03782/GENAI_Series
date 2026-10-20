from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field

class BlogState(BaseModel):
    topic:str = Field(description="User topic to generate blog", default="") 
    audience:str=Field(description="Type of audience", default="general reader")
    ### Researcher Output
    research:str = Field(description="Research on topic", default="")
    research_fb:str = Field(description="Feedback from user", default ="")
    ### Writer Output
    draft:str = Field(description="Blog written", default="")
    draft_fb:str = Field(description="Feedback from user", default = "")
    ### Editor Output
    final_blog:str = Field(description="Final Blog written ", default="")
    ### Metadata
    revision_count : int =  Field(description="Number of times feedback given ", default=0)