import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()


Settings.llm = Gemini(model="models/gemini-1.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
Settings.embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")

print("Carregando documentos...")

documentos = SimpleDirectoryReader("data/documents").load_data()