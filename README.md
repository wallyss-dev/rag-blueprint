
Meu objetivo é construir um sistema que leia e interprete pdfs, você pode enviar livros, artigos, qualquer documento de texto e fazer perguntas que o LLM do sistema te responderá de acordo com as informações do documento.
Vou construir uma pipeline RAG (Retrieval-Augmnted Generation) uma técnica de IA que conecta modelos de linguagem LLMs a bases de dados externos. Farei em python

Como tecnologias irei utilizar python, streamlit llamaindex, pymupdf, sentence-transformers, faiss ou vector store simples e open IA para a versão inicial do projeto.

Para começar, nada melhor do que destrinchar a organização das pastas:
meu-rag/
│
├── app.py
│
├── src/
│   ├── document.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retrieval.py
│   └── chat.py
│
├── data/
│   └── documents/
│
├── tests/
│
├── .env.example
├── requirements.txt
└── README.md

Arquitetura do RAG:
Etapa 1: Extração
Aqui eu viso converter um arquivo binário PDF em texto puro com metadados, para que meu sistema consiga ler dados brutos e mapear a origem de cada trecho. Utilizei o PyMuPDF uma biblioteca do python para abrir o documento, iterar pelas páginas e estruturar o retorno em dicionários py.

Etapa 2: Chunking (fatiamento)
De strings longas do documento em blocos menores de texto (chunks). Quero garantir que o texto caiba no Context Window, e tornar a busca por similaridade mais precisa. Decidi utilizar Regex. A ação tomada foi fatiar string por número de caracteres/tokens aplicando uma sobreposição overlap de 10% a 20% para não quebrar frases no meio.

Etapa 3: Embedding
É o mapeamento do texto em um vetor num de alta dimensão (Um array de muitos elementos). Serve para traduzir o significado semântico das palavras para coordenadas no espaço geométrico. Utilizei Google GenAI API (text-embedding-004 ou sentence-transformers). A ideia é enviar a string do chunk para a API/modelo e receber como resposta uma lista de floats que representa o vetor.

Etapa 4: Vector Store
É um DB otimizado para armazenamento e indexação de vetores numéricos. Obj é guardar os embeddings na memória e permitir cálculos de distância geométrica rápidos. Vou tilizar FAIss ou Numpy. Objetivo é salvar os vetores associados ao ID dos chunks. Para buscar. Calcula-se a distancia vetorial, como a similaridade de Cosseno:

Etapa 5: Retrieval
Processo de busca semântica que pesquisa os k chunks mais próximos da pergunta. Ele seleciona apenas os 3 a 5 trechos mais relevantes do PDF para responder á dúvida do usuário.
Vou utilizar Algoritmo k-NN(K-Nearest Neighbors). Quero vetorizar a pergunta do user usando o mesmo modelo de embedding e consultar o Vector Store para retornar os k índices com menor distância.

Etapa 6: LLM 
Vai ser o modelo que recebe a pergunta concatenada com os chunks restados. Ele vai processar a informação resgatada e redigir uma resposta natural e coesa. Vou utilizar Google Gemini API (google-genai ou gemini-2.5-flash). Para criar um system prompt injetando os chunks como contexto e forçando a IA a responder baseada unicamente nessas evidências.

Etapa 7: Citações
Vai ser o mecanismo de rastreabilidade do sistema. Para garantir auditabilidade para que o user saiba qual página e arquivo a IA retirou a resposta. Lógica de python msm. Para recuperar as chaves “source” e “page” presas ao dicionário do chunk resgatado e exibir na interface junto com o texto.

Final: UI
Apenas a apresentação gráfica. Quero que a interface permita upload de arquivos, envio de mensagens e visualização do histórico do chat. Vou utilizar o stramlit. Objetivo é utilizar componentes reativos
