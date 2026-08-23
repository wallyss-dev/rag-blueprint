import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel('gemini-1.5-flash')

def generate_answer(query: str, retrieved_chunks: List) -> str:
    context = "\n\n".join([f"Trecho (Página {c['page']}): {c['text']}" for c in retrieved_chunks])
    promtp = f"""Você é um assistente RAG. Responda à pergunta baseando-se APENAS no contexto abaixo.
Se a resposta não estiver no contexto, diga que não sabe. Não invente informações.
\nCONTEXTO:\n{context}\n\nPERGUNTA: {query}"""

    response = llm.generate_content(prompt)
    return response.text