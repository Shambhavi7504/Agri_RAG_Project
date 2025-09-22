from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from .loader import load_documents

def build_vectorstore():
    docs = load_documents()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore
