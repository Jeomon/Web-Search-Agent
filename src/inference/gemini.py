from requests import post,get,RequestException,HTTPError,ConnectionError
from tenacity import retry,stop_after_attempt,retry_if_exception_type
from src.message import AIMessage,BaseMessage,HumanMessage,ImageMessage
from src.inference import BaseInference
from httpx import Client,AsyncClient
from json import loads

class ChatGemini(BaseInference):
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self, messages: list[BaseMessage],json=False) -> AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
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
            else:
                system_instruction={
                    'parts':{
                        'text': message.content
                    }
                }

        payload={
            'contents': contents,
            'generationConfig':{
                'temperature': temperature,
                'responseMimeType':'application/json' if json else 'text/plain'
            }
        }
        if system_instruction:
            payload['system_instruction']=system_instruction
        try:
            with Client() as client:
                response=client.post(url=url,headers=headers,json=payload,params=params,timeout=None)
            json_obj=response.json()
            # print(json_obj)
            if json_obj.get('error'):
                raise Exception(json_obj['error']['message'])
            if json:
                content=loads(json_obj['candidates'][0]['content']['parts'][0]['text'])
            else:
                content=json_obj['candidates'][0]['content']['parts'][0]['text']
            return AIMessage(content)
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    async def async_invoke(self, messages: list[BaseMessage],json=False) -> AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
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
            else:
                system_instruction={
                    'parts':{
                        'text': message.content
                    }
                }

        payload={
            'contents': contents,
            'generationConfig':{
                'temperature': temperature,
                'responseMimeType':'application/json' if json else 'text/plain'
            }
        }
        if system_instruction:
            payload['system_instruction']=system_instruction
        try:
            async with AsyncClient() as client:
                response=await client.post(url=url,headers=headers,json=payload,params=params,timeout=None)
            json_obj=response.json()
            # print(json_obj)
            if json_obj.get('error'):
                raise Exception(json_obj['error']['message'])
            if json:
                content=loads(json_obj['candidates'][0]['content']['parts'][0]['text'])
            else:
                content=json_obj['candidates'][0]['content']['parts'][0]['text']
            return AIMessage(content)
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def stream(self, query:str):
        '''Work in progress'''
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
    
    def available_models(self):
        url='https://generativelanguage.googleapis.com/v1beta/models'
        headers=self.headers
        params={'key':self.api_key}
        try:
            with Client() as client:
                response=client.get(url=url,headers=headers,params=params)
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