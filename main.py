from fastapi import FastAPI, UploadFile, File, Form
import pdfplumber
import re
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

    # Regex que captura: data + descrição + valor (formato BR)
    regex_transacao = r"^(\d{2} [A-Za-z]{3})\s+(.+?)\s+R\$ (\d{1,3}(?:\.\d{3})*,\d{2})$"

    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for i, pagina in enumerate(pdf.pages):
            if i < 2:
                continue  # pula as duas primeiras páginas (resumo geral)

            texto = pagina.extract_text()
            if not texto:
                continue

            for linha in texto.split('\n'):
                linha = linha.strip()

                match = re.match(regex_transacao, linha)
                if match:
                    data = match.group(1)
                    descricao = match.group(2).strip()
                    valor = match.group(3)
                    transacoes.append({
                        "data": data,
                        "descricao": descricao,
                        "valor": valor
                    })

    return {
        "transactions": transacoes,
        "totalFound": len(transacoes),
        "month": month,
        "year": year
    }
