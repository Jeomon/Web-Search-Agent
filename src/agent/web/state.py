from typing import TypedDict,Annotated
from playwright.async_api import Page
from src.message import BaseMessage
from operator import add

class AgentState(TypedDict):
    input:str
    page: Page|None
    agent_data:dict
    bboxes:list[dict]
    output:str
    messages: Annotated[list[BaseMessage],add]