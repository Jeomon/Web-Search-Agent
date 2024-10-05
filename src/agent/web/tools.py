from src.tool import tool
from pydantic import BaseModel, Field
from playwright.sync_api import Page

class Click(BaseModel):
    pass

@tool('Click Tool',args_schema=Click)
async def click_tool(page:Page,x:float,y:float):
    await page.mouse.click(x,y,button='left')
    return (page,'Clicked the Button.')

class GoTo(BaseModel):
    pass

@tool('GoTo Tool',args_schema=GoTo)
async def goto_tool(page:Page,url:str):
    await page.goto(url=url)
    return (page,f'Gone to {url}.')

class Type(BaseModel):
    pass

@tool('Type Tool',args_schema=Type)
async def type_tool(page:Page,x:float,y:float,text:str):
    await page.mouse.click(x,y,button='left')
    await page.keyboard.type(text)
    await page.keyboard.press('Enter')
    return (page,f'Typed {text}.')

class Scroll(BaseModel):
    pass

@tool('Scroll Tool',args_schema=Scroll)
async def scroll_tool(page:Page,direction:str,amount:int):
    if direction=='up':
        await page.mouse.wheel(0,amount)
    else:
        await page.mouse.wheel(0,amount)
    return (page,f'Scrolled {direction} by {amount}.')

class Wait(BaseModel):
    pass

@tool('Wait Tool',args_schema=Wait)
async def wait_tool(page:Page,duration:int):
    await page.wait_for_timeout(duration*1000)
    return (page,f'Waited for {duration} seconds.')

class Back(BaseModel):
    pass

@tool('Back Tool',args_schema=Back)
async def back_tool(page:Page):
    await page.go_back()
    return (page,'Gone back.')
