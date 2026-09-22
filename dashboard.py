import sqlite3
import pandas as pd

# Conecta no banco de dados
conexao = sqlite3.connect("dados_saude.db")

# Lê a tabela inteira e joga num DataFrame
df = pd.read_sql_query("SELECT * FROM estoque_desabastecido", conexao)

# Fecha a conexão
conexao.close()

# Mostra as 5 primeiras linhas da tabela
print(df.head())