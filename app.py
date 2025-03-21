from flask import Flask, request, render_template, send_file, redirect, url_for
import os
import camelot
import pandas as pd
import numpy as np
app = Flask(__name__)
BAIXAR_ARQUIVO = 'fusex'
app.config['BAIXAR_ARQUIVO'] = BAIXAR_ARQUIVO

if not os.path.exists(BAIXAR_ARQUIVO):
    os.makedirs(BAIXAR_ARQUIVO)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/enviar", methods= ["POST"])
def subir_arquivo():
    if request.method == "POST":
        if 'arquivo' not in  request.files:
            return "Nenhum arquivo encontrado."
    try:
        arquivo = request.files.get('arquivo')

        if not arquivo or arquivo.filename == '':
            return "Selecione um arquivo!"
        
        caminho_arquivo = os.path.join(app.config['BAIXAR_ARQUIVO'], arquivo.filename)
        arquivo.save(caminho_arquivo)

        tabelas = camelot.read_pdf(caminho_arquivo, pages="1", flavor="stream")
        users = []

        if tabelas.n > 0:
            df = tabelas[0].df
            if len(df) > 13:
                df.columns = df.iloc[7]  
                df.drop(range(8), inplace=True)
                    
                tabela_excel = pd.DataFrame({})
                tabela_excel["Nome"] = df["Atendimento"].str[7:]
                tabela_excel["Guia"] = np.where(
                    (df.iloc[:, 2].isna()) | (df.iloc[:, 2] == ""),
                    df.iloc[:, 1],
                    df.iloc[:, 2]
                )
                tabela_excel["Valor"] = df.iloc[:, -1]
                
                for _, row in tabela_excel.iterrows():
                    nome = row["Nome"]
                    guia = row["Guia"]
                    valor = row["Valor"].replace(".", "")
                    numero = float(valor.replace(",", "."))
                    encontrado = False
                    for item in users:
                        if item["NOME DO PACIENTE"] == nome and item["N Guia"] == guia:
                            item["QTD"] += 1
                            item["VALOR"] += numero
                            encontrado = True
                            break
                    if not encontrado:
                        users.append({"N Guia": guia, "NOME DO PACIENTE": nome, "QTD": 1, "VALOR": numero})
            else:
                df.columns = df.iloc[8]  
                df.drop(range(9), inplace=True)
                
                split_result = df["Início\nTérmino\nGuia TISS\nGuia\nNr.Conta\nAtendimento"].str.split("\n", expand=True)
                novas_colunas = ["Início", "Término", "Guia TISS", "Guia", "Nr.Conta", "Atendimento"]
                tabela2 = pd.DataFrame({})
                
                for x in range(5):
                    tabela2[novas_colunas[x]] = split_result[x]
                
                tabela2[["INICIO", "TERMINO"]] = tabela2["Início"].str.split(" ", expand=True)
                tabela2["Nome"] = df.iloc[:, 1]
                tabela2["Origem"] = df.iloc[:, 3]
                tabela2["Valor"] = df.iloc[:, 4]
                tabela2.drop(["Início", "Término"], axis=1, inplace=True)
                
                for _, row in tabela2.iterrows():
                    nome = row["Nome"]
                    guia = row["Guia TISS"]
                    valor = row["Valor"]
                    if valor:
                        valorr = row["Valor"].strip().replace(".", "")
                        numero = float(valorr.replace(",", "."))
                    encontrado = False
                    for item in users:
                        if item["NOME DO PACIENTE"] == nome and item["N GUIA"] == guia:
                            item["QTD"] += 1
                            item["VALOR"] += numero
                            encontrado = True
                            break
                    if not encontrado:
                        users.append({ "N GUIA": guia, "NOME DO PACIENTE": nome, "QTD": 1, "VALOR": numero})
            
            output_file = os.path.join(app.config['BAIXAR_ARQUIVO'], 'resultado.xlsx')
            pd.DataFrame(users).to_excel(output_file, index=False)

            return send_file(output_file, as_attachment=True)

        return render_template('index.html')
    
    except Exception as erro:
        return f"Erro {erro}"

if __name__ == '__main__':
    app.run(debug=True)
    #Libera o acesso para outros PCs na mesma rede
    # app.run(host="0.0.0.0", port=5000)


