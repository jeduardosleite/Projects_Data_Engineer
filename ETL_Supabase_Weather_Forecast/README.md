## Autor
Graduando em Ciências de Dados, pela Uninter.

Estagiário na iSystems.

### [Linkedin](https://www.linkedin.com/in/jeduardosleite/)

---

<p align="center">
  <img src="imagem/capa.jpg" width="400">
</p>

<h1 align="center">Weather Pipeline</h1>

Pipeline de Engenharia de Dados desenvolvido para consumir dados meteorológicos da API **Visual Crossing**, realizar o processo completo de **ETL (Extract, Transform e Load)**, armazenar os dados em um banco **PostgreSQL** hospedado no **Supabase** e disponibilizá-los para análise em ferramentas de Business Intelligence, como o **Power BI**.

---

<h1 align="center">Objetivo do Projeto</h1>

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

<h1 align="center">Ferramentas Utilizadas</h1>

- Visual Studio Code
- Ubuntu (WSL)
- Git
- GitHub
- Supabase
- PostgreSQL
- Apache Airflow *(próxima etapa)*
- Power BI *(próxima etapa)*

---

<h1 align="center">Tecnologias Utilizadas</h1>

- Python 3.12
- Pandas
- SQLAlchemy
- Psycopg2
- PostgreSQL
- Python-dotenv
- Visual Crossing Weather API

---

<h1 align="center">Arquitetura do Projeto</h1>

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

<h1 align="center">Como Executar o Projeto</h1>

Antes de executar o pipeline, é necessário configurar os serviços utilizados pelo projeto.

## Pré-requisitos

O pipeline utiliza uma API para obtenção dos dados meteorológicos e um banco de dados PostgreSQL hospedado no Supabase. Portanto, antes de iniciar a configuração do ambiente, siga estes passos:

### 1. Criar uma conta no Supabase

Acesse: https://supabase.com/

Crie um novo projeto e anote as seguintes informações, que serão utilizadas no arquivo `.env`:

- **Host**
- **Port**
- **Database**
- **User**
- **Password**

---

### 2. Criar uma conta na Visual Crossing Weather API

Acesse: https://www.visualcrossing.com/

Após criar sua conta, gere uma **API Key**, que também será utilizada no arquivo `.env`.

---

Após concluir essas configurações, siga os passos abaixo para executar o pipeline ETL.

## 1. Clonar o repositório

```bash
git clone https://github.com/jeduardosleite/Projects_Data_Engineer.git
```

---

## 2. Acessar a pasta do projeto

```bash
cd Projects_Data_Engineer/Pipeline_Weather
```

---

## 3. Criar o ambiente virtual

```bash
python3 -m venv .venv
```

---

## 4. Ativar o ambiente virtual

### Linux / Ubuntu / WSL

```bash
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

---

## 5. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## 6. Configurar as variáveis de ambiente

Crie um arquivo chamado `.env` na raiz do projeto.

```env
VC_API_KEY=SUA_CHAVE_DA_API

DB_HOST=xxxxxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=SUA_SENHA
```

---

## 7. Executar o pipeline

### Extração dos dados

Responsável por consumir a API meteorológica e salvar os dados brutos.

```bash
python3 src/extract.py
```

---

### Transformação dos dados

Realiza a limpeza, padronização e preparação dos dados para carga.

```bash
python3 src/transform.py
```

---

### Carga dos dados

Insere ou atualiza os dados processados no banco PostgreSQL (Supabase).

```bash
python3 src/load.py
```
---

## Estrutura do Pipeline

```
API Visual Crossing
        │
        ▼
extract.py
        │
        ▼
transform.py
        │
        ▼
load.py
        │
        ▼
PostgreSQL (Supabase)
```

---

## Tecnologias Utilizadas

- Python 3.12
- Pandas
- Requests
- SQLAlchemy
- PostgreSQL
- Supabase
- Python Dotenv

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

<h1 align="center">Problemas Enfrentados</h1>

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

<h1 align="center">Aprendizados</h1>

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
