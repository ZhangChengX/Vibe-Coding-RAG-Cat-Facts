"""Milestone 4 — Embedding and retrieval.

Embeds chunks with the all-MiniLM-L6-v2 sentence-transformers model and stores
them — alongside their raw text and source file — in a persistent ChromaDB
collection on disk (./chroma_db). retrieve() runs a similarity search and
returns the top results ranked by similarity score.
"""

from pathlib import Path
from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "cat_facts"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Helper variables holding the ChromaDB client and collection used by the
# functions below. The collection uses cosine distance so similarity scores
# fall in a familiar 0..1 range.
_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)

# The embedding model is loaded lazily so importing this module stays cheap.
_model = None


def _get_model() -> SentenceTransformer:
    """Load (once) and return the sentence-transformers embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embedding(file_name: str, chunks: List[str]) -> None:
    """Embed a document's chunks and store them in the vector database.

    Each chunk is stored with its raw text, its embedding vector, and its
    source (the file name) so retrieved results can be attributed back to the
    document they came from.

    Args:
        file_name: The source document the chunks came from.
        chunks: The list of raw text chunks to embed and store.
    """
    if not chunks:
        return

    embeddings = _get_model().encode(chunks).tolist()
    ids = [f"{file_name}::{i}" for i in range(len(chunks))]
    metadatas = [{"source": file_name} for _ in chunks]

    _collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def retrieve(query: str, n_results: int) -> List[Dict]:
    """Search the vector database for the chunks most relevant to a query.

    Args:
        query: The user's question.
        n_results: How many top results to return.

    Returns:
        A list of results ranked by similarity score (highest first). Each item
        is a dict with keys: "text", "score", and "source".
    """
    query_embedding = _get_model().encode([query]).tolist()
    response = _collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
    )

    documents = response["documents"][0]
    distances = response["distances"][0]
    metadatas = response["metadatas"][0]

    results = []
    for text, distance, metadata in zip(documents, distances, metadatas):
        # Convert cosine distance to a similarity score in [0, 1].
        results.append(
            {
                "text": text,
                "score": 1 - distance,
                "source": metadata.get("source"),
            }
        )

    # ChromaDB already returns results ordered by ascending distance, i.e.
    # descending similarity, but sort defensively to guarantee the contract.
    results.sort(key=lambda item: item["score"], reverse=True)
    return results


if __name__ == "__main__":
    # Ingest every document in documents/ and run the evaluation questions.
    if _collection.count() > 0:
        # The ChromaDB store already exists, so embeddings were generated on a
        # previous run — skip re-embedding.
        print(
            f"ChromaDB already exists with {_collection.count()} chunks — "
            "skipping embedding generation."
        )
        print(
            f"To regenerate the embeddings, remove the ChromaDB file first: "
            f"rm -rf {CHROMA_DIR}"
        )
    else:
        from chunking import DOCUMENTS_DIR, load_document, chunk_document
        for path in sorted(DOCUMENTS_DIR.glob("*.txt")):
            chunks = chunk_document(load_document(path.name))
            embedding(path.name, chunks)
            print(f"Embedded {len(chunks)} chunks from {path.name}")
        print(f"\nCollection now holds {_collection.count()} chunks.")

    print()

    eval_questions = [
        "Can cats taste sweets?",
        "How long does a cat pregnant?",
        "How many muscles does cats have to control the outer ear?",
        "What is the smallest pedigreed cat?",
        "What is the biggest wildcat?",
    ]
    for question in eval_questions:
        print(f"Q: {question}")
        for result in retrieve(question, 3):
            text = result["text"][:90] + ("..." if len(result["text"]) > 90 else "")
            print(f"  [{result['score']:.3f}] ({result['source']}) {text}")
        print()
