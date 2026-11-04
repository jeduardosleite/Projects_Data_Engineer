## Vamos nos conectar:
[Linkedin](https://www.linkedin.com/in/jeduardosleite/)
---

![image](Imagem/weather.png)

# Descrição do Projeto

Este projeto tem como objetivo coletar, transformar, armazenar e analisar dados meteorológicos da cidade de Barra Velha durante o ano de 2025. Os dados incluem temperatura média, máxima e mínima, umidade relativa do ar, precipitação e amplitude térmica.

---

# Tecnologias Utilizadas

- **Python** – Automação do ETL e análise de dados
- **SQLite** – Armazenamento dos dados estruturados
- **Pandas** – Manipulação e análise de dados
- **Matplotlib / Seaborn** – Visualização de dados
- **API WeatherAPI** – Fonte de dados meteorológicos (https://www.weatherapi.com/)


# Estrutura do projeto

- **database.py**: Criação do banco e tabela SQLite
- **main.py**: Pipeline ETL completo
- **extract.py**: Função de extração da API
- **transform.py**: Transformação dos dados
- **load.py**: Carregamento no banco
- **analysis.ipynb**: Exploração de dados e gráficos
- **.env**: Armazena a chave da API
- **requirements.txt**: Dependências do projeto

---

# Pipeline ETL (Extract, Transform, Load)

## Extract
Conexão com a API WeatherAPI e coleta de dados diários de temperatura, umidade e precipitação para o ano de 2025

## Transform
Conversão das datas para ```YYYY-MM-DD```, criação de variáveis derivadas: year, month, day, amplitude (máx – mín), padronização e limpeza dos dados

## Load
Inserção dos dados no SQLite, garantia de unicidade por data, estrutura de tabela.

| Coluna        | Tipo    |
| ------------- | ------- |
| id            | INTEGER |
| date          | TEXT    |
| year          | INTEGER |
| month         | INTEGER |
| day           | INTEGER |
| avg_temp      | REAL    |
| max_temp      | REAL    |
| min_temp      | REAL    |
| humidity      | REAL    |
| precipitation | REAL    |
| amplitude     | REAL    |

---

# Insights

1) Dias mais quentes não são necessariamente mais secos
2) Precipitação tende a aumentar quando a umidade é alta
3) Amplitude térmica é maior em períodos secos
4) Pequena tendência de aquecimento ao longo do ano

---

# Aplicações práticas dos insights

- **Agricultura**: Planejamento de plantio e irrigação baseado em dias de chuva e calor.
- **Planejamento urbano**: Preparação para eventos extremos de chuva ou calor.
- **Saúde pública**: Monitoramento de dias de calor intenso ou alta umidade para prevenção de doenças.
- **Energia**: Estimativa de demanda elétrica para aquecimento/resfriamento conforme amplitude e temperatura.

---

# Conclusão

O projeto demonstra a capacidade de:
- Construir um pipeline ETL completo
- Extrair dados de uma API externa
- Transformar e limpar dados brutos
- Armazenar dados em SQLite
- Analisar tendências e relações climáticas
- Gerar insights estratégicos sobre clima e precipitação
