import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import re

st.title("Renomeador de PDFs por OCR (Nome do Empregado)")

uploaded_files = st.file_uploader("Envie um ou mais arquivos PDF", type="pdf", accept_multiple_files=True)

def extrair_nome(texto):
    match = re.search(r"Nome[:\s]+([A-ZÂÊÍÓÚÃÕÇa-záéíóúãõç\s]+)", texto)
    return match.group(1).strip().replace(" ", "_") if match else "empregado_desconhecido"

def ocr_renomear(pdf_bytes):
    imagens = convert_from_bytes(pdf_bytes)
    texto_total = ""
    for img in imagens:
        texto_total += pytesseract.image_to_string(img, lang="por")
    nome = extrair_nome(texto_total)
    reader = PdfReader(pdf_bytes)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        writer.write(temp_pdf)
        return nome + ".pdf", temp_pdf.name

if uploaded_files:
    for file in uploaded_files:
        nome_final, caminho_pdf = ocr_renomear(file.read())
        with open(caminho_pdf, "rb") as f:
            st.download_button(
                label=f"Baixar {nome_final}",
                data=f.read(),
                file_name=nome_final,
                mime="application/pdf"
            )