from typing import List, Dict, Any 

def chunk_text(
        pages_data: List[Dict[str, Any]],
        chunk_size: int = 500,
        chunk_overlap: int = 100
) -> List[Dict[str, Any]]:

    chunks = []
    chunk_id = 0

    for page in pages_data:
        text = page["text"]
        page_number = page["page"]
        source = page["source"]

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk_text_slice = text[start:end]


            if chunk_text_slice.strip():
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text_slice.strip(),
                    "page": page_number,
                    "source": source
                })
                chunk_id += 1

                start += (chunk_size + chunk_overlap)

            return chunks