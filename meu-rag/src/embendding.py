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


if __name__ == "__main__":
    from pdf_reader import read_pdf
    from chunking import chunk_text
    from pathlib import Path 

    project_root = Path(__file__).resolve().parent.parent 
    pdf_path = project_root / "data" / "document" / "Testando_protótipo"

    pages = read_pdf(pdf_path)
    chunks = chunk_text(pages, chunk_size=300, chunk_overlap=50)
    chunk_with_embeddings = generate_embedding(chunks)

    print(f"Total de chunks processados: {len(chunk_with_embeddings)}")

    first_chunk = chunk_with_embeddings[0]
    print(f"\n--- Chunk Vetorizado ---")
    print(f"ID: {first_chunk['chunk_id']}")
    print(f"Texto: {first_chunk['text'][:100]}")
    print(f"Dimensõesdo do vetor: {len(first_chunk['embedding'])}")
    print(f"Primeiros 5 números do vetor: {first_chunk['enbedding'][:5]}")