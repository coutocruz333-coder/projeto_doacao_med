import requests
import pandas as pd
import sqlite3


# Pega os dados da API
url = "https://apidadosabertos.saude.gov.br/daf/estoque-medicamentos-bnafar-horus?codigo_uf=35&limit=100&offset=0"

resposta = requests.get(url).json()


# Dicionário para agrupar os registros
estoques_agrupados = {}


for medicamento in resposta.get("parametros", []):

    estado = medicamento.get("codigo_uf")

#Filtra para as farmácias apenas do Estado de São Paulo
    if estado == 35:

        codigo_farmacia = medicamento.get("codigo_cnes")
        codigo_produto = medicamento.get("codigo_catmat")
        chave = (codigo_farmacia, codigo_produto)

# Cria uma lista para cada combinação de farmácia(cnes) + produto(catmat) 
        if chave not in estoques_agrupados:
            estoques_agrupados[chave] = []

#Aqui irá armazenar na lista: estoques_agrupados[chave(codigo_farmacia,codigo_produto)] os valores da API
        estoques_agrupados[chave].append(medicamento)

estoque_sp_desabastecido = []
lotes_desabastecidos = []
estoque_sp_proximo = []

for chave, lotes in estoques_agrupados.items():

    estoque_total = 0

    for lote in lotes:
        estoque_total += lote.get("quantidade_estoque", 0)

    if estoque_total == 0:

        primeiro = lotes[0]

        estoque_sp_desabastecido.append({
            "medicamento": primeiro.get("descricao_produto"),
            "codigo_produto": primeiro.get("codigo_catmat"),
            "estoque": estoque_total,
            "municipio": primeiro.get("municipio"),
            "farmacia": primeiro.get("nome_fantasia"),
            "codigo_farmacia": primeiro.get("codigo_cnes")
        })

        # Guarda os lotes separadamente
        for lote in lotes:
            lotes_desabastecidos.append({
                "codigo_produto": lote.get("codigo_catmat"),
                "codigo_farmacia": lote.get("codigo_cnes"),
                "numero_lote": lote.get("numero_lote"),
                "data_validade": lote.get("data_validade"),
                "estoque": lote.get("quantidade_estoque")
            })

    elif estoque_total < 50:
        # próximo do desabastecimento
        primeiro = lotes[0]
        
        estoque_sp_proximo.append({
                    "medicamento": primeiro.get("descricao_produto"),
                    "codigo_produto": primeiro.get("codigo_catmat"),
                    "estoque": estoque_total,
                    "municipio": primeiro.get("municipio"),
                    "farmacia": primeiro.get("nome_fantasia"),
                    "codigo_farmacia": primeiro.get("codigo_cnes")
                })


# 4. Transforma na tabela do Pandas
df_desabastecido = pd.DataFrame(estoque_sp_desabastecido)
df_proximo = pd.DataFrame(estoque_sp_proximo)
df_lotes = pd.DataFrame(lotes_desabastecidos)

# 5. Conecta ao banco
conexao = sqlite3.connect("dados_saude.db")


# 6. Salva os dados
df_desabastecido.to_sql(
    "estoque_desabastecido",
    conexao,
    if_exists="replace",
    index=False
)

df_proximo.to_sql(
    "estoque_proximo",
    conexao,
    if_exists="replace",
    index=False
)

df_lotes.to_sql(
    "lotes",
    conexao,
    if_exists="replace",
    index=False
)

# 7. Fecha a conexão
conexao.close()


print("Banco de dados criado e atualizado com sucesso!")