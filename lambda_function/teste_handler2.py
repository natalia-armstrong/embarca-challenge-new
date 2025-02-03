import json
from handler_lambda2 import main  # Supondo que sua função principal no handler_2 seja "main"

def test_handler2():
    # Dados de entrada para a função
    event = {
        "csv_url": "s3://step-functions-challenge-dev-bucket/csv_files/Via Araucaria_20250203102246.csv",  # Exemplo de arquivo no S3
        "file_name": "csv_files/Via Araucaria_20250203102246.csv",
        "original_link": "https://dados.antt.gov.br/dataset/ef0171a8-f0df-4817-a4ed-b4ff94d87194/resource/aa60ce3a-033a-4864-81dc-ae32bea866e5/download/demostrativo_acidentes_viaaraucaria.csv"
    }
    context = {}  # Contexto vazio para testar, se necessário

    # Chama a função principal do handler_2
    result = main(event, context)

    # Exibe o resultado
    print("Resultado do teste:", json.dumps(result, indent=2))

# Chama a função de teste
test_handler2()