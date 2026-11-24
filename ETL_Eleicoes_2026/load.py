
"""
Módulo responsável pelo carregamento dos resultados
eleitorais de 2026 no PostgreSQL do Supabase.

Etapas:
1. Valida o DataFrame transformado;
2. Cria uma conexão com o PostgreSQL;
3. Cria uma tabela temporária;
4. Carrega o DataFrame na tabela temporária;
5. Insere ou atualiza os municípios na tabela principal;
6. Finaliza a transação e libera os recursos.

Chave única:
    uf + codigo_tse

Granularidade:
    Uma linha por município, com os dois turnos.
"""

import logging

import pandas as pd

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from config import TARGET_SCHEMA
from database import create_database_engine


logger = logging.getLogger(__name__)

TARGET_TABLE = "eleicoes_2026_municipios"
STAGING_TABLE = "eleicoes_2026_staging"


# Colunas que deverão existir no DataFrame e no PostgreSQL.
COLUMNS = [
    "uf",
    "codigo_tse",
    "codigo_ibge",
    "municipio",

    "eleitorado_apto_t1",
    "comparecimento_t1",
    "abstencoes_t1",
    "votos_validos_t1",
    "votos_brancos_t1",
    "votos_nulos_t1",

    "eleitorado_apto_t2",
    "comparecimento_t2",
    "abstencoes_t2",
    "votos_validos_t2",
    "votos_brancos_t2",
    "votos_nulos_t2",

    "votos_13_t1",
    "percentual_13_t1",
    "votos_13_t2",
    "percentual_13_t2",

    "votos_22_t1",
    "percentual_22_t1",
    "votos_22_t2",
    "percentual_22_t2",
]

# A chave única não deve ser atualizada no UPSERT.
KEY_COLUMNS = ["uf", "codigo_tse"]

# Demais colunas poderão ser atualizadas.
UPDATE_COLUMNS = [
    column
    for column in COLUMNS
    if column not in KEY_COLUMNS
]


def validate_load_dataframe(df: pd.DataFrame) -> None:
    """
    Valida os dados antes de enviá-los ao Supabase.

    Verificações:
    - DataFrame não vazio;
    - presença das 24 colunas;
    - ausência de nulos na identificação;
    - ausência de municípios duplicados.
    """

    logger.info(
        "Validando DataFrame. Registros: %s",
        len(df)
    )

    if df.empty:
        raise ValueError(
            "O DataFrame está vazio."
        )

    # Verifica colunas obrigatórias.
    missing_columns = [
        column
        for column in COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Colunas ausentes: "
            + ", ".join(missing_columns)
        )

    # Identificação do município não pode ser nula.
    if df[KEY_COLUMNS].isna().any().any():
        raise ValueError(
            "UF e código TSE não podem ser nulos."
        )

    # Verifica se o município aparece mais de uma vez.
    duplicated = df.duplicated(
        subset=KEY_COLUMNS,
        keep=False
    )

    if duplicated.any():
        raise ValueError(
            f"Foram encontrados {duplicated.sum()} "
            "registros duplicados."
        )

    logger.info(
        "Validação do DataFrame concluída."
    )


def load_staging_table(
    df: pd.DataFrame,
    connection: Connection
) -> None:
    """
    Cria e carrega uma tabela temporária no PostgreSQL.

    Etapas:
    1. Cria a tabela temporária;
    2. Converte o DataFrame em uma lista de dicionários;
    3. Insere os registros na tabela temporária.

    A tabela será removida automaticamente
    quando a transação for finalizada.
    """

    logger.info(
        "Criando tabela temporária para %s registros.",
        len(df)
    )

    # Cria uma tabela temporária com a mesma estrutura
    # da tabela principal no Supabase.
    connection.execute(
        text(
            f"""
            CREATE TEMP TABLE {STAGING_TABLE}
            (LIKE {TARGET_SCHEMA}.{TARGET_TABLE}
             INCLUDING DEFAULTS)
            ON COMMIT DROP;
            """
        )
    )

    # Seleciona somente as 24 colunas esperadas.
    dados = df[COLUMNS].copy()

    # Converte valores ausentes do pandas (NaN, pd.NA)
    # em None, que representa NULL no PostgreSQL.
    dados = dados.astype(object).where(
        pd.notna(dados),
        None
    )

    # Converte o DataFrame em uma lista de dicionários.
    #
    # Exemplo:
    # [
    #     {"uf": "SC", "codigo_tse": "80225", ...},
    #     {"uf": "SC", "codigo_tse": "80012", ...}
    # ]
    registros = dados.to_dict(orient="records")

    # Monta a lista de colunas utilizadas no INSERT.
    colunas_sql = ", ".join(COLUMNS)

    # Cria um parâmetro para cada coluna.
    #
    # Exemplo:
    # :uf, :codigo_tse, :codigo_ibge, :municipio, ...
    parametros_sql = ", ".join(
        f":{coluna}"
        for coluna in COLUMNS
    )

    # Prepara o comando SQL de inserção.
    query = text(
        f"""
        INSERT INTO pg_temp.{STAGING_TABLE}
        ({colunas_sql})
        VALUES ({parametros_sql})
        """
    )

    # Insere todos os registros utilizando a
    # mesma conexão e transação.
    #
    # O SQLAlchemy executa a inserção em lote
    # quando recebe uma lista de dicionários.
    connection.execute(query, registros)

    logger.info(
        "Tabela temporária carregada com sucesso. "
        "Registros: %s",
        len(registros)
    )

def upsert_election_data(
    connection: Connection
) -> int:
    """
    Insere municípios novos e atualiza os existentes.

    ON CONFLICT utiliza a chave:
        uf + codigo_tse
    """

    # Lista de colunas para INSERT e SELECT.
    columns_sql = ", ".join(COLUMNS)

    # Monta os campos que serão atualizados.
    update_sql = ",\n".join(
        f"{column} = EXCLUDED.{column}"
        for column in UPDATE_COLUMNS
    )

    query = text(
        f"""
        INSERT INTO {TARGET_SCHEMA}.{TARGET_TABLE}
        ({columns_sql})

        SELECT {columns_sql}
        FROM pg_temp.{STAGING_TABLE}
        WHERE TRUE
        
        ON CONFLICT (uf, codigo_tse)

        DO UPDATE SET
            {update_sql};
        """
    )

    logger.info(
        "Iniciando UPSERT dos resultados eleitorais."
    )

    result = connection.execute(query)

    logger.info(
        "UPSERT concluído. Registros processados: %s",
        result.rowcount
    )

    return result.rowcount


def load_election_data(df: pd.DataFrame) -> int:
    """
    Executa o carregamento completo no Supabase.

    Todas as operações de banco acontecem
    dentro de uma única transação.

    Se houver erro, o PostgreSQL realiza rollback.
    """

    validate_load_dataframe(df)

    engine = create_database_engine()

    try:

        # Inicia uma transação.
        with engine.begin() as connection:

            # Cria e carrega a tabela temporária.
            load_staging_table(
                df=df,
                connection=connection
            )

            # Insere ou atualiza os registros.
            processed_rows = upsert_election_data(
                connection=connection
            )

        # A tabela temporária é removida
        # automaticamente após o COMMIT.
        logger.info(
            "Carga finalizada. Registros: %s",
            processed_rows
        )

        return processed_rows

    except SQLAlchemyError as error:

        logger.exception(
            "Erro durante o carregamento no Supabase."
        )

        raise RuntimeError(
            "Falha ao carregar resultados eleitorais."
        ) from error

    finally:

        # Libera as conexões do Engine.
        engine.dispose()

        logger.info(
            "Recursos do Engine liberados."
        )