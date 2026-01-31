import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# chemin absolu vers le dossier rag_index
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
index_path = os.path.join(base_path, "rag_index")

# charger FAISS
db = FAISS.load_local(
    index_path, 
    embeddings, 
    allow_dangerous_deserialization=True
)

def retrieve_context(query, k=3):
    docs = db.similarity_search(query, k=k)
    return "\n".join([d.page_content for d in docs])
