from src.agent.web.tools import click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool,extract_content_tool,download_tool,tab_tool,upload_tool,menu_tool,form_tool
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
from getpass import getuser
from typing import Literal
from src.tool import Tool
from pathlib import Path
from os import getcwd
import nest_asyncio
import asyncio
import json

main_tools=[
    menu_tool,click_tool,form_tool,
    goto_tool,type_tool,scroll_tool,
    wait_tool,back_tool,key_tool,
    download_tool,tab_tool,upload_tool
]

class WebAgent(BaseAgent):
    def __init__(self,browser:Literal['chrome','firefox','edge']='edge',additional_tools:list[Tool]=[],instructions:list=[],llm:BaseInference=None,max_iteration:int=10,use_vision:bool=False,headless:bool=True,verbose:bool=False,token_usage:bool=False) -> None:
        """
        Initialize a WebAgent instance.
        Args:
            browser (Literal['chrome', 'firefox', 'edge']): The browser to use for web automation. Defaults to 'edge'.
            additional_tools (list[Tool]): A list of additional tools to be used by the agent. Defaults to an empty list.
            instructions (list): A list of instructions for the agent to follow. Defaults to an empty list.
            llm (BaseInference): The language model inference engine used by the agent. Defaults to None.
            max_iteration (int): The maximum number of iterations the agent should perform. Defaults to 10.
            use_vision (bool): Whether to use vision capabilities for web interaction. Defaults to False.
            headless (bool): Whether to run the browser in headless mode. Defaults to True.
            verbose (bool): Whether to enable verbose to show agent's flow. Defaults to False.
            token_usage (bool): Whether to track token usage. Defaults to False.
        """
        self.name='Web Agent'
        self.description='The web agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.'
        self.system_prompt=read_markdown_file('./src/agent/web/prompt/system.md')
        self.human_prompt=read_markdown_file('./src/agent/web/prompt/human.md')
        self.browser=Browser(BrowserConfig(browser=browser,headless=headless,user_data_dir=Path(getcwd()).joinpath(f'./user_data/{browser}/{getuser()}').as_posix()))
        self.ai_prompt=read_markdown_file('./src/agent/web/prompt/ai.md')
        self.instructions=self.format_instructions(instructions)
        self.context=Context(self.browser,ContextConfig())
        self.max_iteration=max_iteration
        self.registry=Registry(main_tools+additional_tools)
        self.use_vision=use_vision
        self.token_usage=token_usage
        self.verbose=verbose
        self.iteration=0
        self.llm=llm
        self.graph=self.create_graph()

    def format_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    async def reason(self,state:AgentState):
        "Call LLM to make decision"
        ai_message=await self.llm.async_invoke(state.get('messages'))
        # print(ai_message.content)
        agent_data=extract_agent_data(ai_message.content)
        thought=agent_data.get('Thought')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data,'messages':[ai_message],'route':route}

    async def action(self,state:AgentState):
        "Execute the provided action"
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
        last_message=state['messages'][-1] #ImageMessage/HumanMessage
        if isinstance(last_message,ImageMessage):
            state['messages'][-1]=HumanMessage(f'<Observation>{state.get('prev_observation')}</Observation>')
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
        # Get the current browser state
        browser_state=await self.context.get_state(use_vision=self.use_vision)
        image_obj=browser_state.screenshot
        # print('Tabs',browser_state.tabs_to_string())
        # Redefining the AIMessage and adding the new observation
        ai_prompt=self.ai_prompt.format(thought=thought,action_name=action_name,action_input=json.dumps(action_input,indent=2),route=route)
        user_prompt=self.human_prompt.format(observation=action_result.content,current_url=browser_state.url,tabs=browser_state.tabs_to_string(),interactive_elements=browser_state.dom_state.elements_to_string())
        messages=[AIMessage(ai_prompt),ImageMessage(text=user_prompt,image_obj=image_obj) if self.use_vision else HumanMessage(user_prompt)]
        return {**state,'agent_data':agent_data,'messages':messages,'prev_observation':action_result.content}

    def final(self,state:AgentState):
        "Give the final answer"
        agent_data=state.get('agent_data')
        final_answer=agent_data.get('Final Answer')
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer}
    def controller(self,state:AgentState):
        return state.get('route').lower()

    def create_graph(self):
        "Create the graph"
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
        system_prompt=self.system_prompt.format(instructions=self.instructions,current_datetime=current_datetime,actions_prompt=actions_prompt)
        human_prompt=f'Task: {input}'
        messages=[SystemMessage(system_prompt),HumanMessage(human_prompt)]
        state={
            'input':input,
            'agent_data':{},
            'output':'',
            'messages':messages
        }
        response=await self.graph.ainvoke(state)
        await self.close()
        return response.get('output')
        
    def invoke(self, input: str)->str:
        """
        Invoke the agent to perform a task.
        Args:
            input (str): The input task
        Returns:
            str: The final answer
        """
        try:
            # If there's no running event loop, use asyncio.run
            return asyncio.run(self.async_invoke(input))
        except RuntimeError:
            nest_asyncio.apply()  # Allow nested event loops in notebooks
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.async_invoke(input))

    def stream(self, input:str):
        pass

    async def close(self):
        '''Close the browser and context followed by clean up'''
        try:
            await self.context.close_session()
            await self.browser.close_browser()
        except Exception as e:
            print('Failed to finish clean up')
        finally:
            self.context=None
            self.browser=None

