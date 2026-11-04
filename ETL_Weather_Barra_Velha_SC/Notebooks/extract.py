# Biblioteca usada para fazer requisições HTTP
import requests

# Esse endpoint retorna dados históricos de clima
BASE_URL = "http://api.weatherapi.com/v1/history.json"

def extract_weather(api_key, date):
    """
    Função responsável por extrair dados climáticos da API.

    Parâmetros:
    - api_key: chave de autenticação da API
    - date: data no formato 'YYYY-MM-DD'

    Retorna:
    - Resposta da API em formato JSON (dicionário Python)
    """
    try:
        params = {
            "key": api_key,        # chave de autenticação
            "q": "Barra Velha",    # Cidade consultada
            "dt": date             # data histórica
        }

        # Faz a requisição GET para a API
        response = requests.get(BASE_URL, params=params)

        # Verifica se houve erro, caso haja, gera uma exceção automaticamente.
        response.raise_for_status()

        # Converte a resposta (que vem em JSON) para dicionário Python.
        return response.json()

    # Se acontecer algum erro, aparecerá aqui.
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)
        return None