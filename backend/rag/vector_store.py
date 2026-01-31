import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

DATA_DIR = "../data"      # your folder with .md files
INDEX_DIR = "rag_index"

def build_faiss_index():
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Load all .md files
    docs = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".md"):
            path = os.path.join(DATA_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                docs.append(Document(page_content=content, metadata={"source": fname}))
    
    # Build FAISS index
    db = FAISS.from_documents(docs, embeddings)
    
    # Save index locally
    db.save_local(INDEX_DIR)
    print(f"✅ FAISS index saved in '{INDEX_DIR}' folder.")

if __name__ == "__main__":
    build_faiss_index()
