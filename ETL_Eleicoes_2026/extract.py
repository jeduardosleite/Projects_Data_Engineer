import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import BASE_URL, ELEICOES, REQUEST_TIMEOUT

# Configura uma sessão HTTP reutilizável
sessao = requests.Session()

retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adaptador = HTTPAdapter(max_retries=retry)

sessao.mount("https://", adaptador)


def consultar_api(url: str) -> dict:
    """
    Consulta a API do TSE com tentativas
    automáticas em caso de falhas temporárias.
    """

    resposta = sessao.get(url, timeout=REQUEST_TIMEOUT)
    resposta.raise_for_status()

    return resposta.json()


def consultar_municipios(turno: int = 1):
    """
    Consulta a configuração municipal do TSE.
    """

    if turno not in ELEICOES:
        raise ValueError("Turno inválido.")

    eleicao = ELEICOES[turno]

    url = (
        f"{BASE_URL}/{eleicao}/config/"
        f"mun-e{eleicao:06d}-cm.json"
    )

    print(f"Consultando configuração: {url}")

    return consultar_api(url)

def extrair_municipios(estado: str, turno: int = 1):
    """
    Extrai os municípios de uma UF a partir do arquivo de configuração do TSE.
    """

    estado = estado.lower().strip()

    # Consulta a configuração municipal
    dados = consultar_municipios(turno)

    # Percorre os estados disponíveis
    for uf in dados.get("abr", []):

        if uf.get("cd") == estado:

            municipios = []

            for municipio in uf.get("mu", []):

                municipios.append({
                    "UF": estado.upper(),
                    "Codigo_TSE": municipio["cd"],
                    "Codigo_IBGE": municipio["cdi"],
                    "Municipio": municipio["nm"],
                    "Capital": municipio.get("c") == "s",
                    "Zonas": municipio.get("z", [])
                })

            return municipios

    raise ValueError(
        f"Estado {estado.upper()} não encontrado."
    )


def extrair_resultado_municipal(
    estado: str,
    codigo_tse: str,
    turno: int
):
    """
    Consulta o resultado da eleição presidencial
    de um município em um turno específico.
    """

    if turno not in ELEICOES:
        raise ValueError("Turno deve ser 1 ou 2.")

    estado = estado.lower().strip()
    codigo_tse = str(codigo_tse).zfill(5)
    eleicao = ELEICOES[turno]

    url = (
        f"{BASE_URL}/{eleicao}/dados/{estado}/"
        f"{estado}{codigo_tse}-c0001-"
        f"e{eleicao:06d}-u.json"
    )

    print(f"Consultando: {url}")

    dados = consultar_api(url)

    # Verifica se a resposta pertence ao município solicitado.
    if str(dados.get("cdabr")).zfill(5) != codigo_tse:
        raise ValueError(
            f"Município retornado diferente do solicitado: {codigo_tse}"
        )

    # Verifica se o turno corresponde ao solicitado.
    if str(dados.get("t")) != str(turno):
        raise ValueError(
            f"Turno retornado diferente do solicitado: {turno}"
        )

    return dados


def extrair_eleicoes(estado: str):
    """
    Extrai os resultados municipais das eleições
    presidenciais de 2026 nos dois turnos.

    Retorna uma lista contendo os dados brutos
    e a identificação de cada município.
    """

    estado = estado.upper().strip()

    resultados = []

    for turno in [1, 2]:

        # Obtém os municípios da UF
        municipios = extrair_municipios(estado, turno)

        print(
            f"\nIniciando {turno}º turno "
            f"- {len(municipios)} municípios"
        )

        for indice, municipio in enumerate(
            municipios, start=1
        ):

            print(
                f"[{indice}/{len(municipios)}] "
                f"{municipio['Municipio']}"
            )

            dados = extrair_resultado_municipal(
                estado=estado,
                codigo_tse=municipio["Codigo_TSE"],
                turno=turno
            )

            resultados.append({
                "UF": estado,
                "Municipio": municipio["Municipio"],
                "Codigo_TSE": municipio["Codigo_TSE"],
                "Codigo_IBGE": municipio["Codigo_IBGE"],
                "Turno": turno,
                "Dados": dados
            })

    return resultados


if __name__ == "__main__":

    # Solicita o estado ao usuário
    estado = input("Informe a UF: ").upper().strip()

    # Executa a extração dos dois turnos
    resultados = extrair_eleicoes(estado)

    # Valida os resultados
    municipios = {
        registro["Codigo_TSE"]
        for registro in resultados
    }

    combinacoes = {
        (registro["Codigo_TSE"], registro["Turno"])
        for registro in resultados
    }

    print("\nExtração concluída!")
    print(f"Estado: {estado}")
    print(f"Municípios distintos: {len(municipios)}")
    print(f"Combinações município/turno: {len(combinacoes)}")
    print(f"Total de registros extraídos: {len(resultados)}")