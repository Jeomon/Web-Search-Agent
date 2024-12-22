from src.tool import Tool
from playwright.sync_api import Page
from pathlib import Path

@Tool('Click Tool')
async def click_tool(page:Page,x:float,y:float):
    await page.mouse.click(x,y,button='left')
    return 'Clicked the Button.'

@Tool('GoTo Tool')
async def goto_tool(page:Page,url:str):
    await page.goto(url=url,wait_until='domcontentloaded')
    return f'Gone to {url}.'

@Tool('Type Tool')
async def type_tool(page:Page,x:float,y:float,text:str):
    await page.mouse.click(x,y,button='left')
    await page.keyboard.type(text)
    # await page.keyboard.press(key='Enter')
    return f'Typed {text}.'

@Tool('Scroll Tool')
async def scroll_tool(page:Page,direction:str,amount:int):
    if direction=='up':
        await page.mouse.wheel(0,amount)
    else:
        await page.mouse.wheel(0,amount)
    return f'Scrolled {direction} by {amount}.'

@Tool('Wait Tool')
async def wait_tool(page:Page,duration:int):
    await page.wait_for_timeout(duration*1000)
    return f'Waited for {duration} seconds.'

@Tool('Back Tool')
async def back_tool(page:Page):
    await page.go_back()
    return 'Gone back.'

@Tool('Right Click Tool')
async def right_click_tool(page:Page,x:float,y:float):
    await page.mouse.click(x,y,button='right')
    return 'Right Clicked the Button.'

@Tool('Download Tool')
async def download_tool(page:Page,url:str):
    Path('./downloads').mkdir(exist_ok=True)
    async with page.expect_download() as download_info:
        await page.goto(url)
    download=await download_info.value
    save_path=Path(f'./downloads/{download.suggested_filename}')
    await download.save_as(save_path)
    return f'Downloaded {download.suggested_filename} to ./downloads.'

@Tool('Key Tool')
async def key_tool(page:Page,key:str):
    await page.keyboard.press(key)
    return f'Pressed {key}.'