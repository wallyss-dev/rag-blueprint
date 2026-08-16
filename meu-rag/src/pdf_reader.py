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

pages = read_pdf(pdf_path)

print(f"Total de páginas: {len(pages)}")

for page in pages:
    print(f"\n--- Página {page['page']}")
    print(f"fonte: {page['source']}")
    print(page["text"])