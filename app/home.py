import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import plotly.express as px
import runpy
from pathlib import Path


st.set_option('client.showErrorDetails', False)

if st.query_params.get("pagina") == "equipamentos":
    pagina_equipamentos = Path(__file__).resolve().parent / "pages" / "01_Equipamentos_Alto_Custo.py"
    runpy.run_path(str(pagina_equipamentos), run_name="__main__")
    st.stop()



# =====================================================
# CONEXÃO
# =====================================================


senha = quote_plus("SUA SENHA AQUI")


st.set_page_config(
    page_title="Observatório de Emendas Parlamentares",
    layout="wide"
)

st.title("🏛️ Observatório de Emendas Parlamentares")

st.markdown(
    '<a href="/?pagina=equipamentos" target="_self">Painel de Equipamentos de Alto Custo</a>',
    unsafe_allow_html=True
)

# =====================================================
# FILTROS
# =====================================================


try:

    engine = create_engine(
        f"postgresql+psycopg2://observatorio_web:{senha}@localhost/observatorio_emendas"
    )

    anos = pd.read_sql(
        """
        SELECT DISTINCT ano
        FROM emendas_raw
        ORDER BY ano DESC
        """,
        engine
    )

except Exception:

    st.error(
        "Não foi possível conectar ao banco de dados."
    )

    st.stop()




ano_selecionado = st.sidebar.selectbox(
    "Ano",
    ["Todos"] + anos["ano"].astype(str).tolist()
)


filtros_base = []

if ano_selecionado != "Todos":
    filtros_base.append(
        f"ano = {ano_selecionado}"
    )

where_base = ""

if filtros_base:
    where_base = "WHERE " + " AND ".join(filtros_base)


# ==========================================
# FILTRO FUNCAO
# ==========================================

sql_funcoes_filtro = f"""
    SELECT DISTINCT funcao
    FROM emendas_raw
    {where_base}
    ORDER BY funcao
    """

funcoes = pd.read_sql(
    sql_funcoes_filtro,
    engine
)

funcao_selecionada = st.sidebar.selectbox(
    "Funcao",
    ["Todas"] + funcoes["funcao"].tolist()
)

# ==========================================
# FILTRO AUTOR
# ==========================================

filtros_autor_opcoes = filtros_base.copy()

if funcao_selecionada != "Todas":
    funcao_sql = funcao_selecionada.replace("'", "''")
    filtros_autor_opcoes.append(
        f"funcao = '{funcao_sql}'"
    )

where_autor_opcoes = ""

if filtros_autor_opcoes:
    where_autor_opcoes = "WHERE " + " AND ".join(filtros_autor_opcoes)

sql_autores_filtro = f"""
    SELECT DISTINCT autor
    FROM emendas_raw
    {where_autor_opcoes}
    ORDER BY autor
    """

autores = pd.read_sql(
    sql_autores_filtro,
    engine
)

autor_selecionado = st.sidebar.selectbox(
    "Autor",
    ["Todos"] + autores["autor"].tolist()
)


filtros = filtros_base.copy()

if funcao_selecionada != "Todas":
    funcao_sql = funcao_selecionada.replace("'", "''")
    filtros.append(
        f"funcao = '{funcao_sql}'"
    )

if autor_selecionado != "Todos":
    autor_sql = autor_selecionado.replace("'", "''")
    filtros.append(
        f"autor = '{autor_sql}'"
    )

where = ""

if filtros:
    where = "WHERE " + " AND ".join(filtros)



# =====================================================
# INDICADORES
# =====================================================

sql_metricas = f"""
SELECT
    COUNT(*) total_emendas,
    COALESCE(SUM(valor_empenhado), 0) total_empenhado,
    COALESCE(SUM(valor_liquidado), 0) total_liquidado,
    COALESCE(SUM(valor_pago), 0) total_pago
FROM emendas_raw
{where}
"""

metricas = pd.read_sql(sql_metricas, engine)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Emendas",
    f"{int(metricas.iloc[0]['total_emendas']):,}".replace(",", ".")
)

col2.metric(
    "Empenhado",
    f"R$ {metricas.iloc[0]['total_empenhado']:,.0f}".replace(",", ".")
)

col3.metric(
    "Liquidado",
    f"R$ {metricas.iloc[0]['total_liquidado']:,.0f}".replace(",", ".")
)

col4.metric(
    "Pago",
    f"R$ {metricas.iloc[0]['total_pago']:,.0f}".replace(",", ".")
)

# =====================================================
# GRÁFICO FUNÇÕES
# =====================================================

sql_funcoes = f"""
SELECT
    funcao,
    SUM(valor_pago) valor
FROM emendas_raw
{where}
GROUP BY funcao
ORDER BY valor DESC
LIMIT 15
"""

df_funcoes = pd.read_sql(sql_funcoes, engine)

st.subheader("Recursos por Função")

fig_funcoes = px.bar(
    df_funcoes,
    x="valor",
    y="funcao",
    orientation="h"
)

fig_funcoes.update_layout(
    height=600,
    yaxis={"categoryorder":"total ascending"}
)

st.plotly_chart(
    fig_funcoes,
    width="stretch"
)





# =====================================================
# TOP 20 AUTORES
# =====================================================

filtros_autores = filtros.copy()
filtros_autores.append(
    "tipo_emenda ILIKE '%%Individual%%'"
)

where_autores = "WHERE " + " AND ".join(filtros_autores)

sql_autores = f"""
SELECT
    autor,
    SUM(valor_pago) valor
FROM emendas_raw
{where_autores}
GROUP BY autor
ORDER BY valor DESC
LIMIT 20
"""

df_autores = pd.read_sql(
    sql_autores,
    engine
)

st.subheader(
    "Top 20 por Autor"
)

fig_autores = px.bar(
    df_autores,
    x="valor",
    y="autor",
    orientation="h"
)

fig_autores.update_layout(
    height=700,
    yaxis={"categoryorder":"total ascending"}
)

st.plotly_chart(
    fig_autores,
    width="stretch"
)




# =====================================================
# TOP BANCADAS
# =====================================================

filtros_bancadas = filtros.copy()
filtros_bancadas.append(
    "tipo_emenda ILIKE '%%Bancada%%'"
)

where_bancadas = "WHERE " + " AND ".join(filtros_bancadas)

sql_bancadas = f"""
SELECT
    autor,
    SUM(valor_pago) valor
FROM emendas_raw
{where_bancadas}
GROUP BY autor
ORDER BY valor DESC
LIMIT 20
"""

df_bancadas = pd.read_sql(
    sql_bancadas,
    engine
)

st.subheader(
    "Top 20 Bancadas por Valor Pago"
)

fig = px.bar(
    df_bancadas,
    x="valor",
    y="autor",
    orientation="h"
)

fig.update_layout(
    height=700,
    yaxis={"categoryorder":"total ascending"}
)

st.plotly_chart(
    fig,
    width="stretch"
)





# =====================================================
# TIPO DE EMENDA
# =====================================================

sql_tipo = f"""
SELECT
    tipo_emenda,
    SUM(valor_pago) valor
FROM emendas_raw
{where}
GROUP BY tipo_emenda
ORDER BY valor DESC
"""

df_tipo = pd.read_sql(
    sql_tipo,
    engine
)




st.subheader(
    "Distribuicao por Tipo de Emenda"
)

fig_tipo = px.pie(
    df_tipo,
    names="tipo_emenda",
    values="valor",
    hole=0.35
)

fig_tipo.update_layout(
    height=600
)

st.plotly_chart(
    fig_tipo,
    width="stretch"
)
