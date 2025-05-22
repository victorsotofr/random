# ==========================================
# RAG SYSTEM FOR WIKIPEDIA Q&A
# Scrapes Wikipedia's "Zidane" page and allows users to ask questions.
# ==========================================
# SOURCES:
# MAIN GUIDE: https://python.langchain.com/docs/tutorials/rag/
# ==========================================

import os
import getpass
import bs4
from typing_extensions import List, TypedDict

# LangChain Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from langchain import hub
from langchain_core.documents import Document

# ==========================================
# SETTING UP OPENAI API KEY
# ==========================================

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

# ==========================================
# MODELS INITIALIZATION
# ==========================================

# Load OpenAI chat model
llm = ChatOpenAI(model="gpt-4o-mini")

# Load OpenAI embeddings for vector storage
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Initialize in-memory vector store
vector_store = InMemoryVectorStore(embeddings)

# ==========================================
# SCRAPE WIKIPEDIA (ZIDANE PAGE)
# ==========================================

print("Scraping Wikipedia's Zidane page...")

loader = WebBaseLoader(
    web_paths=("https://en.wikipedia.org/wiki/Zinedine_Zidane",),
    bs_kwargs=dict(parse_only=bs4.SoupStrainer(id="bodyContent"))  # We will extract the main content only
)

docs = loader.load()

# ==========================================
# TEXT CHUNKING & INDEXING
# ==========================================

print("Splitting text into chunks...")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

print(f"Indexed {len(all_splits)} document chunks.")

# Add chunks to vector store
vector_store.add_documents(documents=all_splits)

# ==========================================
# PROMPT SETUP FOR Q&A
# ==========================================

prompt = hub.pull("rlm/rag-prompt")

# ==========================================
# APPLICATION STATE
# ==========================================

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# ==========================================
# RETRIEVAL FUNCTION
# ==========================================

def retrieve(state: State):
    """
    Retrieves relevant documents from the vector store based on the question.
    If the context does not contain the answer, simply respond: "I don't know based on the provided corpus."
    """
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

# ==========================================
# RESPONSE GENERATION FUNCTION
# ==========================================

def generate(state: State):
    """Generates an answer using the retrieved context."""
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

# ==========================================
# BUILD & COMPILE EXECUTION GRAPH
# ==========================================

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# ==========================================
# ASK A QUESTION & GET AN ANSWER
# ==========================================

print("\n Give us your question! I am stronger if we talk about Zidane ⚽️.")

while True:
    question = input("\n ❓ Your question: ").strip()

    if question.lower() == "exit": # Exit condition
        print("Thanks for using us!")
        break

    # Get response from the RAG system
    response = graph.invoke({"question": question})

    print(f"💡 Answer: {response['answer']}")
