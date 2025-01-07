from src.agent.web.tools import click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool,extract_content_tool
from src.agent.web.utils import read_markdown_file,extract_agent_data
from src.message import SystemMessage,HumanMessage,ImageMessage,AIMessage
from src.agent.web.browser import Browser,BrowserConfig
from src.agent.web.context import Context,ContextConfig
from langgraph.graph import StateGraph,END,START
from src.agent.web.registry import Registry
from src.agent.web.state import AgentState
from src.inference import BaseInference
from src.agent import BaseAgent
from datetime import datetime
from termcolor import colored
from typing import Literal
from pathlib import Path
import nest_asyncio
import asyncio
import json

tools=[click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool,extract_content_tool]

class WebSearchAgent(BaseAgent):
    def __init__(self,browser:Literal['chromium','firefox','edge']='edge',instructions:list=[],llm:BaseInference=None,max_iteration:int=10,use_screenshot:bool=False,headless:bool=True,verbose:bool=False) -> None:
        self.name='Web Search Agent'
        self.description='This agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.'
        self.system_prompt=read_markdown_file('./src/agent/web/prompt/system.md')
        self.human_prompt=read_markdown_file('./src/agent/web/prompt/human.md')
        self.browser=Browser(BrowserConfig(browser=browser,headless=headless))
        self.instructions=self.get_instructions(instructions)
        self.context=Context(self.browser,ContextConfig())
        self.use_screenshot=use_screenshot
        self.max_iteration=max_iteration
        self.registry=Registry(tools)
        self.verbose=verbose
        self.iteration=0
        self.llm=llm
        self.graph=self.create_graph()

    def get_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    async def reason(self,state:AgentState):
        ai_message=await self.llm.async_invoke(state.get('messages'))
        agent_data=extract_agent_data(ai_message.content)
        thought=agent_data.get('Thought')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data,'messages':[ai_message],'route':route}

    async def action(self,state:AgentState):
        agent_data=state.get('agent_data')
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input=agent_data.get('Action Input')
        route=agent_data.get('Route')

        if self.verbose:
            print(colored(f'Action Name: {action_name}',color='blue',attrs=['bold']))
            print(colored(f'Action Input: {action_input}',color='blue',attrs=['bold']))
        action_result=await self.registry.execute(action_name,action_input,self.context)
        if self.verbose:
            print(colored(f'Observation: {action_result.content}',color='green',attrs=['bold']))
        state['messages'].pop() # Remove the last message for modification
        last_message=state['messages'][-1]
        if isinstance(last_message,ImageMessage):
            state['messages'][-1]=HumanMessage(f'<Observation>{last_message.content}</Observation>')

        browser_state=await self.context.get_state(use_vision=self.use_screenshot)
        image_obj=browser_state.screenshot

        ai_prompt=f'<Option>\n<Thought>{thought}</Thought>\n<Action-Name>{action_name}</Action-Name>\n<Action-Input>{json.dumps(action_input,indent=2)}</Action-Input>\n<Route>{route}</Route>\n</Option>'
        user_prompt=self.human_prompt.format(observation=action_result.content,current_url=browser_state.url,tabs=browser_state.tabs_to_string(),interactive_elements=browser_state.dom_state.elements_to_string())
        messages=[AIMessage(ai_prompt),ImageMessage(text=user_prompt,image_obj=image_obj) if self.use_screenshot else HumanMessage(user_prompt)]
        return {**state,'agent_data':agent_data,'messages':messages}

    def final(self,state:AgentState):
        agent_data=state.get('agent_data')
        final_answer=agent_data.get('Final Answer')
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer}
    def controller(self,state:AgentState):
        return state.get('route').lower()

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
        actions_prompt=self.registry.actions_prompt()
        current_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        messages=[SystemMessage(self.system_prompt.format(instructions=self.instructions,current_datetime=current_datetime,actions_prompt=actions_prompt)),HumanMessage(f'Task: {input}')]
        state={
            'input':input,
            'agent_data':{},
            'output':'',
            'messages':messages
        }
        response=await self.graph.ainvoke(state)
        await self.context.close_session()
        await self.browser.close_browser()
        return response.get('output')
        
    def invoke(self, input: str)->str:
        try:
            # If there's no running event loop, use asyncio.run
            return asyncio.run(self.async_invoke(input))
        except RuntimeError:
            nest_asyncio.apply()  # Allow nested event loops in notebooks
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.async_invoke(input))

    def stream(self, input:str):
        pass