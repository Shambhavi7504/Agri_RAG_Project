from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from modules.rag_pipeline import build_pdf_retriever, build_web_retriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

def build_hybrid_rag_with_memory():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")  # Add your API key in env

    # Build retrievers
    pdf_retriever = build_pdf_retriever()
    web_retriever = build_web_retriever()  # cached at startup

    # Combine PDF + Web in a single chain for conversational retrieval
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Conversational chain with both retrievers (prioritize PDF)
    if pdf_retriever and web_retriever:
        # Create two QA chains
        from langchain.chains import RetrievalQA
        pdf_chain = RetrievalQA.from_chain_type(llm=llm, retriever=pdf_retriever)
        web_chain = RetrievalQA.from_chain_type(llm=llm, retriever=web_retriever)

        # Our function to maintain context
        def rag(query):
            print("💬 Thinking...")
            # Include chat history for follow-ups
            chat_history = memory.load_memory_variables({})["chat_history"]

            # Step 1: PDF
            pdf_answer = ""
            try:
                pdf_answer = pdf_chain.invoke({"query": query})["result"]
            except Exception:
                pdf_answer = ""

            if pdf_answer and len(pdf_answer.strip()) > 20:
                memory.save_context({"input": query}, {"output": pdf_answer})
                return f"📌 From PDFs:\n{pdf_answer}"

            # Step 2: Web fallback
            web_answer = ""
            try:
                web_answer = web_chain.invoke({"query": query})["result"]
            except Exception:
                web_answer = ""

            if web_answer:
                memory.save_context({"input": query}, {"output": web_answer})
                return f"📌 From Web:\n{web_answer}"

            memory.save_context({"input": query}, {"output": "No answer found"})
            return "❌ Couldn’t retrieve info from PDFs or web."

        return rag, memory

    else:
        raise ValueError("No retrievers available")
