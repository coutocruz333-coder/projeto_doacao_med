
import sqlite3
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Dashboard BNAFAR",
    page_icon="💊",
    layout="wide"
)

st.title("Dashboard de Estoque de Medicamentos")
st.caption("Consulta de estoques de farmácias públicas de São Paulo")

# 1. Carrega as tabelas do banco de dados
@st.cache_data
def carregar_dados():
    with sqlite3.connect("dados_saude.db") as conexao:
        desabastecido = pd.read_sql_query(
            "SELECT * FROM estoque_desabastecido",
            conexao
        )

        proximo = pd.read_sql_query(
            "SELECT * FROM estoque_proximo",
            conexao
        )

        lotes_desabastecidos = pd.read_sql_query(
            "SELECT * FROM lotes_desabastecidos",
            conexao
        )

        lotes_proximos = pd.read_sql_query(
            "SELECT * FROM lotes_proximos",
            conexao
        )

    return (
        desabastecido,
        proximo,
        lotes_desabastecidos,
        lotes_proximos
    )


df_desabastecido, df_proximo, df_lotes_desabastecidos, df_lotes_proximos = carregar_dados()


# 2. Função para filtrar e exibir uma categoria
def mostrar_estoques(df, df_lotes, titulo, chave):

    st.subheader(titulo)

    if df.empty:
        st.info("Não há registros nesta categoria.")
        return

    # Filtro por município
    municipios = ["Todos"] + sorted(
        df["municipio"].dropna().astype(str).unique().tolist()
    )

    municipio = st.selectbox(
        "Município",
        municipios,
        key=f"municipio_{chave}"
    )

    filtrado = df.copy()

    if municipio != "Todos":
        filtrado = filtrado[
            filtrado["municipio"].astype(str) == municipio
        ]

    # Filtro por farmácia, conforme o município selecionado
    farmacias = ["Todas"] + sorted(
        filtrado["farmacia"].dropna().astype(str).unique().tolist()
    )

    farmacia = st.selectbox(
        "Farmácia",
        farmacias,
        key=f"farmacia_{chave}"
    )

    if farmacia != "Todas":
        filtrado = filtrado[
            filtrado["farmacia"].astype(str) == farmacia
        ]

    # Filtro por nome do medicamento
    busca = st.text_input(
        "Buscar medicamento",
        placeholder="Digite o nome do medicamento...",
        key=f"medicamento_{chave}"
    )

    if busca:
        filtrado = filtrado[
            filtrado["medicamento"].astype(str).str.contains(
                busca,
                case=False,
                na=False
            )
        ]

    # Indicadores e tabela
    st.metric("Registros encontrados", len(filtrado))
    st.dataframe(filtrado, use_container_width=True)

    # 3. Seleção de um medicamento para consultar os lotes
    if filtrado.empty:
        st.warning("Nenhum registro corresponde aos filtros.")
        return

    opcoes = filtrado.index.tolist()

    selecionado = st.selectbox(
        "Selecione um registro para ver os lotes",
        opcoes,
        format_func=lambda indice: (
            f"{filtrado.loc[indice, 'medicamento']} | "
            f"{filtrado.loc[indice, 'farmacia']} | "
            f"CNES: {filtrado.loc[indice, 'codigo_farmacia']}"
        ),
        key=f"registro_{chave}"
    )

    registro = filtrado.loc[selecionado]

    # Relaciona o resumo aos lotes por farmácia e medicamento
    detalhes = df_lotes[
        (df_lotes["codigo_farmacia"].astype(str)
         == str(registro["codigo_farmacia"]))
        &
        (df_lotes["codigo_produto"].astype(str)
         == str(registro["codigo_produto"]))
    ]

    st.markdown("#### Detalhes dos lotes")
    st.dataframe(detalhes, use_container_width=True)


# 4. Abas para as duas categorias
aba_desabastecidos, aba_proximos = st.tabs([
    "Desabastecidos",
    "Próximos do desabastecimento"
])

with aba_desabastecidos:
    mostrar_estoques(
        df_desabastecido,
        df_lotes_desabastecidos,
        "Medicamentos desabastecidos",
        "desabastecido"
    )

with aba_proximos:
    mostrar_estoques(
        df_proximo,
        df_lotes_proximos,
        "Medicamentos próximos do desabastecimento",
        "proximo"
    )
