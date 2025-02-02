from src.memory.episodic.utils import read_markdown_file
from src.memory.episodic.views import Memory,Memories
from src.message import SystemMessage,HumanMessage
from src.inference import BaseInference
from src.message import BaseMessage
from src.memory import BaseMemory
from src.router import LLMRouter
from termcolor import colored
from uuid import uuid4
import json

with open('./src/memory/episodic/routes.json','r') as f:
    routes=json.load(f)

class EpisodicMemory(BaseMemory):
    def __init__(self,knowledge_base:str='knowledge_base.json',llm:BaseInference=None,verbose=False):
        self.memories:Memories=[]
        super().__init__(knowledge_base=knowledge_base,llm=llm,verbose=verbose)

    def router(self,conversation:list[BaseMessage]):
        instructions=[
            'Go through the conversation and revelant memories to determine which route to take.',
            'Be proactive in your choice and perform this task carefully and with utmost accuracy.'
        ]
        router=LLMRouter(instructions=instructions,routes=routes,llm=self.llm,verbose=False)
        route=router.invoke(f'### Revelant Memories from Knowledge Base:\n{self.memories.to_string()}\n### Conversation:\n{self.conversation_to_text(conversation)}')
        return route
    
    def store(self, conversation: list[BaseMessage]):
        route=self.router(conversation)
        if route=='ADD':
            self.add_memory(conversation)
        elif route=='UPDATE':
            self.update_memory(conversation)
        elif route=='REPLACE':
            self.replace_memory(conversation)
        else:
            self.idle_memory(conversation)

    def idle_memory(self,conversation:list[BaseMessage]):
        if self.verbose:
            print(f'{colored(f'Idle memory:',color='yellow',attrs=['bold'])}\n{json.dumps(self.memories.all(),indent=2)}')
        return None

    def add_memory(self,conversation:list[BaseMessage]):
        system_prompt=read_markdown_file('src/memory/episodic/prompt/add.md')
        text_conversation=self.conversation_to_text(conversation)
        user_prompt=f'### Conversation:\n{text_conversation}'
        messages=[SystemMessage(system_prompt),HumanMessage(user_prompt)]
        memory=self.llm.invoke(messages,model=Memory)
        if self.verbose:
            print(f'{colored(f'Adding memory to Knowledge Base:',color='yellow',attrs=['bold'])}\n{json.dumps(memory.to_dict(),indent=2)}')
        with open(f'./memory_data/{self.knowledge_base}','r+') as f:
            knowledge_base:list[dict] = json.load(f)
            knowledge_base.append(memory.model_dump())
            f.seek(0)
            json.dump(knowledge_base, f, indent=2)

    def update_memory(self,conversation:list[BaseMessage]):
        system_prompt=read_markdown_file('src/memory/episodic/prompt/update.md')
        text_conversation=self.conversation_to_text(conversation)
        user_prompt=f'### Revelant memories from Knowledge Base:\n{self.memories.to_string()}\n### Conversation:\n{text_conversation}'
        messages=[SystemMessage(system_prompt),HumanMessage(user_prompt)]
        memory:Memory=self.llm.invoke(messages,model=Memory)
        if self.verbose:
            print(f'{colored(f'Updated memory from Knowledge Base:',color='yellow',attrs=['bold'])}\n{json.dumps(memory.to_dict(),indent=2)}')
        with open(f'./memory_data/{self.knowledge_base}','r+') as f:
            knowledge_base = [Memory.model_validate(memory) for memory in json.loads(f)]
            memory_ids=[memory.get('id') for memory in self.memories.all()]
            updated_knowledge_base=list(filter(lambda memory:memory.id not in memory_ids,knowledge_base))
            updated_knowledge_base.extend(memory)
            f.seek(0)
            json.dump(updated_knowledge_base, f, indent=2)
            f.truncate()

    def replace_memory(self,conversation:list[BaseMessage]):
        system_prompt=read_markdown_file('src/memory/episodic/prompt/replace.md')
        text_conversation=self.conversation_to_text(conversation)
        user_prompt=f'### Conversation:\n{text_conversation}'
        messages=[SystemMessage(system_prompt),HumanMessage(user_prompt)]
        memory:Memory=self.llm.invoke(messages,model=Memory)
        if self.verbose:
            print(f'{colored(f'Replacing memory from Knowledge Base:',color='yellow',attrs=['bold'])}\n{json.dumps(memory.to_dict(),indent=2)}')
        with open(f'./memory_data/{self.knowledge_base}','r+') as f:
            knowledge_base = [Memory.model_validate(memory) for memory in json.loads(f)]
            memory_ids=[memory.id for memory in self.memories.all()]
            updated_knowledge_base=list(filter(lambda memory:memory.id not in memory_ids,knowledge_base))
            updated_knowledge_base.append(memory)
            f.seek(0)
            json.dump([memory.model_dump() for memory in updated_knowledge_base], f, indent=2)
            f.truncate()

    def retrieve(self, query: str)->list[dict]:
        memories=[memory for memory in self.memories]
        system_prompt=read_markdown_file('src/memory/episodic/prompt/retrieve.md')
        user_prompt=f'### Query: {query}\n Now, select the memories those are relevant to solve the query.'
        messages=[SystemMessage(system_prompt.format(memories=memories)),HumanMessage(user_prompt)]
        memories=self.llm.invoke(messages,model=Memories)
        self.memories=memories
        if self.verbose:
            print(f'{colored(f'Retrieved memories from Knowledge Base:',color='yellow',attrs=['bold'])}\n{json.dumps(self.memories.all(),indent=2)}')
        return self.memories

    def attach_memory(self,system_prompt:str)->str:
        episodic_prompt=read_markdown_file('src/memory/episodic/prompt/memory.md')
        memory_prompt=episodic_prompt.format(memories=self.memories.to_string())
        return f'{system_prompt}\n\n{memory_prompt}'

