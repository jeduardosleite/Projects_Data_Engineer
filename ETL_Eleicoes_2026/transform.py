import pandas as pd

def converter_percentual(valor):
    """
    Converte percentuais do formato brasileiro para float.
    """

    if valor is None or valor == "":
        return None

    return float(str(valor).replace(",","."))

def transformar_votacao(resultados: list) -> pd.DataFrame:
    """
    Transforma os resultado municipais retornados pelo Extract em um dataframe estruturado.
    """

    registros = []

    for resultado in resultados:

        dados = resultado["Dados"]

        # Informações do município
        uf = resultado["UF"]
        municipio = resultado["Municipio"]
        codigo_tse = resultado["Codigo_TSE"]
        codigo_ibge = resultado["Codigo_IBGE"]
        turno = resultado["Turno"]

        # Indicadores de eleitorado
        eleitorado = dados["e"]
        votacao = dados["v"]

        # Percorre os cargos disponiveis
        for cargo in dados.get("carg", []):
            if cargo.get("nmn") != "Presidente":
                continue

            # Percorre agrupamentos, partidos e candidatos
            for agrupamento in cargo.get("agr", []):

                for partido in agrupamento.get("par", []):

                    for candidato in partido.get("cand", []):

                        registros.append({
                        "uf": uf,
                        "codigo_tse": codigo_tse,
                        "codigo_ibge": codigo_ibge,
                        "municipio": municipio,
                        "turno": turno,
                        "numero_candidato": candidato["n"],
                        "candidato": candidato["nmu"],
                        "partido": partido["sg"],
                        "votos": int(candidato["vap"]),
                        "percentual": converter_percentual(
                            candidato.get("pvap")
                        ),
                        "eleitorado_apto": int(eleitorado["te"]),
                        "comparecimento": int(eleitorado["c"]),
                        "abstencoes": int(eleitorado["a"]),
                        "votos_validos": int(votacao["vv"]),
                        "votos_brancos": int(votacao["vb"]),
                        "votos_nulos": int(votacao["tvn"])    
                    })
                        
    df = pd.DataFrame(registros)

    return df

def validar_resultados(df: pd.DataFrame):
    """
    Realizada validação básica de integridade dos dados transformados.
    """

    if df.empty:
        raise ValueError("O DataFrame está vazio.")

    # Verifica registros duplicados
    duplicados = df.duplicated(
        subset=[
            "codigo_tse",
            "turno",
            "numero_candidato"
        ]
    ).sum()

    if duplicados > 0:
        raise ValueError(
            f"Foram encontrados {duplicados} registros duplicados."
        )

    # Verifica percentuais inválidos.
    percentuais_invalidos = df[
        (df["percentual"] < 0)
        | (df["percentual"] > 100)
    ]

    if not percentuais_invalidos.empty:
        raise ValueError(
            "Foram encontrados percentuais fora do intervalo 0% a 100%."
        )

    # Verifica a consistência do eleitorado.
    inconsistencia = (
        df["comparecimento"] + df["abstencoes"]
        != df["eleitorado_apto"]
    )

    # Verificar votos negativos.
    if (df["votos"] < 0).any():
        raise ValueError(
            "Foram encontrados votos negativos."
        )

    if inconsistencia.any():
        raise ValueError(
            "Inconsistência entre comparecimento, abstenções e eleitorado."
        )

    print("\nValidação concluída com sucesso!")

def transformar_eleicoes(resultados: list) -> pd.DataFrame:
    """
    Executa o processo completo de transformação.

    Etapas:
    1. Transforma os JSONs em registros de candidatos;
    2. Valida os resultados;
    3. Consolida os municípios e os dois turnos;
    4. Retorna o DataFrame final.
    """

    # Transforma os dados brutos da API
    df_votacao = transformar_votacao(resultados)

    # Valida os registros de candidatos
    validar_resultados(df_votacao)

    # Consolida em uma linha por município
    df_municipios = transformar_municipios(df_votacao)

    # Verifica se a consolidação criou municípios duplicados
    if df_municipios.duplicated(
        subset=["uf", "codigo_tse"]
    ).any():
        raise ValueError(
            "Foram encontrados municípios duplicados."
        )

    print(
        f"\nTransformação concluída: "
        f"{len(df_municipios)} municípios."
    )

    return df_municipios


def transformar_municipios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consolida os resultados eleitorais em uma linha por município.

    Os dois turnos ficam em colunas diferentes.

    Exemplos:
        votos_13_t1
        votos_13_t2
        percentual_22_t1
        percentual_22_t2
    """

    # Identificadores únicos do município
    identificadores = [
        "uf",
        "codigo_tse"
    ]

    # Trabalha sobre uma cópia para preservar o DataFrame original
    df = df.copy()

    # Mantém apenas os candidatos do 13 e 22
    df = df[
        df["numero_candidato"].astype(str).isin(["13", "22"])
    ].copy()

    # Cria os nomes das colunas de votos e percentuais
    df["coluna_votos"] = (
        "votos_"
        + df["numero_candidato"].astype(str)
        + "_t"
        + df["turno"].astype(str)
    )

    df["coluna_percentual"] = (
        "percentual_"
        + df["numero_candidato"].astype(str)
        + "_t"
        + df["turno"].astype(str)
    )

    # Transforma os votos dos candidatos em colunas
    votos = df.pivot(
        index=identificadores,
        columns="coluna_votos",
        values="votos"
    )

    # Transforma os percentuais em colunas
    percentuais = df.pivot(
        index=identificadores,
        columns="coluna_percentual",
        values="percentual"
    )

    # Indicadores municipais que serão separados por turno
    indicadores = [
        "eleitorado_apto",
        "comparecimento",
        "abstencoes",
        "votos_validos",
        "votos_brancos",
        "votos_nulos"
    ]

    # Mantém apenas um registro de totalização
    # para cada município e turno
    totais_base = df.drop_duplicates(
        subset=[
            "uf",
            "codigo_tse",
            "turno"
        ]
    )

    # Transforma os indicadores em colunas por turno
    totais = totais_base.pivot(
        index=identificadores,
        columns="turno",
        values=indicadores
    )

    # Renomeia as colunas:
    # eleitorado_apto_t1, eleitorado_apto_t2 etc.
    totais.columns = [
        f"{indicador}_t{turno}"
        for indicador, turno in totais.columns
    ]

    # Recupera as informações cadastrais do município
    municipios = df.drop_duplicates(
        subset=identificadores
    )[
        [
            "uf",
            "codigo_tse",
            "codigo_ibge",
            "municipio"
        ]
    ].set_index(identificadores)

    # Consolida os dados
    resultado = pd.concat(
        [
            municipios,
            totais,
            votos,
            percentuais
        ],
        axis=1
    ).reset_index()

    # Remove o nome do eixo de colunas criado pelo pivot
    resultado.columns.name = None

    return resultado