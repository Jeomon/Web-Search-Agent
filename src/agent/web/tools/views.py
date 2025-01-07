from pydantic import BaseModel,Field
from typing import Literal

class Click(BaseModel):
    index:int = Field(...,description="the index of the element to click",examples=[0])

class Type(BaseModel):
    index:int = Field(...,description="the index of the element to type",examples=[0])
    text:str = Field(...,description="the text to type",examples=["hello world"])

class Wait(BaseModel):
    time:int = Field(...,description="the time to wait for the element to be visible in seconds",examples=[1])

class Scroll(BaseModel):
    direction:Literal['up','down'] = Field(...,description="the direction to scroll",examples=['up'])
    amount:int = Field(description="the amount to scroll, if None then page up or down",examples=[100],default=None)

class GoTo(BaseModel):
    url:str = Field(...,description="the url to navigate to",examples=["https://www.example.com"])

class Back(BaseModel):
    pass

class Key(BaseModel):
    keys:str = Field(...,description="the keys to type",examples=["Enter","Control+A","Backspace"])

class Download(BaseModel):
    url:str = Field(...,description="the url to download",examples=["https://www.example.com/file.txt"])

class ExtractContent(BaseModel):
    value:Literal['markdown','html','text'] = Field(description="the type of content to be like",examples=['markdown'],default='text')
