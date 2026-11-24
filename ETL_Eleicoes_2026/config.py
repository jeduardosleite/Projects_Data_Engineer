
"""
Configurações gerais do pipeline eleitoral.

Centraliza:
- URL da API do TSE;
- códigos das eleições por turno;
- configurações de requisição;
- nomes das tabelas do PostgreSQL.
"""

from pathlib import Path


# Diretório raiz do projeto.
# Como config.py ficará na raiz, usamos apenas .parent.
PROJECT_ROOT = Path(__file__).resolve().parent


# URL base da API de resultados do TSE.
BASE_URL = "https://resultados.tse.jus.br/oficial/ele2026"


# Identificadores dos dois turnos.
ELEICOES = {
    1: 6257,
    2: 6258
}


# Tempo máximo de espera de uma requisição HTTP.
REQUEST_TIMEOUT = 30


# Configurações do PostgreSQL.
TARGET_SCHEMA = "public"

TABLE_VOTACAO = "eleicoes_2026_votacao"

TABLE_TOTALIZACAO = "eleicoes_2026_totalizacao"
