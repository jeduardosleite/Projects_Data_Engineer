## Autor
Graduando em Ciências de Dados, pela Uninter.

Estagiário na iSystems.

### [Linkedin](https://www.linkedin.com/in/jeduardosleite/)

---

<p align="center">
  <img src="imagem/capa.png" width="400">
</p>

<h1 align="center">Weather Pipeline com Apache Airflow</h1>

Este projeto é uma continuação do `Pipeline_Weather`, disponível neste
mesmo repositório.

[Consultar a primeira etapa do projeto](../Pipeline_Weather)

Este projeto tem como objetivo automatizar um pipeline ETL (Extract, Transform, Load) para coleta, tratamento e armazenamento de dados meteorológicos, utilizando o Apache Airflow para orquestração das tarefas.

O pipeline realiza diariamente as seguintes etapas:

- Extração de dados meteorológicos por meio da API Visual Crossing Weather;
- Transformação e padronização dos dados utilizando Pandas;
- Carregamento dos dados em um banco PostgreSQL hospedado no Supabase;
- Orquestração automática de todo o processo utilizando Apache Airflow.

O projeto foi desenvolvido com foco em boas práticas de Engenharia de Dados, incluindo modularização do código, separação das responsabilidades, utilização de variáveis de ambiente, versionamento com Git e automação do fluxo de dados.

---

# Arquitetura do Projeto

```
Pipeline_Weather_Airflow/
│
├── dags/
│   └── weather_dag.py
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

# Ferramentas e Tecnologias

## Linguagem Python

- pandas
- datetime
- pathlib
- requests
- logging
- os
- SQLAlchemy
- psycopg2-binary

## Orquestração

- Apache Airflow
- DAG
- PythonOperator

## Banco de Dados

- PostgreSQL
- Supabase

## Configuração

- python-dotenv

## API

- Visual Crossing Weather API

## Versionamento

- Git
- GitHub

## Ambiente

- Ubuntu Linux
- VS Code

---

# Como clonar o projeto

## 1. Clonar o repositório

```bash
# Faz uma cópia do repositório remoto para sua máquina.
git clone https://github.com/jeduardosleite/Projects_Data_Engineer.git
```

---

## 2. Entrar na pasta do projeto

```bash
# Acessa o diretório do projeto.
cd Projects_Data_Engineer/Pipeline_Weather_Airflow
```

---

## 3. Criar um ambiente virtual

```bash
# Cria um ambiente Python isolado para evitar conflitos entre dependências.
python3 -m venv .venv
```

---

## 4. Ativar o ambiente virtual

### Linux

```bash
# Ativa o ambiente virtual criado anteriormente.
source .venv/bin/activate
```

### Windows

```powershell
# Ativa o ambiente virtual no PowerShell.
.venv\Scripts\Activate.ps1
```

---

## 5. Instalar as dependências

```bash
# Instala todas as bibliotecas utilizadas pelo projeto.
pip install -r requirements.txt
```

---

## 6. Configurar as variáveis de ambiente

Crie um arquivo chamado:

```
.env
```

Baseando-se no arquivo:

```
.env.example
```

Configure as seguintes variáveis:

```text
VC_API_KEY=

DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

---

# Como inicializar o Apache Airflow

## 1. Definir a pasta do Airflow

```bash
# Define onde o Airflow armazenará banco de dados, DAGs, logs e configurações.
export AIRFLOW_HOME=$(pwd)/airflow
```

---

## 2. Inicializar o banco de dados

```bash
# Cria o banco interno utilizado pelo Airflow.
airflow db migrate
```

---

## 3. Criar um usuário administrador

```bash
# Cria um usuário para acessar a interface Web do Airflow.
airflow users create \
--username admin \
--firstname Jose \
--lastname Leite \
--role Admin \
--email seu@email.com
```

O comando solicitará a senha durante a execução.

---

## 4. Iniciar o Scheduler

```bash
# Responsável por identificar quando uma DAG deve ser executada.
airflow scheduler
```

Abra um novo terminal.

---

## 5. Iniciar o Webserver

```bash
# Inicia a interface Web do Airflow.
airflow webserver --port 8080
```

---

## 6. Acessar o Airflow

Abra o navegador:

```
http://localhost:8080
```

Faça login com o usuário criado anteriormente.

---

# Fluxo do Pipeline

A DAG executa diariamente o seguinte fluxo:

```
Extract
      │
      ▼
Transform
      │
      ▼
Load
```

## Extract

Responsável por:

- consumir a API Visual Crossing;
- salvar os dados brutos;
- registrar logs da extração.

---

## Transform

Responsável por:

- tratar valores nulos;
- padronizar nomes das colunas;
- remover registros duplicados;
- converter tipos de dados;
- preparar os dados para carga.

---

## Load

Responsável por:

- conectar ao PostgreSQL;
- criar tabela temporária;
- realizar UPSERT;
- atualizar registros existentes;
- inserir novos registros.

---

# Principais desafios encontrados

Durante o desenvolvimento do projeto foram encontrados diversos desafios técnicos, entre eles:

## Integração entre Airflow e projeto Python

Foi necessário estruturar o projeto de forma modular para que as DAGs pudessem importar corretamente os módulos responsáveis pela extração, transformação e carga.

---

## Organização da arquitetura

O projeto foi reorganizado seguindo uma estrutura em camadas, separando responsabilidades entre:

- configuração;
- conexão com banco;
- extração;
- transformação;
- carga;
- orquestração.

Essa abordagem facilita a manutenção e a escalabilidade do código.

---

## Upsert no PostgreSQL

A implementação da carga exigiu o desenvolvimento de uma estratégia de UPSERT utilizando SQLAlchemy e PostgreSQL, garantindo que registros existentes fossem atualizados e novos registros fossem inseridos sem duplicidade.

---

## Tratamento de dados

Foi necessário implementar regras para:

- normalização de textos;
- conversão de datas e horários;
- tratamento de valores nulos;
- eliminação de registros duplicados.

---

## Configuração do Airflow

Outro desafio foi configurar corretamente o ambiente do Apache Airflow, incluindo:

- criação do banco interno;
- configuração do scheduler;
- inicialização do webserver;
- organização das DAGs.

---

## Versionamento do projeto

Durante a publicação no GitHub foram realizadas diversas correções relacionadas ao versionamento, organização da estrutura do repositório e configuração de autenticação via SSH.

---
