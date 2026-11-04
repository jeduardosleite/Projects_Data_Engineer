# Biblioteca para acessar variáveis de ambiente (.env)
import os

# Manipulação de datas
from datetime import datetime, timedelta

# Facilita trabalhar com diretórios e arquivos
from pathlib import Path

# Biblioteca para leitura e manipulação de dados
import pandas as pd

# Carrega automaticamente as variáveis do arquivo .env
from dotenv import load_dotenv

# Importa as configurações do pipeline
from config import (
    BASE_URL,
    CIDADES,
    DATA_FIM,
    DATA_INICIO,
    RAW_DIRECTORY,
)

# Importa pacote para incluir infos durante o processo.
import logging

####################################################################################

logger = logging.getLogger(__name__)

# Carrega as variáveis do arquivo .env.
load_dotenv()

# Obtém a chave da Visual Crossing.
API_KEY = os.getenv("VC_API_KEY")


def build_url(
    cidade: str,
    data_inicio: str,
    data_fim: str,
    api_key: str,
) -> str:
    """
    Monta a URL de consulta da Visual Crossing.
    """

    return (
        f"{BASE_URL}/{cidade}/{data_inicio}/{data_fim}"
        f"?unitGroup=metric"
        f"&include=days"
        f"&key={api_key}"
        f"&contentType=csv"
    )

def extract_weather_data() -> pd.DataFrame:
    """
    Extrai os dados meteorológicos de todas as cidades configuradas.

    Retorno:
        DataFrame contendo os dados de todas as cidades.
    """

    logger.info("Iniciando a extração dos dados meteorológicos.")

    if not API_KEY:
        logger.error(
            "API key não encontrada na variável de ambiente VC_API_KEY."
        )

        raise ValueError(
            "API key não encontrada. "
            "Verifique VC_API_KEY no arquivo .env."
        )

    logger.info(
        "API key localizada. Quantidade de cidades configuradas: %s.",
        len(CIDADES),
    )

    # Lista que armazenará um DataFrame para cada cidade.
    city_dataframes = []

    # Percorre todas as cidades definidas no config.py.
    for cidade in CIDADES:
        logger.info(
            "Iniciando extração dos dados da cidade: %s.",
            cidade,
        )

        url = build_url(
            cidade=cidade,
            data_inicio=DATA_INICIO,
            data_fim=DATA_FIM,
            api_key=API_KEY,
        )

        try:
            city_df = pd.read_csv(url)

            logger.info(
                "Extração concluída para %s. Registros extraídos: %s.",
                cidade,
                len(city_df),
            )

            city_dataframes.append(city_df)

        except Exception:
            logger.exception(
                "Erro durante a extração dos dados da cidade: %s.",
                cidade,
            )
            raise

    # Une os DataFrames de todas as cidades.
    final_df = pd.concat(
        city_dataframes,
        ignore_index=True,
    )

    logger.info(
        "Extração concluída para todas as cidades. "
        "Total de registros extraídos: %s.",
        len(final_df),
    )

    return final_df


def save_raw_data(df: pd.DataFrame) -> str:
    """
    Salva o DataFrame extraído na camada RAW.
    """

    logger.info(
        "Iniciando salvamento dos dados na camada RAW. Registros: %s.",
        len(df),
    )

    # Cria a pasta data/raw, caso ainda não exista.
    RAW_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info(
        "Diretório RAW verificado: %s.",
        RAW_DIRECTORY,
    )

    file_path = (
        RAW_DIRECTORY
        / f"weather_raw_{datetime.today():%Y%m%d}.csv"
    )

    try:
        df.to_csv(
            file_path,
            index=False,
        )

        logger.info(
            "Arquivo RAW salvo com sucesso em: %s.",
            file_path,
        )

        return str(file_path)

    except Exception:
        logger.exception(
            "Erro ao salvar o arquivo RAW em: %s.",
            file_path,
        )
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    df_weather = extract_weather_data()

    saved_file = save_raw_data(df_weather)

    logger.info("Arquivo salvo em: %s.", saved_file)
    logger.info(
        "Primeiros registros extraídos:\n%s",
        df_weather.head().to_string(),
    )