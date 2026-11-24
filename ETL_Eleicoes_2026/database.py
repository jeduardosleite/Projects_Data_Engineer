
"""
Módulo responsável pela conexão com o PostgreSQL
do Supabase.

Responsabilidades:
1. Carregar as variáveis do arquivo .env;
2. Validar as configurações obrigatórias;
3. Criar o Engine do SQLAlchemy;
4. Testar a conexão com o banco.
"""

import os
import logging

from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)


# Localiza o arquivo .env na raiz do projeto.
ENV_PATH = Path(__file__).resolve().parent / ".env"


def validate_database_config() -> dict:
    """
    Verifica se todas as variáveis necessárias
    para conexão estão configuradas.

    Retorna um dicionário com as credenciais.
    """

    load_dotenv(ENV_PATH)

    logger.info("Validando configurações do PostgreSQL.")

    config = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
    }

    # Identifica variáveis ausentes ou vazias.
    missing_variables = [
        name
        for name, value in config.items()
        if not value
    ]

    if missing_variables:
        raise ValueError(
            "Variáveis obrigatórias ausentes: "
            + ", ".join(missing_variables)
        )

    # Verifica se a porta é um número válido.
    try:
        port = int(config["DB_PORT"])
    except ValueError as error:
        raise ValueError(
            "DB_PORT deve ser um número inteiro."
        ) from error

    if not 1 <= port <= 65535:
        raise ValueError(
            "DB_PORT deve estar entre 1 e 65535."
        )

    config["DB_PORT"] = port

    logger.info("Configurações validadas com sucesso.")

    return config


def create_database_engine() -> Engine:
    """
    Cria o Engine do SQLAlchemy para conexão
    com o PostgreSQL do Supabase.
    """

    config = validate_database_config()

    # URL.create evita problemas com caracteres
    # especiais presentes na senha.
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        database=config["DB_NAME"],
        query={
            "sslmode": "require"
        }
    )

    # pool_pre_ping verifica se uma conexão
    # reutilizada continua ativa.
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        echo=False
    )

    logger.info("Engine criado com sucesso.")

    return engine


def test_database_connection(engine: Engine) -> bool:
    """
    Testa a conexão executando SELECT 1.

    A consulta não modifica os dados.
    """

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result.scalar_one()

        logger.info(
            "Conexão com Supabase realizada com sucesso."
        )

        return True

    except SQLAlchemyError as error:

        logger.exception(
            "Erro ao conectar ao PostgreSQL."
        )

        raise ConnectionError(
            "Não foi possível conectar ao Supabase. "
            "Verifique as credenciais e a rede."
        ) from error


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        )
    )

    engine = create_database_engine()

    try:
        test_database_connection(engine)

    finally:
        engine.dispose()

        logger.info(
            "Conexões do Engine encerradas."
        )
