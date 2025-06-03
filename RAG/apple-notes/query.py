import os
import json
import faiss
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables
base_dir = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=base_dir / ".env")

# Configuration
EXPORT_ROOT = os.path.expanduser(
    "~/Documents/_PERSO/_Python/random/RAG/apple-notes/notes"
)
INDEX_DIR = os.path.join(EXPORT_ROOT, "index_output")
INDEX_PATH = os.path.join(INDEX_DIR, "notes_index.faiss")
META_PATH = os.path.join(INDEX_DIR, "metadata.json")
TOP_K = 30  # fixed number of chunks to retrieve

# Load FAISS index and metadata
index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Initialize embeddings and LLM
embedder = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-4o", temperature=0)


def retrieve(query: str, top_k: int = TOP_K):
    """
    Retrieve top_k chunks relevant to query.
    Returns list of (chunk_text, source_path).
    """
    q_vec = np.array(embedder.embed_query(query), dtype="float32").reshape(1, -1)
    _, indices = index.search(q_vec, top_k)
    return [(metadata[i]["text"], metadata[i]["source"]) for i in indices[0]]


def answer_question(question: str) -> str:
    # Retrieve relevant chunks
    results = retrieve(question)
    if not results:
        return "No relevant notes found."

    # Build prompt with context
    context = "\n---\n".join([
        f"Source: {src}\n{txt}" for txt, src in results
    ])
    system_msg = SystemMessage(
        content="You are a helpful assistant answering questions based on the user's Apple Notes exports."
    )
    human_msg = HumanMessage(
        content=(
            f"Use the following notes context to answer the question:\n{context}\nQuestion: {question}"
        )
    )
    response = llm([system_msg, human_msg])
    return response.content


if __name__ == "__main__":
    print("⚡︎ Apple Notes RAG Interactive Chat")
    print(f"Loaded {len(metadata)} chunks.\nType 'exit' to quit.\n")
    while True:
        question = input("☞ Enter your question: ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        print("Retrieving answer...\n")
        answer = answer_question(question)
        print("=== Answer ===")
        print(answer)
        print()