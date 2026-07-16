# Weather Pipeline

Pipeline de Engenharia de Dados desenvolvido para consumir dados meteorológicos da API **Visual Crossing**, realizar o processo completo de **ETL (Extract, Transform e Load)**, armazenar os dados em um banco **PostgreSQL** hospedado no **Supabase** e disponibilizá-los para análise em ferramentas de Business Intelligence, como o **Power BI**.

---

# Objetivo do Projeto

O principal objetivo deste projeto é desenvolver um pipeline completo de Engenharia de Dados, simulando um cenário real encontrado em ambientes corporativos.

O pipeline foi construído para automatizar todo o fluxo de dados meteorológicos, desde a extração via API até o armazenamento em um Data Warehouse.

O projeto contempla:

- Extração automática de dados meteorológicos;
- Tratamento e padronização dos dados;
- Carregamento incremental no PostgreSQL;
- Organização modular do código;
- Documentação completa das etapas;
- Estrutura preparada para orquestração com Apache Airflow.

---

# Ferramentas Utilizadas

- Visual Studio Code
- Ubuntu (WSL)
- Git
- GitHub
- Supabase
- PostgreSQL
- Apache Airflow *(próxima etapa)*
- Power BI *(próxima etapa)*

---

# Tecnologias Utilizadas

- Python 3.12
- Pandas
- SQLAlchemy
- Psycopg2
- PostgreSQL
- Python-dotenv
- Visual Crossing Weather API

---

# Estrutura do Projeto

```text
weather_pipeline/
│
├── dags/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── logs/
│
├── src/
│   ├── config.py
│   ├── database.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── .env
├── requirements.txt
└── README.md
```

---

# Arquitetura do Pipeline

```text
              Visual Crossing API
                      │
                      ▼
                 Extract.py
                      │
                      ▼
           data/raw/weather_raw.csv
                      │
                      ▼
                Transform.py
                      │
                      ▼
            DataFrame Tratado
                      │
                      ▼
         project_weather_daily_staging
                      │
                 UPSERT (SQL)
                      │
                      ▼
          project_weather_daily
                      │
                      ▼
                  Power BI
```

---

# Como Executar o Projeto

## 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/weather_pipeline.git
```

---

## 2. Acessar a pasta

```bash
cd weather_pipeline
```

---

## 3. Criar o ambiente virtual

```bash
python3 -m venv .venv
```

---

## 4. Ativar o ambiente virtual

Linux / Ubuntu / WSL

```bash
source .venv/bin/activate
```

---

## 5. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## 6. Criar o arquivo `.env`

Na raiz do projeto, criar um arquivo chamado:

```text
.env
```

Exemplo:

```text
VC_API_KEY=SUA_CHAVE_DA_API

DB_HOST=xxxxxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=SUA_SENHA
```

---

## 7. Executar o pipeline

### Extração

```bash
python3 src/extract.py
```

---

### Transformação

```bash
python3 src/transform.py
```

---

### Carga

```bash
python3 src/load.py
```

---

# Etapas do Pipeline

## Extract (`extract.py`)

Responsável pela comunicação com a API Visual Crossing.

Nesta etapa o pipeline:

- monta dinamicamente a URL da API;
- consulta as cidades configuradas;
- realiza a requisição HTTP;
- converte o retorno para DataFrame;
- salva um arquivo bruto na pasta `data/raw`.

Arquivo gerado:

```text
weather_raw_YYYYMMDD.csv
```

---

## Transform (`transform.py`)

Responsável por limpar, validar e padronizar os dados recebidos.

Principais tratamentos realizados:

- validação das colunas esperadas;
- seleção das colunas relevantes;
- renomeação das colunas para português;
- conversão de datas;
- conversão de horários;
- conversão de tipos numéricos;
- tratamento de valores ausentes;
- padronização de textos;
- remoção de registros duplicados;
- inclusão da data e hora da carga.

Ao final desta etapa, o DataFrame está pronto para ser carregado no PostgreSQL.

---

## Load (`load.py`)

Responsável pelo carregamento dos dados no PostgreSQL.

Foi utilizada uma estratégia baseada em **Staging Table + UPSERT**, muito utilizada em projetos reais de Engenharia de Dados.

Fluxo:

```text
DataFrame

↓

Tabela Staging

↓

UPSERT

↓

Tabela Final
```

O processo utiliza a cláusula SQL:

```sql
ON CONFLICT
```

permitindo:

- inserir registros novos;
- atualizar registros existentes.

A chave única utilizada é:

```text
cidade + data
```

---

## Database (`database.py`)

Responsável pela criação da conexão com o PostgreSQL.

Foram utilizados:

- SQLAlchemy;
- Psycopg2.

A conexão é criada apenas quando necessária e encerrada automaticamente ao final do processo.

---

## Config (`config.py`)

Centraliza todas as configurações do projeto.

Entre elas:

- URL da API;
- cidades consultadas;
- diretórios do projeto;
- intervalo de datas;
- caminhos dos arquivos;
- padrão dos arquivos RAW.

Dessa forma, alterações futuras ficam concentradas em um único arquivo.

---

## Variáveis de Ambiente (`.env`)

Todas as informações sensíveis ficam armazenadas em um arquivo `.env`.

Exemplos:

- chave da API;
- usuário do banco;
- senha;
- host;
- porta.

Essa prática evita expor credenciais no GitHub.

---

# Problemas Enfrentados

Este foi o primeiro projeto em que desenvolvi um pipeline completo de Engenharia de Dados, desde a extração dos dados até o carregamento em um banco PostgreSQL.

Durante o desenvolvimento encontrei diversos desafios, entre eles:

- criação da arquitetura ETL;
- organização modular do projeto;
- criação da conexão com PostgreSQL utilizando SQLAlchemy;
- utilização do Supabase como Data Warehouse;
- diferenças entre tabela principal e tabela de staging;
- implementação do processo de UPSERT utilizando `ON CONFLICT`;
- tratamento de datas, horários e tipos numéricos;
- utilização de variáveis de ambiente com `.env`;
- problemas com caminhos relativos entre Windows, Ubuntu (WSL) e Python;
- limitação de requisições da API (HTTP 429);
- dificuldades iniciais na conexão com o Supabase devido ao suporte IPv6;
- diversos erros SQL relacionados à criação das tabelas, colunas e processo de carga.

Todos esses problemas contribuíram para compreender melhor o funcionamento de um pipeline de dados em um ambiente semelhante ao utilizado em projetos reais.

---

# Aprendizados

Este projeto representou um importante passo na minha formação como Engenheiro de Dados.

Durante seu desenvolvimento pude aprender sobre:

- arquitetura ETL;
- consumo de APIs REST;
- organização de projetos Python;
- modularização do código;
- boas práticas de documentação;
- tratamento de dados utilizando Pandas;
- criação de conexões com PostgreSQL;
- utilização do Supabase como Data Warehouse;
- SQLAlchemy;
- Psycopg2;
- UPSERT utilizando `ON CONFLICT`;
- criação de tabelas temporárias (Staging Tables);
- gerenciamento de variáveis de ambiente;
- controle de versões utilizando Git e GitHub;
- resolução de problemas em ambiente Linux (WSL).

Além dos conhecimentos técnicos, o projeto reforçou a importância da organização do código, documentação adequada e persistência durante a resolução de problemas.

---

# Próximos Passos

- Implementar a orquestração utilizando Apache Airflow;
- Automatizar a execução diária do pipeline;
- Criar logs estruturados para monitoramento;
- Desenvolver um dashboard no Power BI consumindo os dados diretamente do PostgreSQL;
- Expandir o pipeline para múltiplas cidades;
- Implementar testes automatizados;
- Adicionar monitoramento e tratamento de falhas.

---

# Autor

**José Eduardo de Souza Leite**

Graduando em Ciência de Dados

Estagiário em Engenharia de Dados

LinkedIn: *(adicione seu perfil)*

GitHub: *(adicione seu GitHub)*
