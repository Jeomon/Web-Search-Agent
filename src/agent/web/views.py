from pydantic import BaseModel,Field,ConfigDict
from typing import Callable,Type

class Action(BaseModel):
    name:str=Field(...,description="the name of the action")
    description:str=Field(...,description="the description of the action")
    params:Type[BaseModel]
    function:Callable
    model_config=ConfigDict(arbitrary_types_allowed=True)

class ActionResult(BaseModel):
    name: str = Field(...,description="the action taken")
    content: str = Field(...,description="the output of the action")

class AgentStep(BaseModel):
    step:int=Field(...,description='number of steps took so far')
    max_step:int=Field(...,description='maximum number of steps allowed')

class AgentResponse(BaseModel):
    response: str = Field(...,description="the response from the agent")