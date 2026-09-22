import requests
url = "https://apidadosabertos.saude.gov.br/daf/estoque-medicamentos-bnafar-horus?codigo_uf=35&limit=100&offset=0"
resposta = requests.get(url).json()

# A api tem a seguinte : Lista = [dicio_1,dicio_2,dicio_3] -> "parametros": [{"codigo_uf", "codigo_municipio"}] 
farmacia_desabastecida = []

farmacia_proxima_desabastecida = []

for medicamento in resposta["parametros"]:

    descricao = medicamento["descricao_produto"]
    estoque = medicamento["quantidade_estoque"]
    estado = medicamento["codigo_uf"]
    codigo_remedio = medicamento["codigo_catmat"]
    codigo_farmacia = medicamento["codigo_cnes"]

    if estoque == 0 and estado == 35:

         farmacia_desabastecida.append({
            "medicamento": descricao,
            "codigo_produto": codigo_remedio,
            "estoque": estoque,
            "municipio": medicamento["municipio"],
            "farmacia": medicamento["nome_fantasia"],
            "codigo_farmacia": codigo_farmacia
        })
    elif estoque < 50.0 and estado == 35:
            proximos_desabastecimento.append({
            "medicamento": descricao,
            "codigo_produto": codigo_remedio,
            "estoque": estoque,
            "municipio": medicamento["municipio"],
            "farmacia": medicamento["nome_fantasia"],
            "codigo_farmacia": codigo_farmacia
        })

    