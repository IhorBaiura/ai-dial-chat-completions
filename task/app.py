import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    client = DialClient(deployment_name="gpt-5-2025-08-07")
    # client = CustomDialClient(deployment_name="gpt-5-2025-08-07")

    conversation = Conversation()

    print("Type system prompt (or press Enter to use default): ")
    system_prompt = input('> ').strip()

    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT
        print(f"Using default system prompt: {system_prompt}")

    conversation.add_message(Message(Role.SYSTEM, content=system_prompt))
    print("System prompt set. You can start chatting with the assistant. Type 'exit' to quit.")

    while True:
        print("User:")
        user_input = input('> ').strip()

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        conversation.add_message(Message(Role.USER, content=user_input))

        print("Assistant:")
        if stream:
            response_message = await client.stream_completion(conversation.messages)
        else:
            response_message = client.get_completion(conversation.messages)

        conversation.add_message(response_message)


asyncio.run(
    start(True)
)
