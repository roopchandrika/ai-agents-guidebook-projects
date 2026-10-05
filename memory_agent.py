"""AutoGen assistant with long-term, human-like memory backed by Zep Cloud."""
import os
import re
import uuid
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_core.memory import (
    Memory,
    MemoryContent,
    MemoryMimeType,
    MemoryQueryResult,
    UpdateContextResult,
)
from autogen_core.model_context import ChatCompletionContext
from autogen_core.models import SystemMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from zep_cloud.client import Zep
from zep_cloud.types import Message


# 1) LLM: local Qwen 3 via Ollama's OpenAI-compatible API (or any OpenAI-compatible endpoint)
def build_model_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=os.getenv("LLM_MODEL", "qwen3:8b"),
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.getenv("LLM_API_KEY", "ollama"),
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": False,
            "structured_output": False,
            "family": "unknown",
        },
    )


# 2) Zep client
def build_zep() -> Zep:
    return Zep(api_key=os.environ["ZEP_API_KEY"])


# 3) User + thread (session). A user can have many threads; facts are shared across all of them.
def ensure_user(zep: Zep, user_id: str, first_name: str) -> None:
    try:
        zep.user.get(user_id)
    except Exception:
        zep.user.add(user_id=user_id, first_name=first_name)


def new_thread(zep: Zep, user_id: str) -> str:
    thread_id = f"thread-{uuid.uuid4().hex[:12]}"
    zep.thread.create(thread_id=thread_id, user_id=user_id)
    return thread_id


# 4) Zep-backed memory for AutoGen: injects Zep's context (facts + summaries) before every LLM call
class ZepMemory(Memory):
    def __init__(self, zep: Zep, thread_id: str, user_name: str):
        self.zep = zep
        self.thread_id = thread_id
        self.user_name = user_name

    def save_turn(self, role: str, content: str) -> None:
        name = self.user_name if role == "user" else "Assistant"
        self.zep.thread.add_messages(
            self.thread_id, messages=[Message(name=name, role=role, content=content)]
        )

    def get_context(self) -> str:
        return self.zep.thread.get_user_context(thread_id=self.thread_id).context or ""

    async def update_context(self, model_context: ChatCompletionContext) -> UpdateContextResult:
        context = self.get_context()
        if context:
            await model_context.add_message(
                SystemMessage(content=f"Long-term memory about the user (from Zep):\n{context}")
            )
        return UpdateContextResult(
            memories=MemoryQueryResult(
                results=[MemoryContent(content=context, mime_type=MemoryMimeType.TEXT)] if context else []
            )
        )

    async def query(self, query: Any, cancellation_token: CancellationToken | None = None, **kwargs) -> MemoryQueryResult:
        return MemoryQueryResult(results=[MemoryContent(content=self.get_context(), mime_type=MemoryMimeType.TEXT)])

    async def add(self, content: MemoryContent, cancellation_token: CancellationToken | None = None) -> None:
        self.save_turn("user", str(content.content))

    async def clear(self) -> None:
        pass

    async def close(self) -> None:
        pass


SYSTEM_PROMPT = (
    "You are a friendly personal assistant with long-term memory. Use what you remember "
    "about the user to personalise answers, refer back to earlier facts naturally, and never "
    "invent facts about the user. Be concise."
)


# 5) Agent + 6) one chat turn
async def chat_turn(
    memory: ZepMemory, user_message: str, agent_state: dict | None
) -> tuple[str, dict]:
    """Run one user turn. Returns (reply, new_agent_state) so the chat history survives reruns."""
    memory.save_turn("user", user_message)  # Zep extracts facts from the conversation

    agent = AssistantAgent(
        name="memory_agent",
        model_client=build_model_client(),
        system_message=SYSTEM_PROMPT,
        memory=[memory],
    )
    if agent_state:
        await agent.load_state(agent_state)

    result = await agent.run(task=user_message)
    reply = re.sub(r"<think>.*?</think>", "", str(result.messages[-1].content), flags=re.S).strip()

    memory.save_turn("assistant", reply)
    return reply, await agent.save_state()
