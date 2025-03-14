import pdfplumber
import pandas as pd
import re
import os

# Caminho do PDF
pdf_path = "./dados/fatura_cartaobusiness6505_2025-03.pdf"

def extrair_gastos(pdf_path):
    dados = []
    with pdfplumber.open(pdf_path) as pdf:
        titular = None
        cartao_final = None

        for page in pdf.pages:
            words = page.extract_words()  # Captura palavras individuais
            linhas = []
            linha_atual = []

            # Organiza as palavras em linhas (para evitar problemas com colunas desalinhadas)
            last_y = None
            for word in words:
                y = word["top"]
                text = word["text"]

                if last_y is not None and abs(y - last_y) > 5:
                    linhas.append(" ".join(linha_atual))
                    linha_atual = []

                linha_atual.append(text)
                last_y = y

            if linha_atual:
                linhas.append(" ".join(linha_atual))

            # Processa cada linha para encontrar informações
            for linha in linhas:
                linha = linha.strip()

                # Detecta titular e número do cartão
                match_titular_cartao = re.search(r"(\b[A-Z ]+\b)\s+\(final\s+(\d{4})\)", linha)
                if match_titular_cartao:
                    titular = match_titular_cartao.group(1).strip()
                    cartao_final = match_titular_cartao.group(2)

                # Padrão para capturar data, estabelecimento e valor
                matches = re.findall(r"(\d{2}/\d{2})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})", linha)

                # matches = re.findall(r"(\d{2}/\d{2})\s+([^\d]+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})", linha)

                for match in matches:
                    if titular and cartao_final:
                        data = match[0]
                        estabelecimento = match[1].strip()
                        valor = float(match[2].replace(".", "").replace(",", "."))

                        # Se for estorno, transformar em negativo
                        if "ESTORNO" in estabelecimento.upper():
                            valor = -valor

                        dados.append([titular, cartao_final, data, estabelecimento, valor])

    # Criar DataFrame
    df = pd.DataFrame(dados, columns=["Titular", "Cartão Final", "Data", "Estabelecimento", "Valor (R$)"])
    return df

# Extraindo os gastos do PDF
df_gastos = extrair_gastos(pdf_path)

# Exibir os resultados
# print(df_gastos)
df_gastos.to_excel("./dados/saidas/gastos_cartao.xlsx")

def verificar_arquivo(caminho_arquivo):
    if os.path.isfile(caminho_arquivo):
        print(f"O arquivo '{caminho_arquivo}' foi criado com sucesso.")
    else:
        print(f"O arquivo '{caminho_arquivo}' não foi encontrado.")

# Exemplo de uso
caminho = "./dados/saidas/gastos_cartao.xlsx" 
verificar_arquivo(caminho)
