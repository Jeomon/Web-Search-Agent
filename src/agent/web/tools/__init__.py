from src.agent.web.tools.views import Click,Type,Wait,Scroll,GoTo,Back,Key,Download,ExtractContent,Tab
from main_content_extractor import MainContentExtractor
from src.agent.web.context import Context
from typing import Literal
from src.tool import Tool
from pathlib import Path
import httpx

@Tool('Click Tool',params=Click)
async def click_tool(index:int,context:Context=None):
    '''For interacting with elements such as buttons, links, checkboxes, and dropdowns'''
    page=await context.get_current_page()
    element=await context.get_element_by_index(index)
    await element.scroll_into_view_if_needed()
    await element.click()
    await page.wait_for_load_state('load')
    return f'Clicked element {index}'


@Tool('Type Tool',params=Type)
async def type_tool(index:int,text:str,context:Context=None):
    '''To fill input fields or search boxes'''
    page=await context.get_current_page()
    element=await context.get_element_by_index(index)
    await element.scroll_into_view_if_needed()
    await element.type(text,delay=50)
    await page.wait_for_load_state('load')
    return f'Typed {text} in element {index}'

@Tool('Wait Tool',params=Wait)
async def wait_tool(time:int,context:Context=None):
    '''To wait until the page has fully loaded before proceeding'''
    page=await context.get_current_page()
    await page.wait_for_timeout(time*1000)
    return f'Waited for {time}s'

@Tool('Scroll Tool',params=Scroll)
async def scroll_tool(direction:str,amount:int=None,context:Context=None):
    '''To scroll the page by a certain amount or by a page'''
    page=await context.get_current_page()
    if direction=='up':
        if amount is None:
            await page.keyboard.press('PageUp')
        else:
            await page.mouse.wheel(0,-amount)
    elif direction=='down':
        if amount is None:
            await page.keyboard.press('PageDown')
        else:
            await page.mouse.wheel(0,amount)
    else:
        raise ValueError('Invalid direction')
    amount=amount if amount else 'one page'
    return f'Scrolled {direction} by {amount}'

@Tool('GoTo Tool',params=GoTo)
async def goto_tool(url:str,context:Context=None):
    '''To navigate directly to a specified URL.'''
    page=await context.get_current_page()
    await page.goto(url)
    await page.wait_for_load_state('load')
    return f'Navigated to {url}'

@Tool('Back Tool',params=Back)
async def back_tool(context:Context=None):
    '''To return to the previous page'''
    page=await context.get_current_page()
    await page.go_back()
    await page.wait_for_load_state('load')
    return 'Navigated to previous page'

@Tool('Key Tool',params=Key)
async def key_tool(keys:str,context:Context=None):
    '''To perform keyboard shorcuts'''
    page=await context.get_current_page()
    await page.keyboard.press(keys)
    return f'Pressed {keys}'

@Tool('Download Tool',params=Download)
async def download_tool(url:str,filename:str,context:Context=None):
    '''To download a file (e.g., pdf, image, video, audio) to the system'''
    Path('./downloads').mkdir(parents=True,exist_ok=True)
    async with httpx.AsyncClient() as client:
        response=await client.get(url)
        with open(f'./downloads/{filename}','wb') as f:
            f.write(response.content)
    return f'Downloaded {filename} from {url}'

@Tool('ExtractContent Tool',params=ExtractContent)
async def extract_content_tool(value:str,context:Context=None):
    '''Extract the information present in a webpage such as text, images, etc'''
    page=await context.get_current_page()
    html=await page.content()
    content=MainContentExtractor.extract(html,output_format=value)
    return f'Extracted Page Content:\n{content}'

@Tool('Tab Tool',params=Tab)
async def tab_tool(mode:Literal['open','close','switch'],index:int=None,context:Context=None):
    '''To open a new tab, close the current tab or switch to a specified tab'''
    session=await context.get_session()
    if mode=='open':
        page=await session.context.new_page()
        session.current_page=page
        await page.wait_for_load_state('load')
        return f'Opened new tab and switched to it'
    elif mode=='close':
        page=session.current_page
        await page.close()
        pages=session.context.pages
        if index is not None and index>len(pages):
            raise IndexError('Index out of range')
        page=pages[0]
        session.current_page=page
        await page.bring_to_front()
        await page.wait_for_load_state('load')
        return f'Closed current tab and switched to tab 0'
    elif mode=='switch':
        pages=session.context.pages
        if index>len(pages):
            raise IndexError('Index out of range')
        page=pages[index]
        session.current_page=page
        await page.bring_to_front()
        await page.wait_for_load_state('load')
        return f'Switched to tab {index}'
    else:
        raise ValueError('Invalid mode')