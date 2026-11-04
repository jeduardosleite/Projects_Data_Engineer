""" 
Módulo responsável pela transformação dos dados.

Este arquivo recebe o DataFrame bruto extraído da API e aplica tratamentos antes do carregamento no banco.

- Selecionar apenas as colunas relevantes;
- Padronizar os nomes das colunas;
- Converter os tipos de dados;
- Tratar valores ausentes;
- Adicionar informações de controle da carga;
- Retornar um DataFrame pronto para o PostgreSQL.
"""

from datetime import datetime
import logging
import pandas as pd
from pathlib import Path
from config import (
    RAW_DIRECTORY,
    RAW_FILE_PATTERN,
)

logger = logging.getLogger(__name__)

# Colunas utilizadas no projeto
raw_columns = [
    'name', 
    'datetime', 
    'tempmax',
    'tempmin', 
    'temp', 
    'feelslikemax',
    'feelslikemin', 
    'feelslike',
    'dew', 
    'humidity', 
    'precip', 
    'precipprob',
    'precipcover', 
    'preciptype', 
    'snow', 
    'snowdepth', 
    'windgust',
    'windspeed', 
    'winddir', 
    'sealevelpressure', 
    'cloudcover', 
    'visibility',
    'solarradiation', 
    'solarenergy', 
    'uvindex', 
    'severerisk', 
    'sunrise',
    'sunset', 
    'moonphase', 
    'conditions', 
    'description', 
    'icon', 
    'stations'
]

# Renomeando as colunas
columns_renamed = {
    "name": "cidade",
    "datetime": "data",
    "tempmax": "temperatura_max",
    "tempmin": "temperatura_min",
    "temp": "temperatura_media",
    "feelslikemax": "sensacao_termica_max",
    "feelslikemin": "sensacao_termica_min",
    "feelslike": "sensacao_termica_media",
    "humidity": "umidade",
    "precip": "precipitacao",
    "precipprob": "probabilidade_precipitacao",
    "precipcover": "cobertura_precipitacao",
    "windspeed": "velocidade_vento",
    "winddir": "direcao_vento",
    "sealevelpressure": "pressao",
    "cloudcover": "cobertura_nuvem",
    "visibility": "visibilidade",
    "sunrise": "nascer_sol",
    "sunset": "por_sol",
    "conditions": "condicoes",
    "description": "descricao",
}

def validate_columns(df: pd.DataFrame) -> None:
    """
    Verifica se todas as colunas esperadas existem no DataFrame.
    """

    logger.info(
        "Validando as colunas do DataFrame bruto. "
        "Colunas recebidas: %s.",
        len(df.columns),
    )

    missing_columns = [
        column
        for column in raw_columns
        if column not in df.columns
    ]

    if missing_columns:
        missing_names = ", ".join(missing_columns)

        logger.error(
            "Colunas obrigatórias ausentes: %s.",
            missing_names,
        )

        raise ValueError(
            "As seguintes colunas não foram encontradas nos dados da API: "
            f"{missing_names}"
        )

    logger.info("Validação das colunas concluída com sucesso.")

# Transformação principal

def normalize_text_columns(
        df: pd.DataFrame,
        columns: list[str]
    ) -> pd.DataFrame:
    """
    Padroniza colunas textuais do DataFrame.
    """

    logger.info(
        "Iniciando padronização das colunas textuais: %s.",
        ", ".join(columns),
    )

    for column in columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .replace("", pd.NA)
        )

    logger.info("Padronização das colunas textuais concluída.")

    return df

def transform_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma os dados meteorológicos brutos.

    Etapas:
    1) Valida a existência das colunas esperadas;
    2) Cria uma cópia do DataFrame original;
    3) Seleciona apenas as colunas relevantes;
    4) Renomeia as colunas para português no formato snake_case;
    5) Converte datas, horários e valores numéricos;
    6) Trata valores ausentes;
    7) Remove registros duplicados;
    8) Adiciona a data e hora da carga;
    9) Ordena os registros por cidade e data.

    Parâmetro:
        df: DataFrame bruto retornado pela etapa Extract.
    Retorno:
        DataFrame tratado e pronto para o banco.
    """

    logger.info(
        "Iniciando transformação dos dados meteorológicos. "
        "Registros recebidos: %s.",
        len(df),
    )

    if df.empty:
        logger.error(
            "O DataFrame recebido pela transformação está vazio."
        )

        raise ValueError(
            "O Dataframe recebida está vazio, não existem dados para transformar."
        )

    validate_columns(df)

    # Cria uma cópia para não alterar o DataFrame original
    transformed_df = df.copy()

    logger.info("Cópia do DataFrame original criada.")

    # Mantém somente as colunas relevantes
    transformed_df = transformed_df[raw_columns]

    logger.info(
        "Colunas relevantes selecionadas. Total de colunas: %s.",
        len(transformed_df.columns),
    )

    # Renomeia as colunas
    transformed_df = transformed_df.rename(columns=columns_renamed)

    logger.info("Colunas renomeadas com sucesso.")

    transformed_df["data"] = pd.to_datetime(
        transformed_df["data"],
        errors="coerce"
    ).dt.date

    transformed_df["nascer_sol"] = pd.to_datetime(
        transformed_df["nascer_sol"],
        errors="coerce"
    ).dt.time

    transformed_df["por_sol"] = pd.to_datetime(
        transformed_df["por_sol"],
        errors="coerce"
    ).dt.time

    logger.info(
        "Conversão das colunas de data e horário concluída."
    )

    precipitation_columns = [
        "precipitacao",
        "probabilidade_precipitacao",
        "cobertura_precipitacao"
    ]

    descriptions = [
        "descricao",
        "condicoes"
    ]

    texts_padronization = [
        "cidade",
        "descricao",
        "condicoes"
    ]

    transformed_df[precipitation_columns] = (
        transformed_df[precipitation_columns].fillna(0)
    )

    transformed_df[descriptions] = (
        transformed_df[descriptions].fillna("Não informado")
    )

    logger.info(
        "Tratamento dos valores ausentes concluído."
    )

    rows_before_dropna = len(transformed_df)

    transformed_df = transformed_df.dropna(
        subset=["data"]
    )

    removed_null_dates = rows_before_dropna - len(transformed_df)

    logger.info(
        "Registros removidos por data inválida ou ausente: %s.",
        removed_null_dates,
    )

    transformed_df = normalize_text_columns(
        transformed_df,
        texts_padronization,
    )

    rows_before_duplicates = len(transformed_df)

    transformed_df = transformed_df.drop_duplicates(
        subset=["cidade", "data"],
        keep="last",
    )

    removed_duplicates = (
        rows_before_duplicates - len(transformed_df)
    )

    logger.info(
        "Registros duplicados removidos: %s.",
        removed_duplicates,
    )

    # Registra quando o pipeline processou os dados
    transformed_df["data_carga"] = datetime.now()

    # Ordenação e ajuste final
    transformed_df = transformed_df.sort_values(
        by=["cidade", "data"]
    ).reset_index(drop=True)

    logger.info(
        "Transformação concluída com sucesso. "
        "Registros finais: %s. Colunas finais: %s.",
        len(transformed_df),
        len(transformed_df.columns),
    )

    return transformed_df

def get_latest_raw_file(
    raw_directory: Path,
    file_pattern: str,
    ) -> Path:
        """
        Retorna o arquivo RAW mais recente da pasta informada.
        """

        logger.info(
        "Procurando arquivo RAW mais recente no diretório: %s. "
        "Padrão utilizado: %s.",
        raw_directory,
        file_pattern,
        )

        raw_files = list(
        raw_directory.glob(file_pattern)
        )

        if not raw_files:
            logger.error(
                "Nenhum arquivo RAW encontrado em: %s.",
                raw_directory,
            )

            raise FileNotFoundError(
                f"Nenhum arquivo RAW foi encontrado em: "
                f"{raw_directory}"
            )

        latest_file = max(
        raw_files,
        key=lambda file: file.stat().st_mtime,
        )

        logger.info(
        "Arquivo RAW mais recente localizado: %s.",
        latest_file,
        )

        return latest_file

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )

    latest_raw_file = get_latest_raw_file(
        raw_directory=RAW_DIRECTORY,
        file_pattern=RAW_FILE_PATTERN,
    )

    logger.info(
        "Arquivo utilizado na transformação: %s.",
        latest_raw_file,
    )

    raw_df = pd.read_csv(latest_raw_file)

    transformed_df = transform_weather_data(raw_df)

    logger.info(
        "Primeiros registros transformados:\n%s",
        transformed_df.head().to_string(),
    )

    logger.info(
        "Tipos das colunas transformadas:\n%s",
        transformed_df.dtypes.to_string(),
    )