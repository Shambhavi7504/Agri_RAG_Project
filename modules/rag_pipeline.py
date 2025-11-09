import os
from dotenv import load_dotenv
import torch

# --- LangChain Core ---
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- LangChain Community (for vector stores, loaders, etc.) ---
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

# --- Text Splitting ---
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Embeddings (HuggingFace) ---
from langchain_huggingface import HuggingFaceEmbeddings

# --- Gemini Model (Google Generative AI) ---
from langchain_google_genai import ChatGoogleGenerativeAI

# --- External Tools ---
from serpapi import GoogleSearch


# -----------------------
# Environment Setup
# -----------------------
load_dotenv()


# -----------------------
# PDF Loader
# -----------------------
def load_documents_from_directory(directory_path="data/"):
    all_docs = []
    if not os.path.exists(directory_path):
        print(f"⚠️ Directory '{directory_path}' not found. Creating it...")
        os.makedirs(directory_path)
        return all_docs
    
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
    device = "cpu"  # Prevent CUDA/meta tensor issues
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
        print("⚠️ No PDF documents found in 'data/' directory.")
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
        print("⚠️ SERPAPI_API_KEY not found in .env file. Skipping web search.")
        return []

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
        print(f"❌ SerpAPI error: {e}")
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
# Simple Memory Implementation
# -----------------------
class SimpleMemory:
    def __init__(self, k=5):
        self.k = k
        self.chat_history = []
    
    def save_context(self, inputs, outputs):
        self.chat_history.append({"input": inputs.get("input"), "output": outputs.get("output")})
        if len(self.chat_history) > self.k:
            self.chat_history.pop(0)
    
    def get_history(self):
        return self.chat_history
    
    def get_history_string(self):
        history_str = ""
        for item in self.chat_history:
            history_str += f"Q: {item['input']}\nA: {item['output']}\n\n"
        return history_str


# -----------------------
# Create RAG Chain (Modern Approach)
# -----------------------
def create_rag_chain(retriever, llm):
    """Create a RAG chain using the modern LangChain API"""
    
    template = """Answer the question based only on the following context:

{context}

Question: {question}

Answer concisely and directly:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain


# -----------------------
# Hybrid RAG Pipeline
# -----------------------
def build_hybrid_rag():
    """
    Builds a hybrid Retrieval-Augmented Generation (RAG) pipeline
    using FAISS for dense retrieval and Gemini for response generation.
    """

    load_dotenv()

    # Initialize memory and Gemini model
    memory = SimpleMemory(k=5)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    # PDF retriever
    pdf_retriever = build_pdf_retriever()

    # Define the RAG function
    def rag(query):
        print("💬 Thinking...")
        combined_answer = ""

        # --- Step 1: Retrieve from PDFs ---
        if pdf_retriever:
            try:
                pdf_chain = create_rag_chain(pdf_retriever, llm)
                pdf_answer = pdf_chain.invoke(query)
                
                if pdf_answer:
                    combined_answer += f"📘 Context from PDFs:\n{pdf_answer}\n\n"
            except Exception as e:
                print(f"❌ PDF retrieval error: {e}")

        # --- Step 2: Retrieve from Web ---
        try:
            web_retriever = build_web_retriever(query)
            if web_retriever:
                web_chain = create_rag_chain(web_retriever, llm)
                web_answer = web_chain.invoke(query)
                
                if web_answer:
                    combined_answer += f"🌐 Web Info:\n{web_answer}\n"
        except Exception as e:
            print(f"❌ Web retrieval error: {e}")

        # --- Step 3: Save to memory ---
        if combined_answer:
            memory.save_context({"input": query}, {"output": combined_answer})
            return combined_answer

        # If no results, try direct LLM response
        try:
            direct_answer = llm.invoke(query).content
            memory.save_context({"input": query}, {"output": direct_answer})
            return f"💡 Direct answer:\n{direct_answer}"
        except Exception as e:
            print(f"❌ Direct LLM error: {e}")
            return "❌ Couldn't retrieve information from any source."

    return rag, memory