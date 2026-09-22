import requests
import pandas as pd
import sqlite3


# 1. Pega os dados da API
url = "https://apidadosabertos.saude.gov.br/daf/estoque-medicamentos-bnafar-horus?codigo_uf=35&limit=100&offset=0"
resposta = requests.get(url).json()




estoque_sp_desordenado = []

# 2. Filtra apenas o que importa (estoque < 50 em SP)
for medicamento in resposta.get("parametros", []):
    estoque = medicamento.get("quantidade_estoque", 0)
    estado = medicamento.get("codigo_uf")

    if estado == 35 and estoque < 50.0:
        estoque_sp_desordenado.append({
            "medicamento": medicamento.get("descricao_produto"),
            "codigo_produto": medicamento.get("codigo_catmat"),
            "estoque": estoque,
            "municipio": medicamento.get("municipio"),
            "farmacia": medicamento.get("nome_fantasia"),
            "codigo_farmacia": medicamento.get("codigo_cnes")
        })

# 3. Transforma na tabela do Pandas
df = pd.DataFrame(estoque_sp_desordenado)

# 4. O Python cria o arquivo "dados_saude.db" automaticamente na sua pasta!
conexao = sqlite3.connect("dados_saude.db")

# 5. Salva os dados lá dentro
df.to_sql("estoque_desabastecido", conexao, if_exists="replace", index=False)

# 6. Fecha a porta do banco
conexao.close()

print("Banco de dados criado e atualizado com sucesso!")



# 4. Conta os problemas por farmácia e gera o gráfico interativo
#resumo_farmacias = df.groupby('farmacia').size().reset_index(name='qtd_remedios_alerta')

#grafico = px.bar(
#    resumo_farmacias,
#    x='farmacia',
#    y='qtd_remedios_alerta',
#    title='💊 Farmácias com Medicamentos em Alerta (Estoque < 50)',
#    labels={'farmacia': 'Nome da Farmácia', 'qtd_remedios_alerta': 'Quantidade de Alertas'}
#)

#grafico.show()

#grafico.write_html("meu_grafico.html")