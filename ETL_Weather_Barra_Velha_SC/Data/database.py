import sqlite3  # permite criar e manipular bancos dce dados SQLite
import os       # manipular caaminhos de arquivos e diretórios
import sys      # Verifica qual interpretador Python está sendo usado

print("Python usado:", sys.executable)

# Pega o caminho absoluto do arquivo atual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Junta o caminho da pasta com o nome do banco de dados
db_path = os.path.join(BASE_DIR, "weather.db")

# Cria e conecta uma conexão com o banco SQLite
def create_connection():
    """Cria e retorna uma conexão com o banco SQLite."""
    conn = sqlite3.connect(db_path)
    return conn

# Cria a tabela weather_data se não existir.
def create_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        avg_temp REAL,
        max_temp REAL,
        min_temp REAL,
        humidity REAL,
        precipitation REAL
    );
    """)
    conn.commit()  # Salva as alterações feitas no banco