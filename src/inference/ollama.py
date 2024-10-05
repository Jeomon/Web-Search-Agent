from src.message import AIMessage,BaseMessage,SystemMessage,HumanMessage,ImageMessage
from tenacity import retry,stop_after_attempt,retry_if_exception_type
from requests import RequestException,HTTPError
from typing import AsyncGenerator,Generator
from httpx import Client,AsyncClient,get
from src.inference import BaseInference
from json import loads
from io import BytesIO
import requests
import base64
import re

class ChatOllama(BaseInference):
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self,messages: list[BaseMessage],json=False)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        contents=[]
        images=[]
        for message in messages:
            if isinstance(message,[SystemMessage,HumanMessage,AIMessage]):
                contents.append(message)
            elif isinstance(message,ImageMessage):
                text,image=message.content
                contents.append(HumanMessage(text))
                images.append(image)
        payload={
            "model": self.model,
            "messages": contents,
            "images":images,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":False
        }
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,timeout=None)
            response.raise_for_status()
            json_obj=response.json()
            if json:
                content=loads(json_obj['message']['content'])
            else:
                content=json_obj['message']['content']
            return AIMessage(content)
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
    
    def stream(self,messages: list[BaseMessage],json=False)->Generator[str,None,None]:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        contents=[]
        images=[]
        for message in messages:
            if isinstance(message,[SystemMessage,HumanMessage,AIMessage]):
                contents.append(message)
            elif isinstance(message,ImageMessage):
                text,image=message.content
                contents.append(HumanMessage(text))
                images.append(image)
        payload={
            "model": self.model,
            "messages": contents,
            "images":images,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":True
        }
        try:
            response=requests.post(url=url,json=payload,headers=headers,stream=True)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            return (loads(chunk)['message']['content'] for chunk in chunks)
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    async def async_stream(self,messages: list[BaseMessage],json=False)->AsyncGenerator:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        contents=[]
        images=[]
        for message in messages:
            if isinstance(message,[SystemMessage,HumanMessage,AIMessage]):
                contents.append(message)
            elif isinstance(message,ImageMessage):
                text,image=message.content
                contents.append(HumanMessage(text))
                images.append(image)
        payload={
            "model": self.model,
            "messages": contents,
            "images":images,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":True
        }
        try:
            async with AsyncClient() as client:
                async with client.stream(method='POST',url=url,json=payload,headers=headers,timeout=None) as response:
                    async for chunk in response.aiter_lines():
                        yield loads(chunk)['response']
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    def available_models(self):
        url='http://localhost:11434/api/tags'
        headers=self.headers
        try:
            with Client() as client:
                response=client.get(url=url,headers=headers)
            models=response.json()
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
            exit()
        except ConnectionError as err:
            print(err)
            exit()
        return [model['name'] for model in models['models']]

        
class Ollama(BaseInference):
    def invoke(self, query:str,images_path:list[str]=[],json=False)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":False
        }
        if images_path:
            payload['images'] = [self.__image_to_base64(image_path) for image_path in images_path]
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,timeout=None)
            json_obj=response.json()
            return AIMessage(json_obj['response'])
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')

    def __is_url(self,image_path:str)->bool:
        url_pattern = re.compile(r'^https?://')
        return url_pattern.match(image_path) is not None

    def __is_file_path(self,image_path:str)->bool:
        file_path_pattern = re.compile(r'^([./~]|([a-zA-Z]:)|\\|//)?\.?\/?[a-zA-Z0-9._-]+(\.[a-zA-Z0-9]+)?$')
        return file_path_pattern.match(image_path) is not None

    def __image_to_base64(self,image_source: str) -> str:
        if self.__is_url(image_source):
            response = get(image_source)
            bytes = BytesIO(response.content)
            image_bytes = bytes.read()
        elif self.__is_file_path(image_source):
            with open(image_source, 'rb') as image:
                image_bytes = image.read()
        else:
            raise ValueError("Invalid image source. Must be a URL or file path.")
        return base64.b64encode(image_bytes).decode('utf-8')

    def stream(self,query:str,images_path:list[str]=[],json=False)->Generator[str,None,None]:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "images":[self.__image_to_base64(image_path) for image_path in images_path],
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":True
        }
        try:
            response=requests.post(url=url,json=payload,headers=headers,stream=True)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            return (loads(chunk)['response'] for chunk in chunks)
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    async def async_stream(self,query:str,images_path:list[str]=[],json=False)->AsyncGenerator:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":True
        }
        if images_path:
            payload['images'] = [self.__image_to_base64(image_path) for image_path in images_path]
        try:
            async with AsyncClient() as client:
                async with client.stream(method='POST',url=url,json=payload,headers=headers,timeout=None) as response:
                    async for chunk in response.aiter_lines():
                        yield loads(chunk)['response']
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    def available_models(self):
        url='http://localhost:11434/api/tags'
        headers=self.headers
        try:
            with Client() as client:
                response=client.get(url=url,headers=headers)
            models=response.json()
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
            exit()
        except ConnectionError as err:
            print(err)
            exit()
        return [model['name'] for model in models['models']]
