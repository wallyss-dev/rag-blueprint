# Meu RAG

> **Um sistema de perguntas e respostas sobre documentos, construído do zero com Python.**

A ideia é simples:

**envie um PDF → o sistema entende o documento → faça uma pergunta → receba uma resposta baseada no conteúdo do documento.**

O objetivo deste projeto é construir uma pipeline de **Retrieval-Augmented Generation (RAG)** capaz de ler livros, artigos e outros documentos de texto, recuperar os trechos mais relevantes e utilizá-los como contexto para um LLM responder às perguntas do usuário.

Nada de mandar o PDF inteiro para o modelo e torcer para funcionar.

A proposta é construir cada etapa da pipeline de forma explícita, observável e modular.

---

## O que estou construindo?

Um sistema capaz de:

* receber documentos PDF;
* extrair seu conteúdo e metadados;
* dividir documentos grandes em pequenos chunks;
* transformar os chunks em embeddings;
* armazenar e indexar esses vetores;
* buscar semanticamente os trechos mais relevantes;
* enviar esses trechos para um LLM como contexto;
* gerar respostas baseadas nas evidências recuperadas;
* informar ao usuário **de qual arquivo e página veio a informação**.

Em outras palavras:

```text
                    ┌──────────────────┐
                    │      PDF         │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Extraction    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Chunking     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Embeddings    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Vector Store   │
                    └────────┬─────────┘
                             │
                             │
                    Pergunta do usuário
                             │
                             ▼
                    ┌──────────────────┐
                    │    Retrieval     │
                    └────────┬─────────┘
                             │
                      Top-K chunks
                             │
                             ▼
                    ┌──────────────────┐
                    │       LLM        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Resposta + Fonte │
                    └──────────────────┘
```

---

# Stack

A primeira versão será construída utilizando:

| Tecnologia                 | Responsabilidade                  |
| -------------------------- | --------------------------------- |
| **Python**                 | Linguagem principal               |
| **Streamlit**              | Interface da aplicação            |
| **LlamaIndex**             | Componentes e abstrações para RAG |
| **PyMuPDF**                | Extração de conteúdo dos PDFs     |
| **Sentence Transformers**  | Geração de embeddings             |
| **FAISS / NumPy**          | Armazenamento e busca vetorial    |
| **Google Gemini / OpenAI** | Geração das respostas             |
| **Regex**                  | Estratégia inicial de chunking    |

A stack poderá mudar conforme o projeto evoluir. A primeira versão tem uma prioridade:

> **entender o funcionamento da pipeline antes de abstraí-la completamente.**

---

# Estrutura do projeto

A organização inicial será:

```text
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
```

A separação existe por um motivo:

**cada parte da pipeline deve ter uma responsabilidade clara.**

---

# Arquitetura

A pipeline é dividida em sete etapas principais.

```text
PDF
 │
 ▼
[1] Extraction
 │
 ▼
[2] Chunking
 │
 ▼
[3] Embeddings
 │
 ▼
[4] Vector Store
 │
 ▼
[5] Retrieval
 │
 ▼
[6] LLM
 │
 ▼
[7] Citations
 │
 ▼
 UI
```

---

# 1. Extraction

Primeiro precisamos transformar o PDF em algo que o programa consiga manipular.

Um PDF é essencialmente um arquivo binário. O primeiro trabalho do sistema é extrair dele **texto + metadados**.

A ferramenta utilizada será o **PyMuPDF**.

A ideia é:

```python
{
    "text": "...conteúdo da página...",
    "source": "meu_livro.pdf",
    "page": 42
}
```

Cada página será convertida em uma estrutura que preserve sua origem.

Isso é importante porque não queremos apenas saber **o que** foi encontrado.

Queremos saber:

> **onde isso foi encontrado?**

Essa informação será utilizada posteriormente pelo sistema de citações.

### Responsabilidade

```text
PDF
 ↓
PyMuPDF
 ↓
texto + metadados
```

Arquivo responsável:

```text
src/document.py
```

---

# 2. Chunking

Documentos podem possuir milhares de páginas.

Não podemos simplesmente pegar todo o conteúdo e enviar para o modelo.

Precisamos dividir o documento em unidades menores chamadas **chunks**.

```text
Documento
    │
    ├── Chunk 01
    ├── Chunk 02
    ├── Chunk 03
    ├── Chunk 04
    └── ...
```

O objetivo é duplo:

1. manter o contexto dentro dos limites do modelo;
2. melhorar a precisão da busca semântica.

A estratégia inicial será baseada em **número de caracteres/tokens**, utilizando Regex e uma janela de sobreposição (*overlap*).

A ideia:

```text
Chunk A
████████████████████

             ████████████████████
             Chunk B
```

Utilizarei inicialmente um overlap entre **10% e 20%**.

Isso reduz a chance de uma informação importante ser perdida simplesmente porque uma frase ficou dividida exatamente na fronteira entre dois chunks.

### Exemplo

```text
Documento:

"Python é uma linguagem de programação criada por
Guido van Rossum e lançada inicialmente em 1991."

             ↓

Chunk 01:

"Python é uma linguagem de programação criada por
Guido van Rossum"

             ↓

Chunk 02:

"Guido van Rossum e lançada inicialmente em 1991."
```

A sobreposição mantém parte do contexto entre os blocos.

Arquivo responsável:

```text
src/chunking.py
```

---

# 3. Embeddings

Agora precisamos transformar texto em números.

Um **embedding** representa semanticamente um trecho de texto como um vetor em um espaço de alta dimensão.

Por exemplo:

```text
"Python é uma linguagem de programação"
                  │
                  ▼
        [0.12, -0.43, 0.87, ...]
```

Esse vetor não representa apenas as palavras.

A intenção é representar características semânticas do texto.

Isso permite comparar:

```text
"Como funciona Python?"
```

com:

```text
"Python é uma linguagem criada por Guido..."
```

mesmo que as duas frases não utilizem exatamente as mesmas palavras.

A primeira versão poderá utilizar:

* Sentence Transformers;
* Google GenAI embeddings;
* modelos equivalentes de embedding.

O fluxo será:

```text
Chunk
  │
  ▼
Embedding Model
  │
  ▼
Vector
```

Arquivo responsável:

```text
src/embeddings.py
```

---

# 4. Vector Store

Agora temos milhares de vetores.

Precisamos armazená-los e conseguir encontrar rapidamente quais são os mais próximos de uma determinada pergunta.

É aqui que entra o **Vector Store**.

Na primeira versão, a implementação poderá utilizar:

* FAISS;
* ou uma estrutura simples baseada em NumPy.

A associação básica será:

```text
ID
 │
 ├── embedding
 └── chunk
```

Por exemplo:

```python
{
    "id": 42,
    "embedding": [...],
    "text": "...",
    "source": "livro.pdf",
    "page": 87
}
```

A distância entre vetores pode ser calculada utilizando métricas como a **similaridade de cosseno**.

De forma simplificada:

```text
Vector da pergunta
        │
        ▼
      [ Q ]
       /|\
      / | \
     /  |  \
    ▼   ▼   ▼
  C01 C02 C03
```

Quanto mais próximos semanticamente os vetores estiverem, maior a relevância esperada.

Arquivo responsável:

```text
src/vector_store.py
```

---

# 5. Retrieval

Chegamos ao coração da arquitetura RAG.

O usuário faz uma pergunta:

```text
"Quem criou Python?"
```

Primeiro, essa pergunta também precisa virar um embedding.

```text
Pergunta
   │
   ▼
Embedding
   │
   ▼
Vector Store
```

Depois comparamos o vetor da pergunta com os vetores dos chunks.

A busca retorna os **K vizinhos mais próximos**.

```text
Pergunta
   │
   ▼
Embedding
   │
   ▼
┌──────────────────────┐
│    Vector Store      │
│                      │
│ Chunk 01   0.81      │
│ Chunk 02   0.23  ◄───┼── relevante
│ Chunk 03   0.76      │
│ Chunk 04   0.18  ◄───┼── relevante
│ Chunk 05   0.91      │
└──────────────────────┘
```

A primeira implementação utilizará **k-NN — K-Nearest Neighbors**.

A ideia é recuperar aproximadamente **3 a 5 chunks** mais relevantes.

Esses chunks serão então entregues ao LLM.

Arquivo responsável:

```text
src/retrieval.py
```

---

# 6. LLM

Agora temos:

```text
Pergunta do usuário
+
Chunks relevantes
```

É hora de gerar a resposta.

O LLM receberá um prompt estruturado contendo:

```text
SYSTEM:
Responda utilizando somente as informações presentes
no contexto fornecido.

CONTEXT:
[Chunk 1]

[Chunk 2]

[Chunk 3]

USER:
Quem criou Python?
```

A primeira implementação poderá utilizar a API do **Google Gemini**, por exemplo através do `google-genai` e de modelos da família Gemini.

A mesma camada poderá ser adaptada posteriormente para outros provedores.

A regra fundamental será:

> **o modelo não deve responder utilizando conhecimento externo quando a pergunta puder ser respondida somente com o documento recuperado.**

Isso transforma o LLM de uma fonte arbitrária de conhecimento em uma camada de geração sobre evidências recuperadas.

Arquivo responsável:

```text
src/chat.py
```

---

# 7. Citações

Uma resposta sem origem é difícil de auditar.

Por isso, cada chunk carregará seus metadados desde o início da pipeline.

```python
{
    "text": "...",
    "source": "livro.pdf",
    "page": 42
}
```

Quando o Retrieval recuperar um chunk:

```text
Chunk
 ├── text
 ├── source
 └── page
```

essas informações acompanham o contexto enviado ao LLM.

Depois da resposta, a interface poderá apresentar algo como:

```text
Python foi criado por Guido van Rossum.

Fontes:
- livro.pdf — página 42
- artigo.pdf — página 7
```

A implementação inicial será simples:

```text
retrieved_chunks
        │
        ├── source
        └── page
              │
              ▼
          Streamlit UI
```

O objetivo é garantir **rastreabilidade e auditabilidade**.

---

# UI

A interface é a camada final.

Nada disso precisa ser complicado.

A primeira versão utilizará **Streamlit** para criar uma interface reativa com:

```text
┌─────────────────────────────────────────────┐
│                  MEU RAG                    │
├─────────────────────────────────────────────┤
│                                             │
│  [ Upload PDF ]                             │
│                                             │
│  Documento: livro.pdf                       │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  Usuário: Quem criou Python?                │
│                                             │
│  RAG: Python foi criado por...              │
│                                             │
│  Fonte: livro.pdf — pág. 42                │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  [ Faça uma pergunta...              ]      │
│                                             │
└─────────────────────────────────────────────┘
```

A interface deverá permitir:

* upload de documentos;
* envio de perguntas;
* histórico da conversa;
* visualização das respostas;
* visualização das fontes utilizadas.

Arquivo principal:

```text
app.py
```

---

# O fluxo completo

Quando o usuário enviar um PDF:

```text
                 UPLOAD
                    │
                    ▼
              ┌───────────┐
              │    PDF    │
              └─────┬─────┘
                    │
                    ▼
             ┌──────────────┐
             │  Extraction  │
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │   Chunking   │
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │  Embeddings  │
             └──────┬───────┘
                    │
                    ▼
             ┌──────────────┐
             │ Vector Store │
             └──────────────┘
```

Quando o usuário fizer uma pergunta:

```text
              PERGUNTA
                  │
                  ▼
             Embedding
                  │
                  ▼
           Vector Store
                  │
                  ▼
              Top-K
              Chunks
                  │
                  ▼
           ┌────────────┐
           │    LLM     │
           └─────┬──────┘
                 │
                 ▼
          Resposta final
                 │
                 ▼
        + citações/fontes
```

Esse é o RAG.

Não existe mágica.

Existe uma sequência de transformações:

```text
Document
   ↓
Text
   ↓
Chunks
   ↓
Embeddings
   ↓
Vectors
   ↓
Retrieval
   ↓
Context
   ↓
LLM
   ↓
Answer
```

---

# Princípios do projeto

## 1. Modularidade

Cada etapa deve possuir uma responsabilidade.

```text
document.py      → lê
chunking.py      → divide
embeddings.py    → vetoriza
vector_store.py  → armazena
retrieval.py     → recupera
chat.py          → gera
app.py            → apresenta
```

Se algo quebrar, quero saber **onde** quebrou.

---

## 2. Evidência antes de geração

O LLM não deve receber o documento inteiro indiscriminadamente.

A ordem é:

```text
Retrieve
   ↓
Context
   ↓
Generate
```

Primeiro encontramos a evidência.

Depois geramos a resposta.

---

## 3. Rastreabilidade

Cada informação recuperada deve carregar sua origem.

```text
chunk
 ├── text
 ├── source
 └── page
```

Isso permitirá investigar posteriormente:

> "De onde exatamente essa resposta veio?"

---

## 4. Começar simples

A primeira versão não precisa de uma infraestrutura distribuída.

Não preciso começar com:

```text
Kubernetes
Redis
PostgreSQL
Milvus
Kafka
microservices
```

Se um:

```text
Python + NumPy + FAISS
```

resolver o problema inicial, é suficiente.

A complexidade deve aparecer quando houver necessidade real.

---

# Roadmap

## Fase 1 — MVP

* [ ] Criar estrutura do projeto
* [ ] Implementar upload de PDF
* [ ] Extrair texto com PyMuPDF
* [ ] Preservar `source` e `page`
* [ ] Implementar chunking
* [ ] Gerar embeddings
* [ ] Criar Vector Store
* [ ] Implementar busca k-NN
* [ ] Integrar LLM
* [ ] Criar prompt com contexto
* [ ] Implementar citações
* [ ] Criar interface Streamlit

## Fase 2 — Qualidade

* [ ] Avaliar qualidade dos chunks
* [ ] Testar diferentes tamanhos de chunk
* [ ] Testar diferentes overlaps
* [ ] Avaliar modelos de embedding
* [ ] Ajustar `top-k`
* [ ] Melhorar prompts
* [ ] Criar testes automatizados
* [ ] Medir qualidade do Retrieval

## Fase 3 — Evolução

* [ ] Suporte a múltiplos documentos
* [ ] Persistência do Vector Store
* [ ] Histórico de conversas
* [ ] Filtros por documento
* [ ] Reranking
* [ ] Hybrid Search
* [ ] Melhor tratamento de tabelas
* [ ] OCR para PDFs escaneados
* [ ] Observabilidade da pipeline

---

# Variáveis de ambiente

As credenciais não devem ficar dentro do código.

Utilizar:

```text
.env
```

e fornecer apenas um template:

```text
.env.example
```

Exemplo:

```env
GOOGLE_API_KEY=
OPENAI_API_KEY=
```

As chaves reais devem permanecer fora do repositório.

---

# Instalação

Clone o projeto e entre no diretório:

```bash
git clone <repository-url>

cd meu-rag
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente:

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

Depois execute:

```bash
streamlit run app.py
```

---

# Por que construir isso?

Porque um RAG parece simples quando visto de fora:

```text
PDF → IA → resposta
```

Mas por baixo existem vários problemas interessantes:

```text
Como extrair corretamente?
Como dividir o texto?
Qual tamanho de chunk?
Quanto overlap?
Qual embedding?
Como medir similaridade?
Quantos chunks recuperar?
Como evitar contexto irrelevante?
Como reduzir alucinações?
Como citar a fonte?
Como avaliar se a resposta realmente está fundamentada?
```

É exatamente nesses detalhes que está o aprendizado.

O objetivo deste projeto não é apenas **usar um framework de RAG**.

É entender o que acontece em cada etapa.

---

# Definition of Done — MVP

A primeira versão estará pronta quando eu conseguir executar:

```text
1. Abrir a aplicação
2. Enviar um PDF
3. Fazer uma pergunta sobre o documento
4. Recuperar os chunks relevantes
5. Gerar uma resposta com o LLM
6. Exibir a resposta
7. Exibir arquivo e página utilizados
```

Exemplo:

```text
USER

"Qual é a principal conclusão apresentada no capítulo 3?"
```

Pipeline:

```text
Pergunta
   ↓
Embedding
   ↓
k-NN
   ↓
Top 5 chunks
   ↓
Context
   ↓
Gemini
   ↓
Resposta
```

Resultado:

```text
A principal conclusão do capítulo 3 é ...

Fontes:
→ livro.pdf — página 87
→ livro.pdf — página 89
```

---

# Status

```text
[████████░░░░░░░░░░░░]  MVP em construção
```

Este projeto começa como um experimento pessoal para entender RAG por dentro.

A primeira versão será simples.

Depois, cada gargalo encontrado será tratado como um problema de engenharia.

> **Build it. Break it. Measure it. Improve it.**