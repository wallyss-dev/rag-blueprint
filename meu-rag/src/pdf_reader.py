from pathlib import Path 
import pymupdf #Importa a biblioteca pymupdf

project_root = Path(__file__).resolve().parent.parent

pdf_path = project_root / "data" / "documents" / "contrato.pdf"

document = pymupdf.open(pdf_path)

print(f"PDF: {pdf_path}")
print(F"Total de páginas: {len(document)}")

for page_number, page in enumerate(document, start=1): #percorremos cada página 
    text = page.get_text() # Aqui extraimos o trecho da página

    print(f"/n--- Página {page_number} ---")
    print(text)