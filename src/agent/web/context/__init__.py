from src.agent.web.browser import Browser
from src.agent.web.context.config import ContextConfig
from playwright.async_api import Page,Browser as PlaywrightBrowser,ElementHandle
from src.agent.web.context.views import BrowserSession,BrowserState,Tab
from src.agent.web.dom import DOM
from src.agent.web.dom.views import DOMElementNode
from uuid import uuid4
from base64 import b64encode
from pathlib import Path
from datetime import datetime

class Context:
    def __init__(self,browser:Browser,config:ContextConfig=ContextConfig()):
        self.browser=browser
        self.config=config
        self.context_id=str(uuid4())
        self.session:BrowserSession=None

    async def __aenter__(self):
        await self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()

    async def close_session(self):
        try:
            await self.session.context.close()
        except Exception as e:
            print('Context failed to close',e)
        finally:
            self.browser_context=None

    async def init_session(self):
        playwright_browser=await self.browser.get_playwright_browser()
        context=await self.setup_context(playwright_browser)
        page=await context.new_page()
        state=await self.initial_state(page)
        self.session=BrowserSession(context,page,state)
        
    async def initial_state(self,page:Page):
        dom_state=[]
        tabs=[]
        screenshot=None
        state=BrowserState(url=page.url,title=await page.title(),tabs=tabs,screenshot=screenshot,dom_state=dom_state)
        return state
    
    async def update_state(self,use_vision:bool=False):
        page=await self.get_current_page()
        dom=DOM(page)
        dom_state=await dom.get_state()
        print(dom_state.elements_to_string())
        tabs=await self.get_tabs()
        if use_vision:
            with open('./src/agent/web/dom/script.js') as f:
                script=f.read()
            # Loading the script
            await self.execute_script(script)
            nodes=[node.to_dict() for node in dom_state.nodes]
            # Add bounding boxes to the interactive elements
            await self.execute_script('nodes=>{mark_page(nodes)}',nodes)
            # Take screenshot
            screenshot=await self.get_screenshot(save_screenshot=False)
            # Remove bounding boxes
            await self.execute_script('unmark_page()')
        else:
            screenshot=None
        state=BrowserState(url=page.url,title=await page.title(),tabs=tabs,screenshot=screenshot,dom_state=dom_state)
        return state
    
    async def get_state(self,use_vision=False)->BrowserState:
        session=await self.get_session()
        state=await self.update_state(use_vision=use_vision)
        session.state=state
        return session.state
    
    async def get_session(self)->BrowserSession:
        if self.session is None:
            await self.init_session()
        return self.session
    
    async def get_current_page(self)->Page:
        session=await self.get_session()
        return session.current_page
        
    async def setup_context(self,browser:PlaywrightBrowser):
        parameters={
            'no_viewport':False,
            'ignore_https_errors':self.config.disable_security,
            'user_agent':self.config.user_agent,
            'java_script_enabled':True,
            'bypass_csp':self.config.disable_security,
        }
        context=await browser.new_context(**parameters)
        with open('./src/agent/web/context/script.js') as f:
            script=f.read()
        await context.add_init_script(script)
        return context
    
    async def get_selector_map(self)->dict[int,DOMElementNode]:
        session=await self.get_session()
        return session.state.dom_state.selector_map

    async def get_element_by_index(self,index:int)->ElementHandle:
        selector_map=await self.get_selector_map()
        element=selector_map.get(index)
        print(element)
        element_handle=await self.locate_element(element)
        return element_handle

    async def locate_element(self,element:DOMElementNode)->ElementHandle:
        page=await self.get_current_page()
        element_handle=await page.get_by_role(role=element.role,name=element.name).first.element_handle()
        if element_handle is None:
            raise Exception('Element not found')
        await element_handle.scroll_into_view_if_needed()
        return element_handle
    
    async def get_tabs(self)->list[Tab]:
        session=await self.get_session()
        pages=session.context.pages
        return [Tab(index,page.url,await page.title()) for index,page in enumerate(pages)]

    
    async def execute_script(self,script:str,args:list=None):
        page=await self.get_current_page()
        return await page.evaluate(script,args)
    
    async def get_screenshot(self,save_screenshot:bool=False,full_page:bool=False):
        page=await self.get_current_page()
        if save_screenshot:
            date_time=datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            path=Path('./screenshots')
            path.mkdir(parents=True,exist_ok=True)
            path=path.joinpath(f'screenshot_{date_time}.jpeg')
        else:
            path=None
        await page.wait_for_timeout(2*1000)
        screenshot=await page.screenshot(path=path,full_page=full_page,animations='disabled',type='jpeg')
        return b64encode(screenshot).decode('utf-8')
    




    


