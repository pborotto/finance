from fastapi import FastAPI, UploadFile, File, Form
import pdfplumber
import pandas as pd
from io import BytesIO

app = FastAPI()

@app.post("/extract-pdf")
async def extract_pdf(
    file: UploadFile = File(...),
    month: str = Form(...),
    year: str = Form(...)
):
    conteudo = await file.read()
    transacoes = []

    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            for linha in texto.split('\n'):
                linha = linha.strip()

                # Detecção simples de lançamentos
                if linha.startswith("R$ "):
                    transacoes.append({"linha": linha})

    return {
        "transactions": transacoes,
        "totalFound": len(transacoes),
        "month": month,
        "year": year
    }
