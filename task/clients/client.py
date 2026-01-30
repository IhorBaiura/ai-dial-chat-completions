from aidial_client import Dial, AsyncDial
from aidial_client.types.chat import ChatCompletionResponse, Message as AidialMessage

from typing import cast

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)

        self.dial_client = Dial(
            api_key=self._api_key, 
            base_url=DIAL_ENDPOINT
        )

        self.async_dial_client = AsyncDial(
            api_key=self._api_key, 
            base_url=DIAL_ENDPOINT
        )

    def get_completion(self, messages: list[Message]) -> Message:
        completion: ChatCompletionResponse = self.dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=cast(list[AidialMessage], [msg.to_dict() for msg in messages]),
        )

        if choices := completion.choices:
            if message := choices[0].message:
                if content := message.content:
                    print(content)
                    return Message(Role.AI, content=content)

        raise Exception("No choices in response found")

    async def stream_completion(self, messages: list[Message]) -> Message:
        completion = await self.async_dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=cast(list[AidialMessage], [msg.to_dict() for msg in messages])
        )

        contents = []

        async for chunk in completion:
            if choices := chunk.choices:
                if delta := choices[0].delta:
                    if content := delta.content:
                        print(content, end='')
                        contents.append(content)

        print()
        return Message(Role.AI, content=''.join(contents))
