import os
from langchain_community.document_loaders import PyPDFLoader

def load_documents_from_directory(directory_path="data/"):
    all_docs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(directory_path, filename))
            docs = loader.load()
            all_docs.extend(docs)
    return all_docs