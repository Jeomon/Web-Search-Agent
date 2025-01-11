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
    index:int = Field(...,description="the index of the element to download file",examples=[0])
    url:str = Field(...,description="url of the file to download",examples=["https://www.example.com/file.txt","https://abc.org/pdf/54655"])
    filename:str=Field(...,description="the name of the file to download",examples=["file.txt","xy4rs.pdf"])

class ExtractContent(BaseModel):
    value:Literal['markdown','html','text'] = Field(description="the type of content to be like",examples=['markdown'],default='text')

class Tab(BaseModel):
    mode:Literal['open','close','switch'] = Field(...,description="the mode of the tab",examples=['open'])
    index:int = Field(description="switch to the specified index of the tab",examples=[0],default=None)

class File(BaseModel):
    index:int = Field(...,description="the index of the element to upload file",examples=[0])
    filenames:list[str] = Field(...,description="list of filenames of the files to upload",examples=[["file.txt"]])
