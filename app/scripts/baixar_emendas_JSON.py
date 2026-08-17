import requests
import json
import time
from pathlib import Path

# =========================================================
# CONFIGURAÇÕES
# =========================================================

ANO_INICIO = 2021
ANO_FIM = 2025

TAMANHO_PAGINA = 100

URL_BASE = "https://portaldatransparencia.gov.br"

ENDPOINT = "/emendas/consulta/resultado"

# =========================================================
# PASTA DE SAÍDA
# =========================================================

PASTA_BRUTO = Path("/opt/observatorio/dados/bruto")

PASTA_BRUTO.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# CABEÇALHOS HTTP
# =========================================================

HEADERS = {

    "User-Agent":
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/136.0 Safari/537.36"
        ),

    "Referer":
        (
            "https://portaldatransparencia.gov.br/"
            "emendas/consulta"
        ),

    "X-Requested-With":
        "XMLHttpRequest",

    "Accept":
        "application/json, text/javascript, */*; q=0.01",

    "Accept-Language":
        "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}

# =========================================================
# SESSÃO
# =========================================================

session = requests.Session()

session.get(
    "https://portaldatransparencia.gov.br/emendas/consulta",
    headers=HEADERS,
    timeout=60
)

# =========================================================
# CONSULTA UMA PÁGINA
# =========================================================

def buscar_pagina(ano, pagina):

    offset = (
        (pagina - 1)
        * TAMANHO_PAGINA
    )

    payload = {

        "paginacaoSimples": "true",

        "tamanhoPagina":
            TAMANHO_PAGINA,

        "offset":
            offset,

        "direcaoOrdenacao":
            "asc",

        "colunaOrdenacao":
            "acao",

        "de":
            ano,

        "ate":
            ano,

        "colunasSelecionadas":
            (
                "linkDetalhamento,"
                "ano,"
                "tipoEmenda,"
                "autor,"
                "numeroEmenda,"
                "possuiApoiadorSolicitante,"
                "localidadeDoGasto,"
                "codigoFuncao,"
                "funcao,"
                "codigoSubfuncao,"
                "subfuncao,"
                "programa,"
                "acao,"
                "planoOrcamentario,"
                "codigoEmenda,"
                "valorEmpenhado,"
                "valorLiquidado,"
                "valorPago,"
                "valorRestoInscrito,"
                "valorRestoCancelado,"
                "valorRestoPago,"
                "flgExisteCodAutorValido,"
                "skTipoEmenda"
            ),

        "_":
            int(time.time() * 1000)
    }

    response = session.get(
        URL_BASE + ENDPOINT,
        headers=HEADERS,
        params=payload,
        timeout=60
    )

    print(
        f"Ano {ano} | Página {pagina} "
        f"| Status {response.status_code}"
    )

    response.raise_for_status()

    dados = response.json()

    return dados.get("data", [])

# =========================================================
# SALVA JSON
# =========================================================

def salvar_json(ano, registros):

    arquivo = (
        PASTA_BRUTO /
        f"emendas_{ano}.json"
    )

    with open(
        arquivo,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            registros,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Arquivo salvo: {arquivo}"
    )

# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    for ano in range(
        ANO_INICIO,
        ANO_FIM + 1
    ):

        print("\n" + "=" * 60)

        print(
            f"Extraindo ano {ano}"
        )

        print("=" * 60)

        registros = []

        pagina = 1

        while True:

            dados = buscar_pagina(
                ano,
                pagina
            )

            if not dados:
                break

            registros.extend(
                dados
            )

            print(
                f"Total acumulado: "
                f"{len(registros)}"
            )

            pagina += 1

            time.sleep(1)

        salvar_json(
            ano,
            registros
        )

    print(
        "\nExtração concluída."
    )

