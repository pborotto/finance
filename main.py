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

    # Regex para transações nacionais (com ou sem sinal negativo)
    regex_transacao = r"(\d{2} [A-Za-z]{3})\s+(.+?)\s+(-?)R\$ (\d{1,3}(?:\.\d{3})*,\d{2})"

    # Regex para valor convertido em transações internacionais
    regex_conversao = r"Convers[aã]o para Real\s*-\s*R\$ (\d{1,3}(?:\.\d{3})*,\d{2})"

    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for i, pagina in enumerate(pdf.pages):
            if i < 2:
                continue  # Ignora as duas primeiras páginas (resumo)

            texto = pagina.extract_text()
            if not texto:
                continue

            linhas = texto.split('\n')
            for idx, linha in enumerate(linhas):
                linha = linha.strip()

                # 🔹 Transações nacionais (1 ou 2 por linha, com ou sem "-")
                for match in re.finditer(regex_transacao, linha):
                    data = match.group(1)
                    descricao = match.group(2).strip()
                    sinal = match.group(3)
                    valor = match.group(4)

                    if sinal == "-":
                        valor = f"-{valor}"

                    transacoes.append({
                        "data": data,
                        "descricao": descricao,
                        "valor": valor
                    })

                # 🌍 Transações internacionais (ex: US$ + Conversão)
                if "US$" in linha and idx + 2 < len(linhas):
                    linha_atual = linha
                    prox2 = linhas[idx + 2].strip()

                    match_data_desc = re.match(r"(\d{2} [A-Za-z]{3})\s+(.+?)\s+US\$ ", linha_atual)
                    if match_data_desc:
                        data = match_data_desc.group(1)
                        descricao = match_data_desc.group(2).strip()

                        match_conversao = re.search(regex_conversao, prox2)
                        if match_conversao:
                            valor_convertido = match_conversao.group(1)
                            transacoes.append({
                                "data": data,
                                "descricao": descricao,
                                "valor": valor_convertido,
                                "internacional": True
                            })

    return {
        "transactions": transacoes,
        "totalFound": len(transacoes),
        "month": month,
        "year": year
    }
