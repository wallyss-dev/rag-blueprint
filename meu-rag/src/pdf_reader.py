from pathlib import Path 
import pymupdf #Importa a biblioteca pymupdf

def read_pdf(pdf_path):
    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        page_data = {
            "text": text,
            "page": page_number,
            "source": Path(pdf_path).name
        }

        pages.append(page_data)

    document.close()

    return pages
 






project_root = Path(__file__).resolve().parent.parent

pdf_path = project_root / "data" / "documents" / "Testando_protótipo.pdf"

pages = read_path(pdf_path)

print(f"Total de páginas: ")



print(f"PDF: {pdf_path}")
print(F"Total de páginas: {len(document)}")

for page_number, page in enumerate(document, start=1): #percorremos cada página 
    text = page.get_text() # Aqui extraimos o trecho da página

    print(f"/n--- Página {page_number} ---")
    print(text)