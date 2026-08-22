from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

# singleton pattern simplificado
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def generate_embedding(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:


    if not chunks:
        return []

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(texts, show_progress_bar=False)

    for chunks, embedding in zip(chunks, embeddings):

        chunks["embedding"] = embedding.tolist()

    return chunks


