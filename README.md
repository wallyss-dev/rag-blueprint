# 📚 RAG do Zero (Retrieval-Augmented Generation)

Projeto focado na construção de um sistema RAG modular, entendendo cada decisão técnica por trás da arquitetura, sem depender exclusivamente de frameworks "caixa-preta".

## 🏗️ Arquitetura do Projeto (MVP)
1. **Extração:** `PyMuPDF` (Converte PDF para texto preservando metadados).
2. **Chunking:** Janela deslizante com sobreposição (Overlap).
3. **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`).
4. **Vector Store:** `FAISS` para indexação e busca por similaridade (L2/Cosseno).
5. **Geração (LLM):** `Google Gemini 1.5 Flash`.
6. **Interface:** `Streamlit`.

## 🚀 Como Executar
1. Clone o repositório e crie um ambiente virtual (`python -m venv venv`).
2. Instale as dependências: `pip install -r requirements.txt`.
3. Crie um arquivo `.env` na raiz com a sua chave: `GEMINI_API_KEY=sua_chave`.
4. Execute a aplicação: `streamlit run app.py`.