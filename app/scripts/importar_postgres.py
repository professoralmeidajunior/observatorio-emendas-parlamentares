import json
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# =====================================================
# CONFIGURAÇÃO
# =====================================================

if len(sys.argv) != 2:

    print(
        "Uso: python importar_postgres.py 2025"
    )

    sys.exit(1)

ANO = sys.argv[1]

ARQUIVO_JSON = Path(
    f"/opt/observatorio/dados/bruto/emendas_{ANO}.json"
)

if not ARQUIVO_JSON.exists():

    print(
        f"Arquivo não encontrado: {ARQUIVO_JSON}"
    )

    sys.exit(1)

# =====================================================
# CONEXÃO POSTGRES
# =====================================================

engine = create_engine(
    "postgresql+psycopg2://observatorio:SUA SENHA@localhost/observatorio_emendas"
)

# =====================================================
# CONVERSÃO MONETÁRIA
# =====================================================

def moeda_para_float(valor):

    if valor is None:
        return None

    valor = str(valor)

    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    try:
        return float(valor)

    except:

        return None

# =====================================================
# LEITURA JSON
# =====================================================

print(
    f"Lendo {ARQUIVO_JSON}"
)

with open(
    ARQUIVO_JSON,
    encoding="utf-8"
) as f:

    dados = json.load(f)

df = pd.DataFrame(dados)

print(
    f"Registros encontrados: {len(df)}"
)

# =====================================================
# RENOMEIA COLUNAS
# =====================================================


df = df.rename(
    columns={
        "codigoEmenda": "codigo_emenda",
        "tipoEmenda": "tipo_emenda",
        "numeroEmenda": "numero_emenda",
        "localidadeDoGasto": "localidade_do_gasto",
        "codigoFuncao": "codigo_funcao",
        "codigoSubfuncao": "codigo_subfuncao",
        "planoOrcamentario": "plano_orcamentario",
        "valorEmpenhado": "valor_empenhado",
        "valorLiquidado": "valor_liquidado",
        "valorPago": "valor_pago",
        "valorRestoInscrito": "valor_resto_inscrito",
        "valorRestoCancelado": "valor_resto_cancelado",
        "valorRestoPago": "valor_resto_pago",
        "flgExisteCodAutorValido": "flg_existe_cod_autor_valido",
        "possuiApoiadorSolicitante": "possui_apoiador_solicitante",
        "skTipoEmenda": "sk_tipo_emenda",
        "linkDetalhamento": "link_detalhamento"
    }
)



# =====================================================
# CONVERTE VALORES MONETÁRIOS
# =====================================================

campos_monetarios = [

    "valor_empenhado",
    "valor_liquidado",
    "valor_pago",
    "valor_resto_inscrito",
    "valor_resto_cancelado",
    "valor_resto_pago"

]

for campo in campos_monetarios:

    if campo in df.columns:

        df[campo] = df[campo].apply(
            moeda_para_float
        )

# =====================================================
# REMOVE COLUNAS NÃO EXISTENTES NO BANCO
# =====================================================

colunas_banco = [

    "codigo_emenda",
    "ano",
    "tipo_emenda",
    "sk_tipo_emenda",
    "autor",
    "numero_emenda",
    "localidade_do_gasto",
    "codigo_funcao",
    "funcao",
    "codigo_subfuncao",
    "subfuncao",
    "programa",
    "acao",
    "plano_orcamentario",
    "valor_empenhado",
    "valor_liquidado",
    "valor_pago",
    "valor_resto_inscrito",
    "valor_resto_cancelado",
    "valor_resto_pago",
    "flg_existe_cod_autor_valido",
    "possui_apoiador_solicitante",
    "link_detalhamento"
]

df = df[colunas_banco]

# =====================================================
# IMPORTAÇÃO
# =====================================================

try:

    df.to_sql(
        "emendas_raw",
        engine,
        if_exists="append",
        index=False,
        chunksize=500
    )

    print(
        f"{len(df)} registros importados."
    )

except Exception as erro:

    import traceback

    print("\nERRO COMPLETO:\n")

    traceback.print_exc()
