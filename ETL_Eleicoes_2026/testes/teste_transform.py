from extract import extrair_municipios, extrair_resultado_municipal
from transform import transformar_eleicoes
from load import validate_load_dataframe

def main():

    # Escolher o estado para testar o transform.py
    estado = "SC"

    municipios = extrair_municipios(estado)

    resultados = []

    # Testa dez municípios nos dois turnos.
    for turno in [1, 2]:

        for municipio in municipios[:10]:

            dados = extrair_resultado_municipal(
                estado=estado,
                codigo_tse=municipio["Codigo_TSE"],
                turno=turno
            )

            resultados.append({
                "UF": estado,
                "Municipio": municipio["Municipio"],
                "Codigo_TSE": municipio["Codigo_TSE"],
                "Codigo_IBGE": municipio["Codigo_IBGE"],
                "Turno": turno,
                "Dados": dados
            })

    # Executa a transformação.
    df = transformar_eleicoes(resultados)

    print("\nQuantidade de registros:", len(df))

    print("\nTipo das colunas:")
    print(df.dtypes)

    df.to_csv("/home/jose/repos/personal/Pesquisa Eleitoral/testes/teste_transform.csv",
              index=False)

    df = transformar_eleicoes(resultados)

    validate_load_dataframe(df)

    print("\nDataFrame aprovado para carregamento! Estrutura do DataFrame está compatível com as 24 colunas esperadas pelo load.py.")

if __name__ == "__main__":
    main()