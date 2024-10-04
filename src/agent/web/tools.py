from src.tool import tool
from pydantic import BaseModel, Field
from playwright.sync_api import Page

class Click(BaseModel):
    pass

@tool('Click Tool',args_schema=Click)
def click_tool(page:Page,x:float,y:float):
    page.mouse.click(x,y,button='left')
    return (page,'Clicked the Button.')

class GoTo(BaseModel):
    pass

@tool('GoTo Tool',args_schema=GoTo)
def goto_tool(page:Page,url:str):
    page.goto(url=url)
    return (page,f'Gone to {url}.')

class Type(BaseModel):
    pass

@tool('Type Tool',args_schema=Type)
def type_tool(page:Page,x:float,y:float,text:str):
    page.mouse.click(x,y,button='left')
    page.keyboard.type(text)
    page.keyboard.press('Enter')
    return (page,f'Typed {text}.')

class Scroll(BaseModel):
    pass

@tool('Scroll Tool',args_schema=Scroll)
def scroll_tool(page:Page,direction:str,amount:int):
    if direction=='up':
        page.mouse.wheel(0,amount)
    else:
        page.mouse.wheel(0,amount)
    return (page,f'Scrolled {direction} by {amount}.')

class Wait(BaseModel):
    pass

@tool('Wait Tool',args_schema=Wait)
def wait_tool(page:Page,duration:int):
    page.wait_for_timeout(duration*1000)
    return (page,f'Waited for {duration} seconds.')

class Back(BaseModel):
    pass

@tool('Back Tool',args_schema=Back)
def back_tool(page:Page):
    page.go_back()
    return (page,'Gone back.')
