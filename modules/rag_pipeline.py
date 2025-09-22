import os
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from serpapi import GoogleSearch
from langchain_community.document_loaders import PyPDFLoader
import torch

load_dotenv()

# -----------------------
# PDF Loader
# -----------------------
def load_documents_from_directory(directory_path="data/"):
    all_docs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(directory_path, filename))
            docs = loader.load()
            all_docs.extend(docs)
    return all_docs

# -----------------------
# HuggingFace Embeddings (CPU-safe)
# -----------------------
def get_hf_embeddings():
    device = "cpu"  # Force CPU to avoid meta tensor issues
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": device}
    )

# -----------------------
# Build PDF retriever
# -----------------------
def build_pdf_retriever():
    docs = load_documents_from_directory()
    if not docs:
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    split_docs = text_splitter.split_documents(docs)

    embeddings = get_hf_embeddings()
    db = FAISS.from_documents(split_docs, embeddings)
    return db.as_retriever()

# -----------------------
# SerpAPI Web Scraper
# -----------------------
def scrape_web_results(query, max_results=5):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("❌ SERPAPI_API_KEY is not set in .env file.")

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": max_results
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"❌ Error fetching SerpAPI results: {e}")
        return []

    documents = []
    for res in results.get("organic_results", []):
        title = res.get("title", "")
        snippet = res.get("snippet", "")
        link = res.get("link", "")
        content = f"{title}\n{snippet}\nSource: {link}"
        documents.append(Document(page_content=content, metadata={"source": link}))

    return documents

# -----------------------
# Build Web retriever
# -----------------------
def build_web_retriever(query, max_results=5):
    docs = scrape_web_results(query, max_results=max_results)
    if not docs:
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    split_docs = text_splitter.split_documents(docs)

    embeddings = get_hf_embeddings()
    db = FAISS.from_documents(split_docs, embeddings)
    return db.as_retriever()

# -----------------------
# Hybrid RAG with Memory
# -----------------------
def build_hybrid_rag():
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=10)
    pdf_retriever = build_pdf_retriever()

    def rag(query):
        print("💬 Thinking...")

        combined_answer = ""

        # Step 1: PDF retrieval
        if pdf_retriever:
            pdf_chain = RetrievalQA.from_chain_type(llm=llm, retriever=pdf_retriever)
            try:
                pdf_answer = pdf_chain.invoke({"query": query})["result"]
            except Exception:
                pdf_answer = ""

            if pdf_answer:
                combined_answer += f"📌 Context from PDFs:\n{pdf_answer}\n\n"

        # Step 2: Web retrieval
        web_retriever = build_web_retriever(query)
        if web_retriever:
            web_chain = RetrievalQA.from_chain_type(llm=llm, retriever=web_retriever)
            try:
                web_answer = web_chain.invoke({"query": query})["result"]
            except Exception:
                web_answer = ""

            if web_answer:
                combined_answer += f"📌 Specific policies from Web (SerpAPI):\n{web_answer}\n"

        # Step 3: Save to memory
        if combined_answer:
            memory.save_context({"input": query}, {"output": combined_answer})
            return combined_answer

        memory.save_context({"input": query}, {"output": "No answer found"})
        return "❌ Couldn’t retrieve info from PDFs or web."

    return rag, memory
