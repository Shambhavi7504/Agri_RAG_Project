import os
from langchain_community.document_loaders import PyPDFLoader

def load_documents():
    documents = []
    data_folder = "data"
    for file in os.listdir(data_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(data_folder, file))
            documents.extend(loader.load())
    return documents
