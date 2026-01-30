import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    STREAM_BEGINNER = 'data:'
    STREAM_TERMINATOR = '[DONE]'

    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            'Content-Type': 'application/json',
            'api-key': self._api_key
        }

        request_data: dict[str, list[dict[str, str]] | bool] = {
            'messages': [msg.to_dict() for msg in messages],
            'stream': False # False by default the param might be omitted
        }

        response = requests.post(self._endpoint, headers=headers, json=request_data)

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        data = response.json()
        choices = data.get('choices', None)

        if not choices:
            raise ValueError("No Choice has been present in the response")
    
        content = choices[0]['message']['content']
        print(content)

        return Message(Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            'Content-Type': 'application/json',
            'api-key': self._api_key
        }

        request_data: dict[str, list[dict[str, str]] | bool] = {
            'messages': [msg.to_dict() for msg in messages],
            'stream': True
        }

        contents: list[str] = []

        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, json=request_data, headers=headers) as response:
                if response.status == 200:
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith(self.STREAM_BEGINNER):
                            data = line[6:].strip()
                            if data != self.STREAM_TERMINATOR:
                                content_snippet = self._get_content_snippet(data)
                                contents.append(content_snippet)
                                print(content_snippet, end='')
                            else:
                                print()
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")
                
                return Message(role=Role.AI, content=''.join(contents))
        
    def _get_content_snippet(self, data: str) -> str:
        """
        Extract content from streaming data chunk.
        """
        content = json.loads(data)

        if choices:= content.get('choices'):
            delta = choices[0].get('delta', {})
            return delta.get("content", '')
        
        return ''
             