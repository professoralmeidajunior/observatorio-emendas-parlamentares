import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import plotly.express as px


st.set_page_config(
    page_title="Equipamentos de Alto Custo",
    layout="wide"
)


def sql_text(value):
    return str(value).replace("'", "''")


senha = quote_plus("SUA SENHA")

try:
    engine = create_engine(
        f"postgresql+psycopg2://observatorio_web:{senha}@localhost/observatorio_emendas"
    )

    anos = pd.read_sql(
        """
        SELECT DISTINCT ano
        FROM emendas_raw
        WHERE codigo_funcao = '10'
          AND acao ILIKE '8535%%'
        ORDER BY ano DESC
        """,
        engine
    )

except Exception:
    st.error("Não foi possível conectar ao banco de dados.")
    st.stop()


st.title("Equipamentos de Alto Custo")
st.caption(
    "Função Saúde | Ação 8535 - ESTRUTURACAO DE UNIDADES DE ATENCAO ESPECIALIZADA EM SAUDE"
)


filtros_painel = [
    "codigo_funcao = '10'",
    "acao ILIKE '8535%%'"
]

where_painel = "WHERE " + " AND ".join(filtros_painel)


localidades = pd.read_sql(
    f"""
    SELECT DISTINCT localidade_do_gasto
    FROM emendas_raw
    {where_painel}
    ORDER BY localidade_do_gasto
    """,
    engine
)

autores = pd.read_sql(
    f"""
    SELECT DISTINCT autor
    FROM emendas_raw
    {where_painel}
    ORDER BY autor
    """,
    engine
)


sql_metricas = f"""
SELECT
    COUNT(*) total_emendas,
    COALESCE(SUM(valor_empenhado), 0) total_empenhado,
    COALESCE(SUM(valor_liquidado), 0) total_liquidado,
    COALESCE(SUM(valor_pago), 0) total_pago,
    COALESCE(SUM(valor_resto_pago), 0) total_resto_pago
FROM emendas_raw
{where_painel}
"""

metricas = pd.read_sql(sql_metricas, engine)

col1, col2, col3, col4, col5 = st.columns(5)

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

col5.metric(
    "Restos Pagos",
    f"R$ {metricas.iloc[0]['total_resto_pago']:,.0f}".replace(",", ".")
)


st.subheader("Emendas")

filtro_tabela_col1, filtro_tabela_col2, filtro_tabela_col3 = st.columns(3)

ano_selecionado = filtro_tabela_col1.selectbox(
    "Ano",
    ["Todos"] + anos["ano"].astype(str).tolist(),
    key="tabela_ano"
)

localidade_selecionada = filtro_tabela_col2.selectbox(
    "Localidade",
    ["Todas"] + localidades["localidade_do_gasto"].dropna().tolist(),
    key="tabela_localidade"
)

autor_selecionado = filtro_tabela_col3.selectbox(
    "Autor",
    ["Todos"] + autores["autor"].dropna().tolist(),
    key="tabela_autor"
)

filtros_tabela = filtros_painel.copy()

if ano_selecionado != "Todos":
    filtros_tabela.append(f"ano = {ano_selecionado}")

if localidade_selecionada != "Todas":
    filtros_tabela.append(
        f"localidade_do_gasto = '{sql_text(localidade_selecionada)}'"
    )

if autor_selecionado != "Todos":
    filtros_tabela.append(
        f"autor = '{sql_text(autor_selecionado)}'"
    )

where_tabela = "WHERE " + " AND ".join(filtros_tabela)

sql_tabela = f"""
SELECT
    codigo_emenda,
    ano,
    autor,
    localidade_do_gasto,
    tipo_emenda,
    acao,
    valor_empenhado,
    valor_liquidado,
    valor_pago,
    valor_resto_pago
FROM emendas_raw
{where_tabela}
ORDER BY valor_pago DESC, valor_empenhado DESC
LIMIT 200
"""

df_tabela = pd.read_sql(sql_tabela, engine)

st.dataframe(
    df_tabela,
    width="stretch",
    hide_index=True
)

sql_tipo = f"""
SELECT
    tipo_emenda,
    SUM(valor_pago) valor
FROM emendas_raw
{where_painel}
GROUP BY tipo_emenda
ORDER BY valor DESC
"""

df_tipo = pd.read_sql(sql_tipo, engine)

st.subheader("Distribuição por Tipo de Emenda")

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


sql_cidades = f"""
SELECT
    localidade_do_gasto cidade,
    SUM(valor_pago) valor
FROM emendas_raw
{where_painel}
  AND localidade_do_gasto ~ ' - [A-Z]{{2}}$'
GROUP BY localidade_do_gasto
ORDER BY valor DESC
LIMIT 20
"""

df_cidades = pd.read_sql(sql_cidades, engine)

st.subheader("Top 20 Cidades por Valor Pago")

fig_cidades = px.bar(
    df_cidades,
    x="valor",
    y="cidade",
    orientation="h"
)

fig_cidades.update_layout(
    height=700,
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(
    fig_cidades,
    width="stretch"
)


sql_estados = f"""
WITH base AS (
    SELECT
        CASE
            WHEN localidade_do_gasto ~ ' - [A-Z]{{2}}$'
                THEN RIGHT(localidade_do_gasto, 2)
            WHEN localidade_do_gasto = 'ACRE (UF)' THEN 'AC'
            WHEN localidade_do_gasto = 'ALAGOAS (UF)' THEN 'AL'
            WHEN localidade_do_gasto = 'AMAPÁ (UF)' THEN 'AP'
            WHEN localidade_do_gasto = 'AMAZONAS (UF)' THEN 'AM'
            WHEN localidade_do_gasto = 'BAHIA (UF)' THEN 'BA'
            WHEN localidade_do_gasto = 'CEARÁ (UF)' THEN 'CE'
            WHEN localidade_do_gasto = 'DISTRITO FEDERAL (UF)' THEN 'DF'
            WHEN localidade_do_gasto = 'ESPÍRITO SANTO (UF)' THEN 'ES'
            WHEN localidade_do_gasto = 'GOIÁS (UF)' THEN 'GO'
            WHEN localidade_do_gasto = 'MARANHÃO (UF)' THEN 'MA'
            WHEN localidade_do_gasto = 'MATO GROSSO (UF)' THEN 'MT'
            WHEN localidade_do_gasto = 'MATO GROSSO DO SUL (UF)' THEN 'MS'
            WHEN localidade_do_gasto = 'MINAS GERAIS (UF)' THEN 'MG'
            WHEN localidade_do_gasto = 'PARÁ (UF)' THEN 'PA'
            WHEN localidade_do_gasto = 'PARAÍBA (UF)' THEN 'PB'
            WHEN localidade_do_gasto = 'PARANÁ (UF)' THEN 'PR'
            WHEN localidade_do_gasto = 'PERNAMBUCO (UF)' THEN 'PE'
            WHEN localidade_do_gasto = 'PIAUÍ (UF)' THEN 'PI'
            WHEN localidade_do_gasto = 'RIO DE JANEIRO (UF)' THEN 'RJ'
            WHEN localidade_do_gasto = 'RIO GRANDE DO NORTE (UF)' THEN 'RN'
            WHEN localidade_do_gasto = 'RIO GRANDE DO SUL (UF)' THEN 'RS'
            WHEN localidade_do_gasto = 'RONDÔNIA (UF)' THEN 'RO'
            WHEN localidade_do_gasto = 'RORAIMA (UF)' THEN 'RR'
            WHEN localidade_do_gasto = 'SANTA CATARINA (UF)' THEN 'SC'
            WHEN localidade_do_gasto = 'SÃO PAULO (UF)' THEN 'SP'
            WHEN localidade_do_gasto = 'SERGIPE (UF)' THEN 'SE'
            WHEN localidade_do_gasto = 'TOCANTINS (UF)' THEN 'TO'
        END estado,
        valor_pago
    FROM emendas_raw
    {where_painel}
)
SELECT
    estado,
    SUM(valor_pago) valor
FROM base
WHERE estado IS NOT NULL
GROUP BY estado
ORDER BY valor DESC
LIMIT 10
"""

df_estados = pd.read_sql(sql_estados, engine)

st.subheader("Top 10 Estados por Valor Pago")

fig_estados = px.bar(
    df_estados,
    x="valor",
    y="estado",
    orientation="h"
)

fig_estados.update_layout(
    height=500,
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(
    fig_estados,
    width="stretch"
)


st.divider()
st.header("Auditoria por Localidade")

filtro_col1, filtro_col2, filtro_col3 = st.columns(3)

ano_auditoria = filtro_col1.selectbox(
    "Ano para auditoria",
    ["Todos"] + anos["ano"].astype(str).tolist(),
    key="auditoria_ano"
)

tipo_localidade = filtro_col2.selectbox(
    "Tipo de localidade",
    ["Todas", "Cidades", "Estados (UF)", "MÚLTIPLO", "Outras/imprecisas"],
    key="auditoria_tipo_localidade"
)

min_emendas = filtro_col3.number_input(
    "Mínimo de emendas",
    min_value=1,
    value=1,
    step=1,
    key="auditoria_min_emendas"
)

valor_col1, valor_col2 = st.columns(2)

faixa_individual = valor_col1.selectbox(
    "Maior valor individual empenhado",
    [
        "Todos",
        "Acima de R$ 500 mil",
        "Acima de R$ 1 milhão",
        "Acima de R$ 2 milhões",
        "Acima de R$ 5 milhões"
    ],
    key="auditoria_faixa_individual"
)

faixa_total = valor_col2.selectbox(
    "Valor total empenhado da localidade",
    [
        "Todos",
        "Acima de R$ 1 milhão",
        "Acima de R$ 2 milhões",
        "Acima de R$ 5 milhões",
        "Acima de R$ 10 milhões"
    ],
    key="auditoria_faixa_total"
)

filtros_auditoria = filtros_painel.copy()

if ano_auditoria != "Todos":
    filtros_auditoria.append(f"ano = {ano_auditoria}")

if tipo_localidade == "Cidades":
    filtros_auditoria.append("localidade_do_gasto ~ ' - [A-Z]{2}$'")
elif tipo_localidade == "Estados (UF)":
    filtros_auditoria.append("localidade_do_gasto LIKE '%% (UF)'")
elif tipo_localidade == "MÚLTIPLO":
    filtros_auditoria.append("localidade_do_gasto = 'MÚLTIPLO'")
elif tipo_localidade == "Outras/imprecisas":
    filtros_auditoria.append("localidade_do_gasto !~ ' - [A-Z]{2}$'")
    filtros_auditoria.append("localidade_do_gasto NOT LIKE '%% (UF)'")
    filtros_auditoria.append("localidade_do_gasto <> 'MÚLTIPLO'")

where_auditoria = "WHERE " + " AND ".join(filtros_auditoria)

limites_individuais = {
    "Acima de R$ 500 mil": 500_000,
    "Acima de R$ 1 milhão": 1_000_000,
    "Acima de R$ 2 milhões": 2_000_000,
    "Acima de R$ 5 milhões": 5_000_000
}

limites_totais = {
    "Acima de R$ 1 milhão": 1_000_000,
    "Acima de R$ 2 milhões": 2_000_000,
    "Acima de R$ 5 milhões": 5_000_000,
    "Acima de R$ 10 milhões": 10_000_000
}

having_auditoria = [f"COUNT(*) >= {int(min_emendas)}"]

if faixa_individual != "Todos":
    having_auditoria.append(
        f"MAX(valor_empenhado) >= {limites_individuais[faixa_individual]}"
    )

if faixa_total != "Todos":
    having_auditoria.append(
        f"COALESCE(SUM(valor_empenhado), 0) >= {limites_totais[faixa_total]}"
    )

having_auditoria_sql = " AND ".join(having_auditoria)

sql_localidades_auditoria = f"""
SELECT
    localidade_do_gasto,
    CASE
        WHEN localidade_do_gasto ~ ' - [A-Z]{{2}}$' THEN 'Cidade'
        WHEN localidade_do_gasto LIKE '%% (UF)' THEN 'Estado (UF)'
        WHEN localidade_do_gasto = 'MÚLTIPLO' THEN 'Múltiplo'
        ELSE 'Outra/Imprecisa'
    END tipo_localidade,
    COUNT(*) qtd_emendas,
    COUNT(DISTINCT autor) qtd_autores,
    COUNT(DISTINCT ano) qtd_anos,
    COALESCE(MAX(valor_empenhado), 0) maior_empenho_individual,
    COUNT(*) FILTER (WHERE valor_empenhado >= 1000000) qtd_emendas_acima_1mi,
    COUNT(*) FILTER (WHERE valor_empenhado >= 2000000) qtd_emendas_acima_2mi,
    COUNT(*) FILTER (WHERE valor_empenhado >= 5000000) qtd_emendas_acima_5mi,
    COALESCE(SUM(valor_empenhado), 0) total_empenhado,
    COALESCE(SUM(valor_liquidado), 0) total_liquidado,
    COALESCE(SUM(valor_pago), 0) total_pago,
    COALESCE(SUM(valor_resto_pago), 0) total_resto_pago,
    STRING_AGG(DISTINCT tipo_emenda, '; ') tipos_emenda,
    STRING_AGG(DISTINCT codigo_emenda, ', ') codigos_emenda
FROM emendas_raw
{where_auditoria}
GROUP BY localidade_do_gasto
HAVING {having_auditoria_sql}
ORDER BY maior_empenho_individual DESC, qtd_emendas DESC, total_empenhado DESC
"""

df_auditoria = pd.read_sql(sql_localidades_auditoria, engine)

if df_auditoria.empty:
    st.warning("Nenhuma localidade encontrada para os filtros de auditoria.")
else:
    def sinais_de_atencao(row):
        sinais = []

        if row["qtd_emendas"] >= 3:
            sinais.append("3+ emendas na mesma localidade")
        if row["qtd_autores"] >= 3:
            sinais.append("3+ autores diferentes")
        if row["maior_empenho_individual"] >= 1_000_000:
            sinais.append("emenda individual acima de R$ 1 mi")
        if row["qtd_emendas_acima_2mi"] > 0:
            sinais.append("emenda individual acima de R$ 2 mi")
        if row["tipo_localidade"] != "Cidade":
            sinais.append("localização ampla/imprecisa")
        if row["total_pago"] > 0 and row["total_liquidado"] == 0:
            sinais.append("valor pago com liquidação zero")
        if row["total_empenhado"] > 0 and row["total_pago"] / row["total_empenhado"] < 0.1:
            sinais.append("baixa execução paga")

        return "; ".join(sinais) if sinais else "sem sinal automático"

    df_auditoria["sinais_de_atencao"] = df_auditoria.apply(
        sinais_de_atencao,
        axis=1
    )

    def pontuacao_risco(row):
        pontos = 0

        if row["qtd_emendas"] >= 5:
            pontos += 2
        elif row["qtd_emendas"] >= 3:
            pontos += 1

        if row["qtd_autores"] >= 3:
            pontos += 1

        if row["tipo_localidade"] != "Cidade":
            pontos += 1

        if row["maior_empenho_individual"] >= 5_000_000:
            pontos += 3
        elif row["maior_empenho_individual"] >= 2_000_000:
            pontos += 2
        elif row["maior_empenho_individual"] >= 1_000_000:
            pontos += 1

        if row["qtd_emendas_acima_1mi"] >= 3:
            pontos += 1

        if row["total_pago"] >= 5_000_000:
            pontos += 2
        elif row["total_pago"] >= 1_000_000:
            pontos += 1

        if row["total_pago"] > 0 and row["total_liquidado"] == 0:
            pontos += 2

        if row["total_empenhado"] > 0 and row["total_pago"] / row["total_empenhado"] < 0.1:
            pontos += 1

        return pontos

    def classificacao_risco(pontos):
        if pontos >= 5:
            return "Alto"
        if pontos >= 3:
            return "Médio"
        return "Baixo"

    df_auditoria["pontuacao_risco"] = df_auditoria.apply(
        pontuacao_risco,
        axis=1
    )
    df_auditoria["risco"] = df_auditoria["pontuacao_risco"].apply(
        classificacao_risco
    )

    colunas_auditoria = [
        "risco",
        "pontuacao_risco",
        "localidade_do_gasto",
        "tipo_localidade",
        "qtd_emendas",
        "qtd_autores",
        "qtd_anos",
        "maior_empenho_individual",
        "qtd_emendas_acima_1mi",
        "qtd_emendas_acima_2mi",
        "qtd_emendas_acima_5mi",
        "total_empenhado",
        "total_liquidado",
        "total_pago",
        "total_resto_pago",
        "sinais_de_atencao",
        "tipos_emenda",
        "codigos_emenda"
    ]
    df_auditoria = df_auditoria[colunas_auditoria]

    met_col1, met_col2, met_col3, met_col4, met_col5 = st.columns(5)

    met_col1.metric(
        "Localidades",
        f"{len(df_auditoria):,}".replace(",", ".")
    )
    met_col2.metric(
        "Emendas",
        f"{int(df_auditoria['qtd_emendas'].sum()):,}".replace(",", ".")
    )
    met_col3.metric(
        "Pago",
        f"R$ {df_auditoria['total_pago'].sum():,.0f}".replace(",", ".")
    )
    met_col4.metric(
        "Com sinais",
        f"{int((df_auditoria['sinais_de_atencao'] != 'sem sinal automático').sum()):,}".replace(",", ".")
    )
    met_col5.metric(
        "Risco alto",
        f"{int((df_auditoria['risco'] == 'Alto').sum()):,}".replace(",", ".")
    )

    st.subheader("Localidades para Análise")

    st.dataframe(
        df_auditoria,
        width="stretch",
        hide_index=True
    )

    achados = []

    for _, row in df_auditoria.iterrows():
        if row["maior_empenho_individual"] >= 1_000_000:
            achados.append({
                "risco": row["risco"],
                "localidade_do_gasto": row["localidade_do_gasto"],
                "achado_potencial": "Emenda individual compatível com equipamento de alto custo",
                "evidencia": f"Maior empenho individual: R$ {row['maior_empenho_individual']:,.0f}".replace(",", "."),
                "acao_sugerida": "Verificar objeto comprado, unidade beneficiada, contrato, nota fiscal e tombamento.",
                "codigos_emenda": row["codigos_emenda"]
            })

        if row["qtd_emendas_acima_1mi"] >= 2:
            achados.append({
                "risco": row["risco"],
                "localidade_do_gasto": row["localidade_do_gasto"],
                "achado_potencial": "Mais de uma emenda individual acima de R$ 1 mi",
                "evidencia": f"{int(row['qtd_emendas_acima_1mi'])} emendas acima de R$ 1 mi",
                "acao_sugerida": "Verificar se os objetos são distintos ou se há sobreposição de equipamentos/beneficiários.",
                "codigos_emenda": row["codigos_emenda"]
            })

        if row["qtd_emendas"] >= 5:
            achados.append({
                "risco": row["risco"],
                "localidade_do_gasto": row["localidade_do_gasto"],
                "achado_potencial": "Concentração de emendas na mesma localidade",
                "evidencia": f"{int(row['qtd_emendas'])} emendas para a localidade",
                "acao_sugerida": "Verificar se a quantidade de entregas/equipamentos é compatível com o número de emendas.",
                "codigos_emenda": row["codigos_emenda"]
            })

        if row["qtd_autores"] >= 3:
            achados.append({
                "risco": row["risco"],
                "localidade_do_gasto": row["localidade_do_gasto"],
                "achado_potencial": "Múltiplos autores destinando recursos à mesma localidade",
                "evidencia": f"{int(row['qtd_autores'])} autores diferentes",
                "acao_sugerida": "Verificar coordenação dos objetos e risco de duplicidade na destinação.",
                "codigos_emenda": row["codigos_emenda"]
            })

        if row["tipo_localidade"] != "Cidade":
            achados.append({
                "risco": row["risco"],
                "localidade_do_gasto": row["localidade_do_gasto"],
                "achado_potencial": "Localização ampla ou imprecisa",
                "evidencia": f"Tipo de localidade: {row['tipo_localidade']}",
                "acao_sugerida": "Identificar município, unidade de saúde e beneficiário final antes de planejar fiscalização em campo.",
                "codigos_emenda": row["codigos_emenda"]
            })

        if row["total_pago"] > 0 and row["total_liquidado"] == 0:
            achados.append({
                "risco": row["risco"],
                "localidade_do_gasto": row["localidade_do_gasto"],
                "achado_potencial": "Valor pago com liquidação zerada",
                "evidencia": f"Pago: R$ {row['total_pago']:,.0f}; liquidado: R$ {row['total_liquidado']:,.0f}".replace(",", "."),
                "acao_sugerida": "Conferir estágio da despesa e consistência dos registros financeiros.",
                "codigos_emenda": row["codigos_emenda"]
            })

    df_achados = pd.DataFrame(achados)

    if not df_achados.empty:
        ordem_risco = {"Alto": 0, "Médio": 1, "Baixo": 2}
        df_achados["ordem_risco"] = df_achados["risco"].map(ordem_risco)
        df_achados = (
            df_achados
            .sort_values(["ordem_risco", "localidade_do_gasto", "achado_potencial"])
            .drop(columns=["ordem_risco"])
        )

    localidade_auditoria = st.selectbox(
        "Detalhar localidade",
        df_auditoria["localidade_do_gasto"].tolist(),
        key="auditoria_localidade"
    )

    sql_detalhe_auditoria = f"""
    SELECT
        codigo_emenda,
        ano,
        autor,
        localidade_do_gasto,
        tipo_emenda,
        valor_empenhado,
        valor_liquidado,
        valor_pago,
        valor_resto_pago,
        plano_orcamentario,
        link_detalhamento
    FROM emendas_raw
    {where_auditoria}
      AND localidade_do_gasto = '{sql_text(localidade_auditoria)}'
    ORDER BY valor_pago DESC, valor_empenhado DESC
    """

    df_detalhe_auditoria = pd.read_sql(sql_detalhe_auditoria, engine)

    st.subheader("Emendas da Localidade Selecionada")

    st.dataframe(
        df_detalhe_auditoria,
        width="stretch",
        hide_index=True
    )

    st.subheader("Achados Potenciais")

    if df_achados.empty:
        st.info("Nenhum achado potencial gerado para os filtros atuais.")
    else:
        st.dataframe(
            df_achados,
            width="stretch",
            hide_index=True
        )


st.divider()
st.header("Ferramenta: Detalhar Emendas")

busca_col1, busca_col2 = st.columns([4, 1])

codigos_emenda_busca = busca_col1.text_input(
    "Códigos das emendas",
    placeholder="Ex.: 202512700001, 202513310021, 202527500001",
    key="busca_codigos_emenda"
)

detalhar_emendas = busca_col2.button(
    "Detalhar",
    key="botao_detalhar_emendas"
)

if detalhar_emendas:
    codigos = [
        codigo.strip()
        for codigo in codigos_emenda_busca.split(",")
        if codigo.strip()
    ]
    codigos = list(dict.fromkeys(codigos))

    if not codigos:
        st.warning("Digite um ou mais códigos de emenda separados por vírgula.")
    else:
        codigos_sql = ", ".join(
            f"'{sql_text(codigo)}'"
            for codigo in codigos
        )

        sql_emendas = f"""
        SELECT
            codigo_emenda,
            ano,
            tipo_emenda,
            autor,
            numero_emenda,
            localidade_do_gasto,
            codigo_funcao,
            funcao,
            codigo_subfuncao,
            subfuncao,
            programa,
            acao,
            plano_orcamentario,
            valor_empenhado,
            valor_liquidado,
            valor_pago,
            valor_resto_inscrito,
            valor_resto_cancelado,
            valor_resto_pago,
            flg_existe_cod_autor_valido,
            possui_apoiador_solicitante,
            link_detalhamento,
            data_carga
        FROM emendas_raw
        WHERE codigo_emenda IN ({codigos_sql})
        ORDER BY ano DESC, codigo_emenda
        """

        df_emendas = pd.read_sql(sql_emendas, engine)

        if df_emendas.empty:
            st.warning("Nenhuma emenda encontrada para os códigos informados.")
        else:
            encontrados = set(df_emendas["codigo_emenda"].astype(str).tolist())
            nao_encontrados = [
                codigo
                for codigo in codigos
                if codigo not in encontrados
            ]

            if nao_encontrados:
                st.warning(
                    "Códigos não encontrados: "
                    + ", ".join(nao_encontrados)
                )

            st.subheader("Detalhes das Emendas")
            st.dataframe(
                df_emendas,
                width="stretch",
                hide_index=True
            )
