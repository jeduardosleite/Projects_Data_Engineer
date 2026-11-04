from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from .extract import extract_weather
from .transform import transform_weather
from .load import load_weather

from Data.database import create_connection, create_table

load_dotenv()

def generate_dates(year):
    """
    Gera todas as datas de um determinado ano no formato YYYY-MM-DD.
    Usa generator para evitar carregar tudo na memória.
    """
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)

    current = start
    while current <= end:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)


def run_pipeline(year):
    """
    Executa o pipeline ETL completo para o ano informado.
    """

    # Busca API Key da variável de ambiente
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente WEATHER_API_KEY não foi definida.")

    conn = create_connection()
    create_table(conn)

    success_count = 0
    error_count = 0

    try:
        for date in generate_dates(year):
            try:
                raw = extract_weather(api_key, date)
                transformed = transform_weather(raw)
                load_weather(conn, transformed)

                success_count += 1
                print(f"[OK] {date} inserido")

            except Exception as e:
                error_count += 1
                print(f"[ERRO] {date}: {e}")

        # 💾 Commit único após todas as inserções
        conn.commit()

    except Exception as critical_error:
        # ❌ Se algo muito grave acontecer, desfaz alterações
        conn.rollback()
        print(f"[ERRO CRÍTICO] {critical_error}")

    finally:
        conn.close()

    print("\n===== RESUMO =====")
    print(f"Sucessos: {success_count}")
    print(f"Erros: {error_count}")


if __name__ == "__main__":
    run_pipeline(2025)