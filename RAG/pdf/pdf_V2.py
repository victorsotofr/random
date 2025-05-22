# ==========================================
# RAG SYSTEM FOR PDFs
# Extracts information from PDFs and allows users to ask questions.
# ==========================================
# SOURCES:
# MAIN GUIDE: https://python.langchain.com/docs/tutorials/rag/
# With the BIG HELP of this guy: https://www.youtube.com/watch?v=ZCSsIkyCZk4
# ==========================================

# SETUP
import getpass
import os
import openai
from langchain_openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.chains import RetrievalQA

# ==========================================
# SETTING UP OPENAI API KEY
# ==========================================

# os.environ["OPENAI_API_KEY"] = "sk-"

if not os.environ.get("OPENAI_API_KEY"):
    api_key = getpass.getpass("Enter your API key here: ")
    os.environ["OPENAI_API_KEY"] = api_key
else:
    api_key = os.environ["OPENAI_API_KEY"]

# ==========================================
# PROCESSING PDFs
# ==========================================
PDF_DIR = "./pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def load_pdfs(directory):
    """Loads all PDFs in a directory and extracts text."""
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
    return documents
    
def process_documents(documents):
    """Splits documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return text_splitter.split_documents(documents)

# ==========================================
# RETRIEVER - FAISS VECTORSTORE FOR EMBEDDINGS
# ==========================================
def build_faiss_vectorstore(chunks):
    """Embeds text chunks and stores them in a FAISS index."""
    embeddings = OpenAIEmbeddings(openai_api_key = api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = VectorStoreRetriever(vectorstore = vectorstore)
    return retriever

# ==========================================
# QUERYING THE DOCUMENTS
# ==========================================
def query_documents(query, retriever):
    """Retrieves relevant chunks and generates an answer using OpenAI."""
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(api_key = api_key),
        retriever=retriever
    )
    response = qa_chain.invoke({"query": query})
    return response["result"] if isinstance(response, dict) and "result" in response else response

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    pdf_documents = load_pdfs(PDF_DIR)
    if not pdf_documents:
        print("No PDFs found. Add PDFs to the 'pdfs' directory and try again.")
        return
    
    chunks = process_documents(pdf_documents)
    retriever = build_faiss_vectorstore(chunks)
    
    print("\nReady for questions! Type 'exit' to quit.")
    
    while True:
        query = input("\n❓ Your question: ").strip()
        if query.lower() == "exit":
            print("\nExiting. Thanks for using the PDF Q&A system by Victor SOTO!")
            break
        
        answer = query_documents(query, retriever)
        print("\n💡 Answer:\n", answer)

if __name__ == "__main__":
    main()