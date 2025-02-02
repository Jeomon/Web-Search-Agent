from abc import ABC,abstractmethod
from src.inference import BaseInference
from src.message import BaseMessage,SystemMessage
import json
import os

class BaseMemory(ABC):
    def __init__(self,knowledge_base:str='knowledge_base.json',llm:BaseInference=None,verbose=False):
        self.llm=llm
        self.verbose=verbose
        self.knowledge_base=knowledge_base
        self.__initialize_memory()

    @abstractmethod
    def store(self,conversation:list[BaseMessage])->None:
        pass

    @abstractmethod
    def retrieve(self,query:str)->list[dict]:
        pass

    @abstractmethod
    def attach_memory(self)->str:
        pass
    
    def __initialize_memory(self):
        if not os.path.exists(f'./memory_data/{self.knowledge_base}'):
            os.makedirs('./memory_data',exist_ok=True)
            with open(f'./memory_data/{self.knowledge_base}','w') as f:
                f.write(json.dumps(self.memories,indent=2))
        else:
            with open(f'./memory_data/{self.knowledge_base}','r') as f:
                self.memories=json.loads(f.read())
    def conversation_to_text(self,conversation:list[BaseMessage]):
        conversation=list(self.__filter_conversation(conversation))
        return '\n'.join([f'{message.role}: {message.content}' for message in conversation])
    def __filter_conversation(self,conversation:list[BaseMessage]):
        return filter(lambda message: not isinstance(message,SystemMessage),conversation)