from __future__ import annotations

from typing import Any, AsyncIterable, Iterable, Literal, Sequence, overload

from .types.chat import ChatCompletionChunk, ChatCompletionResponse


class ChatCompletions:
    @overload
    def create(
        self,
        *,
        deployment_name: str,
        messages: Sequence[Any],
        stream: Literal[False],
        **kwargs: Any,
    ) -> ChatCompletionResponse: ...

    @overload
    def create(
        self,
        *,
        deployment_name: str,
        messages: Sequence[Any],
        stream: Literal[True],
        **kwargs: Any,
    ) -> Iterable[ChatCompletionChunk]: ...


class AsyncChatCompletions:
    @overload
    async def create(
        self,
        *,
        deployment_name: str,
        messages: Sequence[Any],
        stream: Literal[False],
        **kwargs: Any,
    ) -> ChatCompletionResponse: ...

    @overload
    async def create(
        self,
        *,
        deployment_name: str,
        messages: Sequence[Any],
        stream: Literal[True],
        **kwargs: Any,
    ) -> AsyncIterable[ChatCompletionChunk]: ...


class Chat:
    completions: ChatCompletions


class AsyncChat:
    completions: AsyncChatCompletions


class Dial:
    chat: Chat

    def __init__(self, *, api_key: str, base_url: str) -> None: ...


class AsyncDial:
    chat: AsyncChat

    def __init__(self, *, api_key: str, base_url: str) -> None: ...
