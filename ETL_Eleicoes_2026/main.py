"""
Módulo principal do pipeline eleitoral de 2026.

Responsabilidades:

E - Extract (Extração):
    Busca os resultados eleitorais na API do TSE.

T - Transform (Transformação):
    Organiza os dados em um DataFrame do pandas.

L - Load (Carregamento):
    Envia os dados tratados para o PostgreSQL no Supabase.

O main.py funciona como um orquestrador, ele não realizada todas as operações diretamente,
mas chama funções dos outros módulos do projeto.
"""

import logging
import json

from pathlib import Path

from extract import extrair_eleicoes, extrair_municipios
from transform import transformar_eleicoes
from load import load_election_data

logger = logging.getLogger(__name__)

# Diretório raiz do projeto.
PROJECT_ROOT = Path(__file__).resolve().parent

RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"

def main():
    # Solicita o estado ao usuário.
    estado = input("Informe a UF: ").upper().strip()

    # Define o arquivo JSON correspondente ao estado.
    arquivo_raw = RAW_DIRECTORY / f"eleicoes_2026_{estado}.json"

    # Cria o diretório, caso não exista.
    RAW_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    logger.info(
        "Iniciando pipeline eleitoral para %s.",
        estado
    )

    # Extract
    # Obtém todos os municípios e os resultados dos dois turnos.
    if arquivo_raw.exists():

        logger.info(
            "Carregando dados brutos de %s.",
            arquivo_raw
        )

        with open(arquivo_raw,
                  "r",
                  encoding="utf-8"
                  ) as arquivo:
            resultados = json.load(arquivo)

    else:

        resultados = extrair_eleicoes(estado)

        with open(arquivo_raw,
                  "w",
                  encoding="utf-8"
                  ) as arquivo:
            json.dump(
                resultados,
                arquivo,
                ensure_ascii=False,
                indent=2
            )

        logger.info(
            "Dados brutos salvos em %s.",
            arquivo_raw
        )

    # Validação dos turnos
    # Obtém as combinações município/turno extraídos.
    combinacoes = {
        (str(registro["Codigo_TSE"]),
         int(registro["Turno"]))
         for registro in resultados
    }

    # Consulta a lista oficial de municípios.
    municipios = extrair_municipios(estado)

    codigos_esperados = {
    str(municipio["Codigo_TSE"])
    for municipio in municipios
    }

    # Gera todas as combinações esperadas.
    combinacoes_esperadas = {
        (codigo, turno)
        for codigo in codigos_esperados
        for turno in (1,2)
    }

    # Verifica se há municípios ou turnos ausentes.
    if (
        combinacoes != combinacoes_esperadas
        or len(resultados) != len(combinacoes_esperadas)
    ):
        raise ValueError(
            "Extração incompleta ou duplicada."
        )

    logger.info(
        "Extração validada: %s combinações município/turno.",
        len(combinacoes)
    )

    # Transform
    # Consolida os resultados em uma linha por município.
    df = transformar_eleicoes(resultados)

    quantidade_esperada = len(municipios)

    if len(df) != quantidade_esperada:
        raise ValueError(
            "Quantidade de municípios inconsistente."
            f"Esperado: {quantidade_esperada}."
            f"Obtido: {len(df)}."
        )

    # Compara os códigos TSE do Dataframe
    codigos_extraidos = set(
        df["codigo_tse"].astype(str)
    )

    if codigos_esperados != codigos_extraidos:
        raise ValueError(
            "Os códigos dos municípios extraídos não correspondem à lista oficial."
        )

    logger.info(
        "Validação concluída: %s municípios.",
        len(df)
    )

    # Load
    # Insere ou atualiza os registros no Supabase.
    registros = load_election_data(df)

    logger.info(
        "Pipeline concluído. Registros processados: %s.",
        registros
    )

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s |"
            "%(name)s | %(message)s"
        )
    )

    main()