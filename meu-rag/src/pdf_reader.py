from pathlib import Path # Biblioteca orientada a objetos de lidar com caminhos de arquivos no python, ele garante que o meu código funcione tanto no windows quanto em outros sistemas que utilizam barra invertida
import pymupdf #Importa a biblioteca pymupdf

# função de extração. Ela recebe o caminho exato de onde o pdf está no pc
def read_pdf(pdf_path): 
    document = pymupdf.open(pdf_path) # Carregar arquivo binario do pdf para a memoria ram e criar um objeto iterável

    pages = [] # Aqui eu guardo as páginas extraídas

    for page_number, page in enumerate(document, start=1): # "document" funciona como uma lista de páginas, "enumerate" é uma função nativa do python excelente para loops, retorna "page_number" = índice e o conteúdo = "page". coloquei o "start" para iniciar no 1 porque o índice começa em 0.
        text = page.get_text() # extrai tudo o que for caractere legível, convertendo para str de py e preservando as \n.
        
        # Começo a criação de metadados. Quando eu for salvar isso no banco vetorial, a ideia é que a IA leia a chave "text". Quando for necessário mostrar as citações apra o usuário, o system vai olhar para as keys "page" e "source"
        page_data = {
            "text": text,
            "page": page_number,
            "source": Path(pdf_path).name
        }

        pages.append(page_data) # add dict criado na lista "pages".

# Importante frizar que sem o close o python manteria o documento "preso" na memória e quando o user tentasse deletar o arquivo o sistema negaria a ação com o argumento: "O arquivo está sendo usado ou aberto por outro programa".
    document.close()
    return pages 


project_root = Path(__file__).resolve().parent.parent # "__file__" contém o caminho do script atual. ".resolve()": Transforma caminhos relativos em absolutos. ".parent" sobre o nv da pasta e sai de pdf_reade.py para src, o segundo "parent" sobe mais um nível e sai de src e cai na pasta do projeto: meu-rag

pdf_path = project_root / "data" / "documents" / "Testando_protótipo.pdf" # é só o caminho exato até o pdf de teste


# Executa a função, apenas imprime tudo no console para eu testar se a extração funcionou.
pages = read_pdf(pdf_path) 

print(f"Total de páginas: {len(pages)}")

for page in pages:
    print(f"\n--- Página {page['page']}")
    print(f"fonte: {page['source']}")
    print(page["text"])