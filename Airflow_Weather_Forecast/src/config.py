"""
Configurações gerais do pipeline meteorológico.

Este módulo centraliza:

- cidades consultadas;
- intervalo de datas;
- URL base da API;
- caminhos das pastas;
- padrão dos arquivos RAW.
"""
import pendulum

from datetime import datetime, timedelta
from pathlib import Path

"""
Caminho absoluto da raiz do projeto.

- __file__ representa o arquivo config.py.
- parent representa a pasta src.
- parent.parent representa a raiz weather_pipeline.

"""
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Pasta onde os dados brutos serão armazenados.
RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"

# Pasta onde os dados transformados poderão ser armazenados.
PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"

# Padrão usado para localizar os arquivos RAW.
RAW_FILE_PATTERN = "weather_raw_*.csv"

# Padrão dos arquivos transformado.
PROCESSED_FILE_PATTERN = "weather_processed_*.pkl"

BASE_URL = (
    "https://weather.visualcrossing.com/"
    "VisualCrossingWebServices/rest/services/timeline"
)

# Lista de cidades
CIDADES = [
    "Florianopolis"
]

HOJE = pendulum.now("America/Sao_Paulo")

# Busca somente o dia anterior 
DATA_INICIO = (
    HOJE - timedelta(days=1)
).format("YYYY-MM-DD")

DATA_FIM = (
    HOJE + timedelta(days=7)
).format("YYYY-MM-DD")