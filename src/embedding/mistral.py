from src.embedding import BaseEmbedding
from httpx import Client
from typing import Literal
from requests import RequestException,HTTPError,ConnectionError
import json

class MistralEmbedding(BaseEmbedding):
    def embed(self, text):
        url=self.base_url or 'https://api.mistral.ai/v1/embeddings'
        self.headers['Authorization'] = f'Bearer {self.api_key}'
        headers=self.headers
        payload={
            'model':self.model,
            'input':text,
            'encoding_format':'float'
        }
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            return response.json()['data']['embedding']
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)

