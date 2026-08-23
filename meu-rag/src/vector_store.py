import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

class VectorStore:
    def __init__(self):
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks_map = {}

    def add_chunks(self, chunks: list):
        if not chunks: return 
        text = [c["text"] for c in chunks]
        embeddings = model.encode(texts).astype('float32')
        startu_id = self.index.ntotal
        self.index.add(embeddings)
        for i, chunk in enumerate(chunks):
            self.chunks_map[start_id + i] = chunk

    def search(self, query: str, k: int = 3) -> List:
        if self.index.ntotal == 0: return []