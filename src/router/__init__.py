from src.message import HumanMessage,SystemMessage
from src.router.utils import read_markdown_file
from src.inference import BaseInference
from json import dumps

class LLMRouter:
    def __init__(self,instructions:list[str]=[],routes:list[dict]=[],llm:BaseInference=None,verbose=False):
        self.system_prompt=read_markdown_file('./src/router/prompt.md')
        self.instructions=self.__get_instructions(instructions)
        self.routes=dumps(routes,indent=2)
        self.llm=llm
        self.verbose=verbose

    def __get_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for i,instruction in enumerate(instructions)])
    
    def invoke(self,query:str)->str:
        parameters={'instructions':self.instructions,'routes':self.routes}
        messages=[SystemMessage(self.system_prompt.format(**parameters)),HumanMessage(query)]
        response=self.llm.invoke(messages,json=True)
        route=response.content.get('route')
        if self.verbose:
            print(f"Going to {route.upper()} route")
        return route
