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
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            'Content-Type': 'application/json',
            'api-key': self._api_key
        }

        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data: dict[str, list[dict[str, str]] | bool] = {
            'messages': [msg.to_dict() for msg in messages],
            'stream': False # False by default the param might be omitted
        }

        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        response = requests.post(self._endpoint, headers=headers, json=request_data)

        # 4. Get content from response, print it and return message with assistant role and content
        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"
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
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            'Content-Type': 'application/json',
            'api-key': self._api_key
        }

        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data: dict[str, list[dict[str, str]] | bool] = {
            'messages': [msg.to_dict() for msg in messages],
            'stream': True
        }

        # 3. Create empty list called 'contents' to store content snippets
        contents: list[str] = []

        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
        # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
        #    chunks, collect them and return as assistant message
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
        # 1. Parse JSON data using json.loads(data)
        content = json.loads(data)

        # 2. Get "choices" from parsed JSON data
        choices = content.get('choices', None)

        # 3. If choices exist and not empty:
        #    - Get delta from choices[0]["delta"]
        #    - Return content from delta.get("content", '') - use empty string as default
        # 4. If no choices, return empty string
        if not choices:
            return ''
        
        delta = choices[0]['delta']
        
        return delta.get("content", '')
                