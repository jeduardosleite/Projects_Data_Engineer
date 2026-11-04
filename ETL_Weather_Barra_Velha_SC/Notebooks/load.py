def load_weather(conn, data):
    """
    Função responsável por inserir no banco os dados já transformados na etapa anterior.

    Parâmetros:
    - conn: objeto de conexão ativo com o SQLite
    - data: dicionário estruturado vindo do transform_weather()
    """

    # Inserindo os dados no banco de dados.
    conn.execute("""
        INSERT OR IGNORE INTO weather_data (             
            date, year, month, day,
            avg_temp, max_temp, min_temp,
            humidity, precipitation
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["date"],           # Data completa (ex: "2025-02-17")
        data["year"],           # Ano extraído da data
        data["month"],          # Mês extraído da data
        data["day"],            # Dia extraído da data
        data["avg_temp"],       # Temperatura média do dia
        data["max_temp"],       # Temperatura máxima
        data["min_temp"],       # Temperatura mínima
        data["humidity"],       # Umidade média
        data["precipitation"]   # Precipitação total em mm
    ))