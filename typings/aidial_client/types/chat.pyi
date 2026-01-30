from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Message:
    role: str
    content: Optional[str]


@dataclass
class ChatCompletionChoice:
    message: Optional[Message]


@dataclass
class ChatCompletionResponse:
    choices: List[ChatCompletionChoice]


@dataclass
class Delta:
    content: Optional[str]


@dataclass
class ChatCompletionChunkChoice:
    delta: Optional[Delta]


@dataclass
class ChatCompletionChunk:
    choices: List[ChatCompletionChunkChoice]
