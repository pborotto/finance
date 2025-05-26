from fastapi import FastAPI, UploadFile, File
import pdfplumber
import pandas as pd
from io import BytesIO

app = FastAPI()

@app.post("/processar")
async def processar_pdf(file: UploadFile = File(...)):
    conteudo = await file.read()
    transacoes = []

    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            for linha in texto.split('\n'):
                linha = linha.strip()

                # Detecção simples de transações (pode melhorar depois com regex)
                if linha.startswith("R$ "):
                    transacoes.append({"linha": linha})

    return {"transacoes": transacoes}
