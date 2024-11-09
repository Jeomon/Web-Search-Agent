from chromadb import PersistentClient
from src.embedding import BaseEmbedding
from uuid import uuid4

class Memory:
    def __init__(self,path:str,embedding_function:BaseEmbedding):
        self.collection=self.get_or_create_memory(path,embedding_function)

    def get_or_create_memory(self,path:str,embedding_function):
        client=PersistentClient(path=path)
        collection=client.get_or_create_collection('memory',embedding_function=embedding_function)
        return collection

    def add_memory(self,memory:str):
        self.collection.add(documents=[memory],ids=[str(uuid4())])

    def get_memory(self,query:str,k:int=10):
        results=self.collection.query(query_texts=[query],n_results=k)
        return results['documents']
    