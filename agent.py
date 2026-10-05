"""Real-time Voice RAG agent.

Pipeline: mic audio -> Silero VAD -> AssemblyAI STT -> LLM (+ LlamaIndex RAG tool) -> Cartesia TTS

Run:
  python agent.py download-files   # one-time: fetch VAD model files
  python agent.py console          # talk to it in your terminal (no LiveKit server needed)
  python agent.py dev              # connect to LiveKit Cloud, then use the Agents Playground
"""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import assemblyai, cartesia, openai, silero
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

# 1) Environment and logging
load_dotenv()
logger = logging.getLogger("voice-rag-agent")
logger.setLevel(logging.INFO)

# 2) RAG: index ./data once and persist it to ./storage
DATA_DIR = Path(__file__).parent / "data"
PERSIST_DIR = Path(__file__).parent / "storage"

if PERSIST_DIR.exists():
    index = load_index_from_storage(StorageContext.from_defaults(persist_dir=str(PERSIST_DIR)))
else:
    documents = SimpleDirectoryReader(str(DATA_DIR)).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=str(PERSIST_DIR))
    logger.info("Indexed %d documents", len(documents))

query_engine = index.as_query_engine(use_async=True)


def build_llm():
    """OpenAI by default; set LLM_PROVIDER=ollama to use a local model."""
    if os.getenv("LLM_PROVIDER", "openai") == "ollama":
        return openai.LLM.with_ollama(
            model=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        )
    return openai.LLM(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))


class VoiceRAGAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful voice assistant. Answer questions using the "
                "query_knowledge_base tool whenever the question could be covered by the "
                "user's documents. Keep answers short and conversational, and avoid "
                "markdown, lists or symbols because your replies are spoken aloud."
            )
        )

    @function_tool
    async def query_knowledge_base(self, context: RunContext, question: str) -> str:
        """Look up information in the user's document knowledge base.

        Args:
            question: The question to answer from the documents.
        """
        logger.info("RAG query: %s", question)
        response = await query_engine.aquery(question)
        return str(response)


# 3) Voice Activity Detection: prewarm Silero once per worker process
def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load()


# 4) Entry point: wire STT -> LLM -> TTS into a voice session
async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=assemblyai.STT(),
        llm=build_llm(),
        tts=cartesia.TTS(),
    )
    await session.start(agent=VoiceRAGAssistant(), room=ctx.room)
    await session.generate_reply(
        instructions="Greet the user and tell them they can ask about their documents."
    )


# 5) Run the app
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
