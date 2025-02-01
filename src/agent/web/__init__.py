from src.agent.web.tools import click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool,extract_content_tool,download_tool,tab_tool,upload_tool,menu_tool,form_tool
from src.message import SystemMessage,HumanMessage,ImageMessage,AIMessage
from src.agent.web.utils import read_markdown_file,extract_agent_data
from src.agent.web.browser import Browser,BrowserConfig
from src.agent.web.context import Context,ContextConfig
from langgraph.graph import StateGraph,END,START
from src.memory.episodic import EpisodicMemory
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
    def __init__(self,browser:Literal['chrome','firefox','edge']='edge',additional_tools:list[Tool]=[],instructions:list=[],episodic_memory:EpisodicMemory=None,llm:BaseInference=None,max_iteration:int=10,use_vision:bool=False,headless:bool=True,verbose:bool=False,token_usage:bool=False) -> None:
        """
        WebAgent.

        Parameters:
        browser (Literal['chrome','firefox','edge']): The browser to use for the agent. Defaults to 'edge'.
        additional_tools (list[Tool]): A list of additional tools to use with the agent. Defaults to an empty list.
        instructions (list): A list of instructions to execute with the agent. Defaults to an empty list.
        memory (BaseMemory): The memory to use for the agent. Defaults to None.
        llm (BaseInference): The language model to use for the agent. Defaults to None.
        max_iteration (int): The maximum number of iterations to run the agent. Defaults to 10.
        use_vision (bool): Whether to use vision based tools. Defaults to False.
        headless (bool): Whether to run the agent in headless mode. Defaults to True.
        verbose (bool): Whether to print verbose output. Defaults to False.
        token_usage (bool): Whether to track token usage. Defaults to False.

        Returns:
        None
        """
        self.name='Web Agent'
        self.description='The web agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.'
        self.browser=Browser(BrowserConfig(browser=browser,headless=headless,user_data_dir=Path(getcwd()).joinpath(f'./user_data/{browser}/{getuser()}').as_posix()))
        self.observation_prompt=read_markdown_file('./src/agent/web/prompt/observation.md')
        self.system_prompt=read_markdown_file('./src/agent/web/prompt/system.md')
        self.action_prompt=read_markdown_file('./src/agent/web/prompt/action.md')
        self.answer_prompt=read_markdown_file('./src/agent/web/prompt/answer.md')
        self.instructions=self.format_instructions(instructions)
        self.context=Context(self.browser,ContextConfig())
        self.registry=Registry(main_tools+additional_tools)
        self.episodic_memory=episodic_memory
        self.max_iteration=max_iteration
        self.token_usage=token_usage
        self.use_vision=use_vision
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
        observation=action_result.content
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        state['messages'].pop() # Remove the last message for modification
        last_message=state['messages'][-1] # ImageMessage/HumanMessage
        if isinstance(last_message,(ImageMessage,HumanMessage)):
            state['messages'][-1]=HumanMessage(f'<Observation>{state.get('prev_observation')}</Observation>')
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
        # Get the current browser state
        browser_state=await self.context.get_state(use_vision=self.use_vision)
        image_obj=browser_state.screenshot
        # print('Tabs',browser_state.tabs_to_string())
        # Redefining the AIMessage and adding the new observation
        action_prompt=self.action_prompt.format(thought=thought,action_name=action_name,action_input=json.dumps(action_input,indent=2),route=route)
        observation_prompt=self.observation_prompt.format(observation=observation,current_url=browser_state.url,tabs=browser_state.tabs_to_string(),interactive_elements=browser_state.dom_state.elements_to_string())
        messages=[AIMessage(action_prompt),ImageMessage(text=observation_prompt,image_obj=image_obj) if self.use_vision else HumanMessage(observation_prompt)]
        return {**state,'agent_data':agent_data,'messages':messages,'prev_observation':observation}

    def final(self,state:AgentState):
        "Give the final answer"
        state['messages'].pop() # Remove the last message for modification
        last_message=state['messages'][-1] # ImageMessage/HumanMessage
        if isinstance(last_message,(ImageMessage,HumanMessage)):
            state['messages'][-1]=HumanMessage(f'<Observation>{state.get('prev_observation')}</Observation>')
        agent_data=state.get('agent_data')
        thought=agent_data.get('Thought')
        final_answer=agent_data.get('Final Answer')
        answer_prompt=self.answer_prompt.format(thought=thought,final_answer=final_answer)
        messages=[AIMessage(answer_prompt)]
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer,'messages':messages}
    
    def controller(self,state:AgentState):
        "Route to the next node"
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
        # Attach episodic memory to the system prompt 
        if self.episodic_memory and self.episodic_memory.retrieve(input):
            system_prompt=self.episodic_memory.attach_memory(system_prompt)
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
        # Extract and store the key takeaways of the task performed by the agent
        if self.episodic_memory:
            self.episodic_memory.store(response.get('messages'))
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

