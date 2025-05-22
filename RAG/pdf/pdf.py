# ==========================================
# RAG SYSTEM FOR PDFs
# Extracts information from PDFs and allows users to ask questions.
# ==========================================
# SOURCES:
# MAIN GUIDE: https://python.langchain.com/docs/tutorials/rag/
# ==========================================
import os
import getpass
import faiss
import numpy as np
import PyPDF2
from sentence_transformers import SentenceTransformer
import openai
import tiktoken  # Tokenizer to estimate token count
import gc # Garbage collector for memory management
import signal # Handles crashes gracefully

# ==========================================
# SETTING UP OPENAI API KEY
# ==========================================
if not os.environ.get("OPENAI_API_KEY"):
    openai.api_key = getpass.getpass("Enter your API key here: ")
else:
    openai.api_key = os.environ["OPENAI_API_KEY"]

# ==========================================
# FAISS THREAD MANAGEMENT (PREVENT FAULTS)
# ==========================================
faiss.omp_set_num_threads(1) # ensures faiss doesn't overuse CPU

# ==========================================
# MODELS INITIALIZATION
# ==========================================
# Load the embedding model:
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Path to the directory storing the PDFs:
PDF_DIR = "./pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# ==========================================
# TEXT EXTRACTION FROM PDF
# ==========================================
def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    return text.strip()

# ==========================================
# TEXT INDEXING - FAISS
# ==========================================
def build_faiss_index(text_chunks):
    """Embeds text chunks and stores them in a FAISS index."""
    embeddings = embedding_model.encode(text_chunks, convert_to_numpy=True, show_progress_bar=True, batch_size=32)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    print(f"\nIndexed {len(text_chunks)} text chunks in FAISS.\n")  # Debugging
    return index, text_chunks

# ==========================================
# RETRIEVAL FUNCTION
# ==========================================
def retrieve_relevant_chunks(query, index, text_chunks, top_k=3):
    """Finds the most relevant text chunks based on the user's query."""
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    
    if not index.is_trained or index.ntotal == 0:
        print("\n FAISS index is empty! Skipping retrieval.")
        return []
    
    distances, indices = index.search(query_embedding, min(top_k, index.ntotal))

    retrieved_texts = [text_chunks[i] for i in indices[0] if i < len(text_chunks)]

    print(f"\nRetrieved {len(retrieved_texts)} chunks for query: '{query}'")
    return retrieved_texts

# ==========================================
# TRIM CONTEXT WITHIN TOKEN LIMIT
# ==========================================
def trim_context(relevant_chunks, max_tokens=4000):
    """Ensures the retrieved text remains within the model's token limit."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    token_count, trimmed_chunks = 0, []

    for chunk in relevant_chunks:
        chunk_tokens = encoding.encode(chunk)
        if token_count + len(chunk_tokens) > max_tokens:
            break
        trimmed_chunks.append(chunk)
        token_count += len(chunk_tokens)

    print(f"\nUsing {token_count} tokens (limit: {max_tokens}).\n")  # Debugging
    return "\n".join(trimmed_chunks)

# ==========================================
# RESPONSE GENERATION FUNCTION
# ==========================================
def generate_answer(query, relevant_chunks):
    """Generates an AI response using GPT-4 based on retrieved document excerpts."""
    context = trim_context(relevant_chunks)
    
    if not context:
        return "I don't know based on the provided documents."

    prompt = f"""
    You are an AI assistant that answers questions strictly based on the provided document excerpts.
    If the context does not contain the answer, simply respond: "I don't know based on the provided documents."

    Context:
    {context}

    Question: {query}
    Answer:
    """

    client = openai.Client()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content  # Extract answer

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    """Loads PDFs, builds FAISS index, and starts an interactive Q&A loop."""
    
    pdf_files = [os.path.join(PDF_DIR, f) for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("No PDF files found in the 'pdfs' directory. Please add PDFs and try again.")
        return
    
    all_text = "\n".join([extract_text_from_pdf(pdf) for pdf in pdf_files])
    text_chunks = all_text.split("\n\n")  # Simple chunking by paragraphs

    # Build FAISS index
    index, chunks = build_faiss_index(text_chunks)

    print("\nReady for questions! Type 'exit' to quit.")

    while True:
        query = input("\n❓ Your question: ").strip()

        if query.lower() == "exit":
            print("\nExiting. Thanks for using the PDF Q&A system!")
            break

        relevant_chunks = retrieve_relevant_chunks(query, index, text_chunks, top_k=5)  # Increase retrieval depth

        if not relevant_chunks:
            print("\nNo relevant text found! Try rephrasing your question.\n")
            continue

        answer = generate_answer(query, relevant_chunks)
        print("\n💡 Answer:\n", answer)

# ==========================================
# RUN MAIN FUNCTION
# ==========================================

if __name__ == "__main__":
    main()