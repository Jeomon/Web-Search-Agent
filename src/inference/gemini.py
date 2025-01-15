from src.message import AIMessage,BaseMessage,HumanMessage,ImageMessage,SystemMessage,ToolMessage
from requests import get,RequestException,HTTPError,ConnectionError
from tenacity import retry,stop_after_attempt,retry_if_exception_type
from ratelimit import limits,sleep_and_retry
from src.inference import BaseInference,Token
from httpx import Client,AsyncClient
from pydantic import BaseModel
from typing import Literal
from json import loads
from uuid import uuid4

class ChatGemini(BaseInference):
    def __init__(self,model:str,api_version:Literal['v1','v1beta','v1alpha']='v1beta',modality:Literal['text','audio']='text',api_key:str='',base_url:str='',tools:list=[],temperature:float=0.5):
        super().__init__(model,api_key=api_key,base_url=base_url,tools=tools,temperature=temperature)
        self.api_version=api_version
        self.modality=modality

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self, messages: list[BaseMessage],json=False,model:BaseModel|None=None) -> AIMessage|ToolMessage|BaseModel:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or f"https://generativelanguage.googleapis.com/{self.api_version}/models/{self.model}:generateContent"
        params={'key':self.api_key}
        contents=[]
        system_instruct=None
        for message in messages:
            if isinstance(message,HumanMessage):
                contents.append({
                    'role':'user',
                    'parts':[{
                        'text':message.content
                    }]
                })
            elif isinstance(message,AIMessage):
                contents.append({
                    'role':'model',
                    'parts':[{
                        'text':message.content
                    }]
                })
            elif isinstance(message,ImageMessage):
                text,image=message.content
                contents.append({
                        'role':'user',
                        'parts':[{
                            'text':text
                    },
                    {
                        'inline_data':{
                            'mime_type':'image/jpeg',
                            'data': image
                        }
                    }]
                })
            elif isinstance(message,SystemMessage):
                system_instruct={
                    'parts':{
                        'text': self.structured(message,model) if model else message.content
                    }
                }
            else:
                raise Exception("Invalid Message")

        payload={
            'contents': contents,
            'generationConfig':{
                'temperature': temperature,
                'responseMimeType':'application/json' if json or model else 'text/plain',
                'responseModalities': [self.modality]
            }
        }
        if self.tools:
            payload['tools']=[
                {
                    'function_declarations':[
                        {
                            'name': tool.name,
                            'description': tool.description,
                            'parameters': tool.schema
                        }
                    for tool in self.tools]
                }
            ]
        if system_instruct:
            payload['system_instruction']=system_instruct
        try:
            with Client() as client:
                response=client.post(url=url,headers=headers,json=payload,params=params,timeout=None)
            json_obj=response.json()
            # print(json_obj)
            if json_obj.get('error'):
                raise Exception(json_obj['error']['message'])
            message=json_obj['candidates'][0]['content']['parts'][0]
            usage_metadata=json_obj['usageMetadata']
            input,output,total=usage_metadata['promptTokenCount'],usage_metadata['candidatesTokenCount'],usage_metadata['totalTokenCount']
            self.tokens=Token(input=input,output=output,total=total)
            # print(message)
            if model:
                return model.model_validate_json(message['text'])
            if json:
                content=loads(message['text'])
                return AIMessage(content)
            if message['text']:
                content=message['text']
                return AIMessage(content)
            else:
                tool_call=message['functionCall']
                return ToolMessage(id=str(uuid4()),name=tool_call['name'],args=tool_call['args'])
                
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    async def async_invoke(self, messages: list[BaseMessage],json=False,model:BaseModel=None) -> AIMessage|ToolMessage|BaseModel:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        params={'key':self.api_key}
        contents=[]
        system_instruction=None
        for message in messages:
            if isinstance(message,HumanMessage):
                contents.append({
                    'role':'user',
                    'parts':[{
                        'text':message.content
                    }]
                })
            elif isinstance(message,AIMessage):
                contents.append({
                    'role':'model',
                    'parts':[{
                        'text':message.content
                    }]
                })
            elif isinstance(message,ImageMessage):
                text,image=message.content
                contents.append({
                        'role':'user',
                        'parts':[{
                            'text':text
                    },
                    {
                        'inline_data':{
                            'mime_type':'image/jpeg',
                            'data': image
                        }
                    }]
                })
            elif isinstance(message,SystemMessage):
                system_instruction={
                    'parts':{
                        'text': self.structured(message,model) if model else message.content
                    }
                }
            else:
                raise Exception("Invalid Message")

        payload={
            'contents': contents,
            'generationConfig':{
                'temperature': temperature,
                'responseMimeType':'application/json' if json or model else 'text/plain',
                'responseModalities': [self.modality]
            }
        }
        if self.tools:
            payload['tools']=[
                {
                    'function_declarations':[
                        {
                            'name': tool.name,
                            'description': tool.description,
                            'parameters': tool.schema
                        }
                    for tool in self.tools]
                }
            ]
        if system_instruction:
            payload['system_instruction']=system_instruction
        try:
            async with AsyncClient() as client:
                response=await client.post(url=url,headers=headers,json=payload,params=params,timeout=None)
            json_obj=response.json()
            # print(json_obj)
            if json_obj.get('error'):
                raise Exception(json_obj['error']['message'])
            message=json_obj['candidates'][0]['content']['parts'][0]
            usage_metadata=json_obj['usageMetadata']
            input,output,total=usage_metadata['promptTokenCount'],usage_metadata['candidatesTokenCount'],usage_metadata['totalTokenCount']
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(message['text'])
            if json:
                content=loads(message['text'])
                return AIMessage(content)
            if message['text']:
                content=message['text']
                return AIMessage(content)
            else:
                tool_call=message['functionCall']
                return ToolMessage(id=str(uuid4()),name=tool_call['name'],args=tool_call['args'])
                
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def stream(self, query:str):
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
    
    def available_models(self):
        url='https://generativelanguage.googleapis.com/v1beta/models'
        headers=self.headers
        params={'key':self.api_key}
        try:
            response=get(url=url,headers=headers,params=params)
            response.raise_for_status()
            json_obj=response.json()
            models=json_obj['models']
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
            exit()
        except ConnectionError as err:
            print(err)
            exit()
        return [model['displayName'] for model in models]