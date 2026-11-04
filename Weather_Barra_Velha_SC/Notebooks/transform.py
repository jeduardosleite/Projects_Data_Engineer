# Biblioteca usada para converter string de data em objeto de data
from datetime import datetime

def transform_weather(data):
    """
    Função responsável por transformar os dados brutos vindo da API
    em um formato estruturado pronto para inserção no banco.
    """

    try:
        # Acessando o primeiro elemento da lista
        forecast = data["forecast"]["forecastday"][0]
        # A chave "day" contem os dados agregados do dia (temperatura, umidade, etc)
        day_data = forecast["day"]

        # Pega a data no formato string
        date_str = forecast["date"]
        # Converte string para objeto datetime. Isso permite extrair ano, mês e dia separadamente.
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        # Retorna um novo dicionário estruturado
        return {
            "date": date_str,                                 # Data completa como texto
            "year": date_obj.year,                            # Ano extraído da data
            "month": date_obj.month,                          # Mês extraído da data
            "day": date_obj.day,                              # Dia extraído da data
            "avg_temp": day_data.get("avgtemp_c"),            # Temperatura média
            "max_temp": day_data.get("maxtemp_c"),            # Temperatura máxima
            "min_temp": day_data.get("mintemp_c"),            # Temperatura mínima
            "humidity": day_data.get("avghumidity"),          # Umidade média
            "precipitation": day_data.get("totalprecip_mm")   # Precipitação total (mm)
        }

    except (KeyError, IndexError, TypeError) as e:
        print("Erro na transformação:", e)
        return None