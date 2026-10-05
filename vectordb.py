"""Tiny local vector store: FastEmbed embeddings + Qdrant (embedded, on-disk)."""
import os
from functools import lru_cache

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")
COLLECTION = "docs"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384-dim, small and fast on CPU
EMBED_DIM = 384


@lru_cache
def get_embedder() -> TextEmbedding:
    return TextEmbedding(model_name=EMBED_MODEL)


@lru_cache
def get_client() -> QdrantClient:
    return QdrantClient(path=QDRANT_PATH)


def index_chunks(chunks: list[dict]) -> int:
    """chunks: [{"text": ..., "source": ...}]. Recreates the collection."""
    client = get_client()
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        COLLECTION, vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE)
    )
    vectors = get_embedder().embed([c["text"] for c in chunks])
    points = [
        PointStruct(id=i, vector=v.tolist(), payload=c)
        for i, (c, v) in enumerate(zip(chunks, vectors))
    ]
    client.upsert(COLLECTION, points=points)
    return len(points)


def search(query: str, k: int = 4) -> list[dict]:
    client = get_client()
    if not client.collection_exists(COLLECTION):
        return []
    vector = next(iter(get_embedder().embed([query]))).tolist()
    hits = client.query_points(COLLECTION, query=vector, limit=k).points
    return [{**h.payload, "score": round(h.score, 3)} for h in hits]
