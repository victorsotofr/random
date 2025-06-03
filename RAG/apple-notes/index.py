import os
import glob
import json
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
import faiss
import numpy as np

# WARNING: Run this script only after having exported your Apple Notes to HTML files, running the Apple Notes Exporter script (Script Editor).

# Configuration
base_dir = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=base_dir / ".env")

EXPORT_ROOT = os.path.expanduser("~/Documents/_PERSO/_Python/random/RAG/apple-notes/notes")
OUTPUT_DIR = os.path.join(EXPORT_ROOT, "index_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Gather documents
html_paths = glob.glob(os.path.join(EXPORT_ROOT, "**", "*.html"), recursive=True)
docs = []
for path in html_paths:
    with open(path, "r", encoding="utf-8") as file:
        text = BeautifulSoup(file, "html.parser").get_text(separator=" ", strip=True)
        docs.append({"text": text, "path": path})

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=100)
chunks = []
for doc in docs:
    for i, piece in enumerate(splitter.split_text(doc["text"])):
        chunks.append({
            "text": piece,
            "source": doc["path"],
            "chunk_id": i
        })

# Embed chunks
embedder = OpenAIEmbeddings()
vectors = np.array([embedder.embed_query(c["text"]) for c in chunks], dtype="float32")

# Build FAISS index
dim = vectors.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(vectors)

# Save index and metadata
faiss.write_index(index, os.path.join(OUTPUT_DIR, "notes_index.faiss"))
with open(os.path.join(OUTPUT_DIR, "metadata.json"), "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"Indexed {len(chunks)} chunks from {len(docs)} documents.")