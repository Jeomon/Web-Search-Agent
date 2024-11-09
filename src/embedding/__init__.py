from chromadb import Documents,EmbeddingFunction,Embeddings
from abc import ABC,abstractmethod

class BaseEmbedding(ABC,EmbeddingFunction):
    def __init__(self,model:str='',api_key:str='',base_url:str=''):
        self.name=self.__class__.__name__.replace('Embedding','')
        self.api_key=api_key
        self.model=model
        self.base_url=base_url
        self.headers={'Content-Type': 'application/json'}

    def __call__(self, input:Documents)->Embeddings:
        return self.embed(input)
        
    @abstractmethod
    def embed(self,text:list[str]|str)->list:
        pass