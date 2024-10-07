from src.agent.web.tools import click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool
from src.agent.web.utils import read_markdown_file,extract_llm_response
from src.message import SystemMessage,HumanMessage,ImageMessage,AIMessage
from playwright.async_api import async_playwright
from langgraph.graph import StateGraph,END,START
from src.agent.web.state import AgentState
from src.inference import BaseInference
from src.agent import BaseAgent
from datetime import datetime
from termcolor import colored
from base64 import b64encode
from typing import Literal
from pathlib import Path
import asyncio
import json

class WebSearchAgent(BaseAgent):
    def __init__(self,browser:Literal['chromium','firefox','edge']='chromium',instructions=[],llm:BaseInference=None,screenshot=False,viewport:tuple[int,int]=(1920,1080),max_iteration=10,headless=True,verbose=False) -> None:
        self.name='Web Search Agent'
        self.description=''
        self.headless=headless
        self.instructions=self.get_instructions(instructions)
        self.system_prompt=read_markdown_file('./src/agent/web/prompt.md')
        tools=[click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool]
        self.tool_names=[tool.name for tool in tools]
        self.tools={tool.name:tool for tool in tools}
        self.browser=browser
        self.max_iteration=max_iteration
        self.iteration=0
        self.llm=llm
        self.screenshot=screenshot
        self.viewport=viewport
        self.verbose=verbose
        self.graph=self.create_graph()
        self.cordinates=None
        self.wait_time=5000
        with open('./src/agent/web/bounding_box.js','r') as js:
            self.js_script=js.read()

    def get_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    async def reason(self,state:AgentState):
        llm_response=await self.llm.async_invoke(state.get('messages'))
        # print(llm_response.content)
        agent_data=extract_llm_response(llm_response.content)
        if self.verbose:
            thought=agent_data.get('Thought')
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data}

    def element_finder(self,state:AgentState,label:str):
        x,y=None,None
        for bbox in state.get('bboxes'):
            if bbox.get('label_number')==label:
                x,y=bbox.get('x'),bbox.get('y')
                break
        if x is None or y is None:
            raise Exception('Bounding Box not found')
        return x,y

    async def action(self,state:AgentState):
        agent_data=state.get('agent_data')
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input=agent_data.get('Action Input')
        route=agent_data.get('Route')
        page=state.get('page')
        if self.verbose:
            print(colored(f'Action Name: {action_name}',color='blue',attrs=['bold']))
            print(colored(f'Action Input: {action_input}',color='blue',attrs=['bold']))
        tool=self.tools[action_name]
        if action_name=='GoTo Tool':
            page,observation=await tool(page,**action_input)
            await page.wait_for_timeout(self.wait_time)
        elif action_name=='Click Tool':
            label=action_input.get('label_number')
            page,observation=await tool(page,*self.element_finder(state,label))
            await page.wait_for_timeout(self.wait_time)
        elif action_name=='Type Tool':
            label=action_input.get('label_number')
            text=action_input.get('content')
            page,observation=await tool(page,*self.element_finder(state,label),text=text)
            await page.wait_for_timeout(self.wait_time)
        elif action_name=='Scroll Tool':
            direction=action_input.get('direction')
            amount=int(action_input.get('amount'))
            page,observation=await tool(page,direction,amount)
            await page.wait_for_timeout(self.wait_time)
        elif action_name=='Wait Tool':
            duration=int(action_input.get('duration'))
            page,observation=await tool(page,duration)
            await page.wait_for_timeout(self.wait_time)
        else:
            raise Exception('Tool not found')
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        # await asyncio.sleep(10) #Wait for 10 seconds
        await page.wait_for_load_state('domcontentloaded')
        await page.evaluate(self.js_script)
        cordinates=await page.evaluate('mark_page()')
        if self.screenshot:
            date_time=datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            path=Path('./screenshots')
            if not path.exists():
                path.mkdir(parents=True,exist_ok=True)
            path=path.joinpath(f'screenshot_{date_time}.jpeg').as_posix()
            bytes=await page.screenshot(path=path,type='jpeg',full_page=False)
        else:
            bytes=await page.screenshot(type='jpeg',full_page=False)
            await page.evaluate('unmark_page()')
        state['messages'].pop()
        image_obj=b64encode(bytes).decode('utf-8')
        bboxes=[{'element_type':bbox.get('elementType'),'label_number':bbox.get('label'),'x':bbox.get('x'),'y':bbox.get('y')} for bbox in cordinates]
        ai_prompt=f'<Thought>{thought}</Thought>\n<Action-Name>{action_name}</Action-Name>\n<Action-Input>{json.dumps(action_input,indent=2)}</Action-Input>\n<Route>{route}</Route>'
        user_prompt=f'<Observation>{observation} Now analyze the given screenshot for gathering information and decide whether to act or answer.</Observation>'
        messages=[AIMessage(ai_prompt),ImageMessage(text=user_prompt,image_base_64=image_obj)]
        return {**state,'agent_data':agent_data,'messages':messages,'bboxes':bboxes,'page':page}

    def final(self,state:AgentState):
        agent_data=state.get('agent_data')
        final_answer=agent_data.get('Final Answer')
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer}

    def controller(self,state:AgentState):
        agent_data=state.get('agent_data')
        return agent_data.get('Route').lower()
    
    def create_graph(self):
        graph=StateGraph(AgentState)
        graph.add_node('reason',self.reason)
        graph.add_node('action',self.action)
        graph.add_node('final',self.final)

        graph.add_edge(START,'reason')
        graph.add_conditional_edges('reason',self.controller)
        graph.add_edge('action','reason')
        graph.add_edge('final',END)

        return graph.compile(debug=False)

    async def async_invoke(self, input: str):
        playwright=await async_playwright().start()
        width,height=self.viewport
        args=["--window-position=0,0",f"--window-size={width},{height}"]
        if self.browser=='chromium':
            browser=await playwright.chromium.launch(headless=self.headless,slow_mo=500,args=args)
        elif self.browser=='firefox':
            browser=await playwright.firefox.launch(headless=self.headless,slow_mo=500,args=args)
        elif self.browser=='edge':
            browser=await playwright.chromium.launch(channel='msedge',headless=self.headless,slow_mo=500,args=args)
        else:
            raise ValueError('Browser not found')
        page=await browser.new_page()
        state={
            'input':input,
            'page':page,
            'agent_data':{},
            'output':'',
            'messages':[SystemMessage(self.system_prompt),HumanMessage(input)]
        }
        response=await self.graph.ainvoke(state)
        await page.close()
        await browser.close()
        await playwright.stop()
        return response['output']

    def invoke(self, input: str)->str:
        return asyncio.run(self.async_invoke(input))

    def stream(self, input:str):
        pass