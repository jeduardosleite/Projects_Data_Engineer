"""
Módulo responsável pelo carregamento dos dados meteorológicos.

Este arquivo recebe um DataFrame já transformado e realiza o carregamento na tabela project_weather_daily do PostgreSQL.

Etapas:
1) cria uma tabela temporária;
2) envia o DataFrame para a tabela temporária;
3) insere registros novos na tabela principal;
4) atualiza registros que já existem;
5) remove a tabela temporária ao final.

A combinação "cidade + data" identifica unicamente cada registro.
"""

from pathlib import Path

import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from config import RAW_DIRECTORY, RAW_FILE_PATTERN
from database import create_database_engine
from transform import (
    get_latest_raw_file,
    transform_weather_data
)

"""
Configurando os nomes da etapa Load.

Tabela: project_weather_daily
Schema: public (padrão)
Tabela temporária: weather_daily_staging
"""
logger = logging.getLogger(__name__)

TARGET_TABLE = "project_weather_daily"
TARGET_SCHEMA = "public"
STAGING_TABLE = "project_weather_daily_staging"

def validate_load_dataframe(df: pd.DataFrame) -> None:
    """
    Valida se o DataFrame pode ser carregado no banco.
    """

    logger.info(
        "Iniciando validação do DataFrame para carga. "
        "Registros recebidos: %s.",
        len(df),
    )

    if df.empty:
        logger.error(
            "O DataFrame recebido pela etapa de carga está vazio."
        )

        raise ValueError(
            "O DataFrame está vazio, não existem dados para carregar."
        )

    required_columns = [
        "cidade",
        "data",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        logger.error(
            "Colunas obrigatórias ausentes para carga: %s.",
            ", ".join(missing_columns),
        )

        raise ValueError(
            "Colunas obrigatórias ausentes no DataFrame: "
            + ", ".join(missing_columns)
        )

    if df[required_columns].isna().any().any():
        logger.error(
            "Foram encontrados valores nulos nas colunas cidade ou data."
        )

        raise ValueError(
            "As colunas cidade e data não podem conter valores nulos."
        )

    duplicated_rows = df.duplicated(
        subset=["cidade", "data"],
        keep=False,
    )

    if duplicated_rows.any():
        logger.error(
            "Foram encontrados %s registros duplicados "
            "para cidade e data.",
            int(duplicated_rows.sum()),
        )

        raise ValueError(
            "Foram encontrados registros duplicados para a combinação "
            "'cidade + data'."
        )

    logger.info(
        "Validação do DataFrame para carga concluída com sucesso."
    )

def load_staging_table(df: pd.DataFrame, engine: Engine) -> None:
    """
    Carrega o DataFrame em uma tabela temporária.
    """

    logger.info(
        "Iniciando carga da staging table %s.%s. Registros: %s.",
        TARGET_SCHEMA,
        STAGING_TABLE,
        len(df),
    )

    df.to_sql(
        name=STAGING_TABLE,
        con=engine,
        schema=TARGET_SCHEMA,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=500,
    )

    logger.info(
        "Staging table %s.%s carregada com sucesso.",
        TARGET_SCHEMA,
        STAGING_TABLE,
    )

def upsert_weather_data(engine: Engine) -> int:
    """
    Insere ou atualiza os dados da staging table na tabela principal.

    A instrução ON CONFLICT utiliza a chave única 'cidade + data'.

    - Quando o registro ainda não existe:
        realiza o INSERT.
    
    - Quando 'cidade + data' já existem:
        realiza UPDATE das demais colunas.
    
    Parâmetro:
        engine: Engine de conexão com o PostgreSQL.

    Retorno:
        Quantidade de linhas processadas pelo comando.
    """

    upsert_query = text(
        f"""
        INSERT INTO {TARGET_SCHEMA}.{TARGET_TABLE} (
            cidade,
            data,
            temperatura_max,
            temperatura_min,
            temperatura_media,
            sensacao_termica_max,
            sensacao_termica_min,
            sensacao_termica_media,
            umidade,
            precipitacao,
            probabilidade_precipitacao,
            cobertura_precipitacao,
            velocidade_vento,
            direcao_vento,
            pressao,
            cobertura_nuvem,
            visibilidade,
            nascer_sol,
            por_sol,
            condicoes,
            descricao,
            data_carga
        )
        SELECT
            cidade,
            data,
            temperatura_max,
            temperatura_min,
            temperatura_media,
            sensacao_termica_max,
            sensacao_termica_min,
            sensacao_termica_media,
            umidade,
            precipitacao,
            probabilidade_precipitacao,
            cobertura_precipitacao,
            velocidade_vento,
            direcao_vento,
            pressao,
            cobertura_nuvem,
            visibilidade,
            nascer_sol,
            por_sol,
            condicoes,
            descricao,
            data_carga
        FROM {TARGET_SCHEMA}.{STAGING_TABLE}

        ON CONFLICT (cidade, data)
        
        DO UPDATE SET
            temperatura_max = EXCLUDED.temperatura_max,
            temperatura_min = EXCLUDED.temperatura_min,
            temperatura_media = EXCLUDED.temperatura_media,
            sensacao_termica_max = EXCLUDED.sensacao_termica_max,
            sensacao_termica_min = EXCLUDED.sensacao_termica_min,
            sensacao_termica_media = EXCLUDED.sensacao_termica_media,
            umidade = EXCLUDED.umidade,
            precipitacao = EXCLUDED.precipitacao,
            probabilidade_precipitacao = EXCLUDED.probabilidade_precipitacao,
            cobertura_precipitacao = EXCLUDED.cobertura_precipitacao,
            velocidade_vento = EXCLUDED.velocidade_vento,
            direcao_vento = EXCLUDED.direcao_vento,
            pressao = EXCLUDED.pressao,
            cobertura_nuvem = EXCLUDED.cobertura_nuvem,
            visibilidade = EXCLUDED.visibilidade,
            nascer_sol = EXCLUDED.nascer_sol,
            por_sol = EXCLUDED.por_sol,
            condicoes = EXCLUDED.condicoes,
            descricao = EXCLUDED.descricao,
            data_carga = EXCLUDED.data_carga;
        """
    )

    logger.info(
        "Iniciando upsert da tabela %s.%s para %s.%s.",
        TARGET_SCHEMA,
        STAGING_TABLE,
        TARGET_SCHEMA,
        TARGET_TABLE,
    )

    with engine.begin() as connection:
        result = connection.execute(upsert_query)

    logger.info(
        "Upsert concluído. Registros processados: %s.",
        result.rowcount,
    )

    return result.rowcount

def drop_staging_table(engine: Engine) -> None:
    """
    Remove a tabela temporária após o carregamento.
    """

    logger.info(
        "Iniciando remoção da staging table %s.%s.",
        TARGET_SCHEMA,
        STAGING_TABLE,
    )

    drop_query = text(
        f"""
        DROP TABLE IF EXISTS
        {TARGET_SCHEMA}.{STAGING_TABLE};
        """
    )

    with engine.begin() as connection:
        connection.execute(drop_query)

    logger.info(
        "Staging table %s.%s removida com sucesso.",
        TARGET_SCHEMA,
        STAGING_TABLE,
    )

def load_weather_data(df: pd.DataFrame) -> int:
    """
    Executa todo o processo de carregamento.

    Etapas:
    1) Valida o DataFrame;
    2) Cria o Engine;
    3) Carrega a staging table;
    4) Executa o upsert;
    5) Remove a staging table;
    6) Fecha os recursos do Engine.

    Parâmetro
        df: DataFrame já transformado.

    Retorno
        Quantidade de registros processados.
    """
    logger.info(
        "Iniciando etapa de carga no PostgreSQL. Registros: %s.",
        len(df),
    )

    validate_load_dataframe(df)

    logger.info("Criando Engine de conexão com o PostgreSQL.")

    engine = create_database_engine()

    try:
        load_staging_table(
            df=df,
            engine=engine
        )

        processed_rows = upsert_weather_data(engine)

        drop_staging_table(engine)

        logger.info(
            "Carga realizada com sucesso. "
            "Registros processados: %s.",
            processed_rows,
        )

        return processed_rows

    except SQLAlchemyError:
        logger.exception(
            "Erro SQLAlchemy durante o carregamento "
            "dos dados no PostgreSQL."
        )

        raise RuntimeError(
            "Erro ao carregar os dados no PostgreSQL."
        )

    except Exception:
        logger.exception(
            "Erro inesperado durante a etapa de carga."
        )
        raise

    finally:
        # Libera conexões mantidas pelo Engine.
        engine.dispose()

        logger.info(
            "Recursos e conexões do Engine foram liberados."
        )

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
        file_pattern=RAW_FILE_PATTERN
    )

    logger.info(
        "Arquivo RAW utilizado na carga: %s.",
        latest_raw_file,
    )

    raw_df = pd.read_csv(latest_raw_file)

    transformed_df = transform_weather_data(raw_df)

    processed_rows = load_weather_data(transformed_df)

    logger.info(
        "Execução isolada do load.py concluída. "
        "Registros processados: %s.",
        processed_rows,
    )