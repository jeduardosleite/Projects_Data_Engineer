"""
Módulo responsável pela conexão com o banco PostgreSQL do Supabase.

Este arquivo centraliza:
- Leitura das credenciais do arquivo .env;
- Validação das variáveis obrigatórias;
- Criação do Engine do SQLAlchemy;
- Teste de conexão com o banco.

As demais etapas do projeto deverão importar a função create_database_engine() em vez de criar novas conexões diretamente.
"""

import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError


# Procura o arquivo .env e carrega suas variáveis
load_dotenv()

logger = logging.getLogger(__name__)

"""
Aqui acontece a leitura das credenciais:

- host = endereço do servidor PostgreSQL
- port = porta utilizada
- name = nome do banco de dados
- user = usuário utilizado para autenticação
- password = senha definida
"""

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Validação das configurações
def validate_database_config() -> None:
    """
    Verifica se todas as configurações obrigatórias do banco foram definidas no .env.

    A função não retorna valor, ou seja, é None.

    Caso alguma variável obvrigatória esteja ausente, gera uma exceção ValueError.
    """

    logger.info(
        "Validando as configurações de conexão com o banco."
    )

    required_variables = {
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
    }

    missing_variables = [
        variable_name
        for variable_name, variable_value in required_variables.items()
        if not variable_value
    ]

    if missing_variables:
        missing_names = ", ".join(missing_variables)

        logger.error(
            "Configurações obrigatórias ausentes: %s.",
            missing_names,
        )

        raise ValueError(
            "Configurações do banco não encontradas no arquivo .env: "
            f"{missing_names}"
        )

    logger.info(
        "Configurações de conexão validadas com sucesso."
    )

# Criação do engine
def create_database_engine() -> Engine:
    """
    Cria e retorna o Engine do SQLAlchemy.

    O Engine é o objeto utilizado para gerenciar as conexões entre o Python e o PostgreSQL.

    Return:
        objeto de conexão do SQLAlchemy.
    """

    logger.info(
        "Iniciando criação do Engine do SQLAlchemy."
    )

    validate_database_config()

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        query={
            "sslmode": "require"
        },
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=1800,
        echo=False,
    )

    logger.info(
        "Engine do SQLAlchemy criado com sucesso."
    )

    return engine

# Teste de conexão

def test_database_connection(engine: Engine) -> bool:
    """
    Testa se o python consegue se conectar ao PostgreSQL.

    Executa uma consulta que não altera dados e serve apenas para confirmar que a conexão está funcionando.

    Parâmetro:
        engine: Engine criado por create_database_engine().
    Retorno:
        bool: True quando a conexão tiver sucesso.
    Exceção:
        ConectionError quando ocorrer falha na conexão.
    """

    logger.info(
        "Iniciando teste de conexão com o PostgreSQL do Supabase."
    )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info(
            "Conexão com o PostgreSQL realizada com sucesso."
        )

        return True

    except SQLAlchemyError as error:
        logger.exception(
            "Falha ao conectar ao PostgreSQL do Supabase."
        )

        raise ConnectionError(
            "Não foi possível conectar ao PostgreSQL do Supabase."
            "Verifique host, porta, usuário, senha e conexão com a internet."
        ) from error
    
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
    )
    
    database_engine = create_database_engine()

    try:
        test_database_connection(database_engine)

    finally:
        database_engine.dispose()

        logger.info(
            "Recursos do Engine de teste foram liberados."
        )