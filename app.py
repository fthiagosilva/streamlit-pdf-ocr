import streamlit as st
import requests
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import io
import re

OCR_API_URL = "https://api.ocr.space/parse/image"
API_KEY = "helloworld"  # chave pública de teste (limite diário)

st.title("Renomeador de PDFs com OCR via API (OCR.space)")

uploaded_files = st.file_uploader("Envie um ou mais arquivos PDF", type="pdf", accept_multiple_files=True)

def extrair_nome(texto):
    match = re.search(r"Nome[:\s]+([A-ZÂÊÍÓÚÃÕÇa-záéíóúãõç\s]+)", texto)
    return match.group(1).strip().replace(" ", "_") if match else "empregado_desconhecido"

def enviar_para_ocr(image_bytes):
    response = requests.post(
        OCR_API_URL,
        files={"file": image_bytes},
        data={"language": "por", "isOverlayRequired": False},
        headers={"apikey": API_KEY}
    )
    result = response.json()
    try:
        return result["ParsedResults"][0]["ParsedText"]
    except:
        return ""

def converter_pdf_para_imagens(pdf_bytes):
    from fitz import open as fitz_open
    import fitz
    doc = fitz_open(stream=pdf_bytes, filetype="pdf")
    imagens = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        imagens.append(io.BytesIO(pix.tobytes("png")))
    return imagens

def processar_pdf(pdf_bytes):
    imagens = converter_pdf_para_imagens(pdf_bytes)
    texto_total = ""
    for img in imagens:
        img.seek(0)
        texto_total += enviar_para_ocr(img)

    nome = extrair_nome(texto_total)
    novo_nome = f"{nome}.pdf"

    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        writer.write(temp_pdf)
        return novo_nome, temp_pdf.name

if uploaded_files:
    for file in uploaded_files:
        nome_final, caminho_pdf = processar_pdf(file.read())
        with open(caminho_pdf, "rb") as f:
            st.download_button(
                label=f"Baixar {nome_final}",
                data=f.read(),
                file_name=nome_final,
                mime="application/pdf"
            )