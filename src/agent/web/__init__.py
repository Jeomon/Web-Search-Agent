from src.agent.web.tools import click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool
from src.message import SystemMessage,HumanMessage,ImageMessage,AIMessage
from src.agent.web.utils import read_markdown_file,extract_llm_response
from src.agent.web.ally_tree import build_a11y_tree
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
    def __init__(self,browser:Literal['chromium','firefox','edge']='chromium',instructions:list=[],llm:BaseInference=None,screenshot:bool=False,strategy:Literal['ally_tree','screenshot','combined']='ally_tree',viewport:tuple[int,int]=(1920,1080),max_iteration:int=10,headless:bool=True,verbose:bool=False) -> None:
        self.name='Web Search Agent'
        self.description='This agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.'
        self.headless=headless
        self.instructions=self.get_instructions(instructions)
        self.system_prompt=read_markdown_file(f'./src/agent/web/prompt/{strategy}.md')
        tools=[click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool]
        self.tool_names=[tool.name for tool in tools]
        self.tools={tool.name:tool for tool in tools}
        self.max_iteration=max_iteration
        self.screenshot=screenshot
        self.strategy=strategy
        self.viewport=viewport
        self.browser=browser
        self.verbose=verbose
        self.iteration=0
        self.llm=llm
        self.graph=self.create_graph()
        self.wait_time=5000
        with open('./src/agent/web/bounding_box.js','r') as js:
            self.js_script=js.read()

    def get_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    async def reason(self,state:AgentState):
        ai_message=await self.llm.async_invoke(state.get('messages'))
        # print(ai_message.content)
        agent_data=extract_llm_response(ai_message.content)
        if self.verbose:
            thought=agent_data.get('Thought')
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data,'messages':[ai_message]}

    def find_element_by_label(self,state:AgentState,label_number:str):
        x,y=None,None
        for bbox in state.get('bboxes'):
            if bbox.get('label_number')==label_number:
                x,y=bbox.get('x'),bbox.get('y')
                break
        if x is None or y is None:
            raise Exception('Label is invalid')
        return x,y
    
    def find_element_by_role_and_name(self,state:AgentState,role:str,name:str):
        x,y=None,None
        for bbox in state.get('bboxes'):
            if bbox.get('role').strip()==role.strip() and bbox.get('name').strip()==name.strip():
                x,y=bbox.get('x'),bbox.get('y')
                break
        if x is None or y is None:
            raise Exception('Role or Name is invalid. Either change the role or name.')
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
        if self.strategy=='screenshot':
            try:
                if action_name=='GoTo Tool':
                    observation=await tool(page,**action_input)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Click Tool':
                    label=action_input.get('label_number')
                    observation=await tool(page,*self.find_element_by_label(state,label))
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Right Click Tool':
                    observation=await tool(page,*self.find_element_by_label(state,label))
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Type Tool':
                    label=action_input.get('label_number')
                    text=action_input.get('content')
                    observation=await tool(page,*self.find_element_by_label(state,label),text=text)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Scroll Tool':
                    direction=action_input.get('direction')
                    amount=int(action_input.get('amount'))
                    observation=await tool(page,direction,amount)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Wait Tool':
                    duration=int(action_input.get('duration'))
                    observation=await tool(page,duration)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Back Tool':
                    observation=await tool(page)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Key Tool':
                    key=action_input.get('key')
                    observation=await tool(page,key)
                    await page.wait_for_timeout(self.wait_time)
                else:
                    raise Exception('Tool not found')
            except Exception as e:
                observation=str(e)
        else:
            try:
                if action_name=='GoTo Tool':
                    observation=await tool(page,**action_input)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Click Tool':
                    role=action_input.get('role')
                    name=action_input.get('name')
                    observation=await tool(page,*self.find_element_by_role_and_name(state,role,name))
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Right Click Tool':
                    role=action_input.get('role')
                    name=action_input.get('name')
                    observation=await tool(page,*self.find_element_by_role_and_name(state,role,name))
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Type Tool':
                    role=action_input.get('role')
                    name=action_input.get('name')
                    text=action_input.get('content')
                    observation=await tool(page,*self.find_element_by_role_and_name(state,role,name),text=text)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Scroll Tool':
                    direction=action_input.get('direction')
                    amount=int(action_input.get('amount'))
                    observation=await tool(page,direction,amount)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Wait Tool':
                    duration=int(action_input.get('duration'))
                    observation=await tool(page,duration)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Back Tool':
                    observation=await tool(page)
                    await page.wait_for_timeout(self.wait_time)
                elif action_name=='Key Tool':
                    key=action_input.get('key')
                    observation=await tool(page,key)
                    await page.wait_for_timeout(self.wait_time)
                else:
                    raise Exception('Tool not found')
            except Exception as e:
                observation=str(e)
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        await asyncio.sleep(10) #Wait for 10 seconds

        if self.strategy=='screenshot':
            state['messages'].pop() # Remove the last message for modification
            last_message=state['messages'][-1]
            if isinstance(last_message,ImageMessage):
                state['messages'][-1]=HumanMessage(f'<Observation>{state.get('previous_observation')}</Observation>')
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
            image_obj=b64encode(bytes).decode('utf-8')
            bboxes=[{'element_type':bbox.get('elementType'),'label_number':bbox.get('label'),'x':bbox.get('x'),'y':bbox.get('y')} for bbox in cordinates]
            ai_prompt=f'<Thought>{thought}</Thought>\n<Action-Name>{action_name}</Action-Name>\n<Action-Input>{json.dumps(action_input,indent=2)}</Action-Input>\n<Route>{route}</Route>'
            user_prompt=f'<Observation>{observation}\nNow analyze and evaluate the new labelled screenshot got from the previous action, think whether to act or answer.</Observation>'
            messages=[AIMessage(ai_prompt),ImageMessage(text=user_prompt,image_bytes=image_obj)]
        elif self.strategy=='ally_tree':
            state['messages'].pop() # Remove the last message for modification
            last_message=state['messages'][-1]
            if isinstance(last_message,HumanMessage):
                state['messages'][-1]=HumanMessage(f'<Observation>{state.get('previous_observation')}</Observation>')
            snapshot=await page.accessibility.snapshot(interesting_only=True)
            # print(snapshot)
            ally_tree, bboxes =await build_a11y_tree(snapshot, page)
            # print(ally_tree)
            ai_prompt=f'<Thought>{thought}</Thought>\n<Action-Name>{action_name}</Action-Name>\n<Action-Input>{json.dumps(action_input,indent=2)}</Action-Input>\n<Route>{route}</Route>'
            user_prompt=f'<Observation>{observation}\nAlly tree:\n{ally_tree}\nNow analyze and evaluate the new ally tree got from the previous action, think whether to act or answer.</Observation>'
            messages=[AIMessage(ai_prompt),HumanMessage(user_prompt)]
        else:
            if self.screenshot:
                date_time=datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                path=Path('./screenshots')
                if not path.exists():
                    path.mkdir(parents=True,exist_ok=True)
                path=path.joinpath(f'screenshot_{date_time}.jpeg').as_posix()
                bytes=await page.screenshot(path=path,type='jpeg',full_page=False)
            else:
                bytes=await page.screenshot(type='jpeg',full_page=False)
            image_obj=b64encode(bytes).decode('utf-8')
            state['messages'].pop() # Remove the last message for modification
            last_message=state['messages'][-1]
            if isinstance(last_message,ImageMessage):
                state['messages'][-1]=HumanMessage(f'<Observation>{state.get('previous_observation')}</Observation>')
            snapshot=await page.accessibility.snapshot(interesting_only=True)
            # print(snapshot)
            ally_tree, bboxes =await build_a11y_tree(snapshot, page)
            # print(ally_tree,bboxes)
            ai_prompt=f'<Thought>{thought}</Thought>\n<Action-Name>{action_name}</Action-Name>\n<Action-Input>{json.dumps(action_input,indent=2)}</Action-Input>\n<Route>{route}</Route>'
            user_prompt=f'<Observation>{observation}\nAlly tree:\n{ally_tree}\nNow analyze and evaluate the new ally tree and screenshot got from the previous action, think whether to act or answer.</Observation>'
            messages=[AIMessage(ai_prompt),ImageMessage(user_prompt,image_bytes=image_obj)]
        return {**state,'agent_data':agent_data,'messages':messages,'bboxes':bboxes,'page':page,'previous_observation':observation}

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
            browser=await playwright.chromium.launch(headless=self.headless,slow_mo=100,args=args)
        elif self.browser=='firefox':
            browser=await playwright.firefox.launch(headless=self.headless,slow_mo=100,args=args)
        elif self.browser=='edge':
            browser=await playwright.chromium.launch(channel='msedge',headless=self.headless,slow_mo=100,args=args)
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