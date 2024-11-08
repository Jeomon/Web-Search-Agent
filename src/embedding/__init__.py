from abc import ABC,abstractmethod

class BaseEmbedding(ABC):
    def __init__(self,model:str='',api_key:str='',base_url:str=''):
        self.name=self.__class__.__name__.replace('Embedding','')
        self.api_key=api_key
        self.model=model
        self.base_url=base_url
        self.headers={'Content-Type': 'application/json'}
        
    @abstractmethod
    def embed(self,text:str):
        pass