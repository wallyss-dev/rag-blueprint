import streamlit as st
from src.documents import extract_text_from_pdf
from src.chunking import chunk_text
from src.vector_store import VectorStore

st.set_page_config(page_title="Meu Rag", layout="wide")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()

st.title("Sistema RAG")

uploaded_file = st.file_uploader("Envie seu PDF", type=["pdf"])
if uploaded_file and st.botton("Processar Documento"):
    with st.spinner("Extraido e vorizando......"):
        pages = extract_text_from_pdf(uploaded_file;read()), uploaded_file
        chunks = chunk_text(pages)
        st.session_state.vector_store.add_chunks(chunks)
        st.success(f"{len(chunks)} chunks indexados com sucesso!!!")

query = st.chat_input("Faça uma pergunta sobre o documento......")
if query:
    st.chat_message("user").write(query)
    with st.spinner("Buscando e gerando resposta...."):

        relevant_chunks = st.session_state.vector_store.search(query)

        answer = generate_answer(query, relevant_chunks)

        with st.chat_message("assitant"):
            st.write(answer)
            st.divider()
            st.write("**Citações (Fontes utilizadas):**")
            for c in relevant_chunks:
                st.caption(f"- {c['source']} (Página {c['page']})")

